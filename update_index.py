"""
update_index.py — Scant oefeningen-mappen en update index.html automatisch

Gebruik:
  python update_index.py

Wat het doet:
  1. Scant oefeningen/2025-2026/ en oefeningen/2024-2025/ voor .tex bestanden
  2. Controleert of er een bijhorende PDF bestaat in pdfs/<jaar>/
  3. Extraheert de studentnaam uit de bestandsnaam:
       Formaat: <reeks>-<opgave>-<voornaam>.<achternaam>.INF.tex
       Voorbeeld: 1a-4.3-michael.francken.INF.tex  →  "Michael Francken"
                  1b-14.19-luko.de.vriendt.INF.tex →  "Luko De Vriendt"
  4. Bouwt het leaderboard door per naam te tellen hoeveel bestanden ze hebben
  5. Schrijft de gegenereerde blokken terug naar index.html
"""

import os
import re
import json
from datetime import date

JAREN  = ["2025-2026", "2024-2025"]
INDEX  = "index.html"

MARKER_FILES_START = "// // AUTO-GENERATED: FILES — niet handmatig aanpassen"
MARKER_FILES_END   = "// // EINDE AUTO-GENERATED FILES"
MARKER_LB_START    = "// // AUTO-GENERATED: LEADERBOARD — niet handmatig aanpassen"
MARKER_LB_END      = "// // EINDE AUTO-GENERATED LEADERBOARD"


def extract_name(bestandsnaam: str) -> str | None:
    """
    Haal de studentnaam uit een bestandsnaam (zonder .tex extensie).

    Formaat: <reeks>-<opgave>-<naam>.INF
    Voorbeelden:
      1a-4.3-michael.francken.INF        → "Michael Francken"
      1b-14.19-luko.de.vriendt.INF       → "Luko De Vriendt"
      7e-2.2-tyas.hermans-wout.vanderborcht.INF → "Tyas Hermans-Wout Vanderborcht"
      3b-4.4-luca.letroye-mathijs.pittoors.INF  → "Luca Letroye-Mathijs Pittoors"
    """
    # Verwijder extensie .INF (case-insensitive)
    naam = re.sub(r'\.inf$', '', bestandsnaam, flags=re.IGNORECASE)

    # Patroon: reeks-opgave-naam
    m = re.match(r'^[0-9]+[a-zA-Z]-[\d.]+-(.+)', naam)
    if not m:
        return None

    naam_deel = m.group(1)  # bv. "michael.francken" of "luko.de.vriendt"

    # Punten zijn woordscheidingstekens, hoofdletters per woord
    result = ' '.join(word.capitalize() for word in naam_deel.replace('.', ' ').split())
    return result


def scan_jaar(jaar: str) -> list[dict]:
    """Scan een jaar-map en geef een gesorteerde lijst van bestandsinfo terug."""
    tex_dir = os.path.join("oefeningen", jaar)
    pdf_dir = os.path.join("pdfs", jaar)

    if not os.path.isdir(tex_dir):
        print(f"  ⚠️  '{tex_dir}' niet gevonden — overgeslagen.")
        return []

    bestanden = sorted(f for f in os.listdir(tex_dir) if f.endswith(".tex"))
    vandaag   = date.today().isoformat()
    resultaat = []

    for tex in bestanden:
        stem    = os.path.splitext(tex)[0]  # zonder .tex
        has_pdf = os.path.isfile(os.path.join(pdf_dir, stem + ".pdf"))

        resultaat.append({
            "name":    stem,
            "student": stem.lower(),
            "date":    vandaag,
            "hasPdf":  has_pdf,
        })

    return resultaat


def bouw_leaderboard(files_per_jaar: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """
    Tel per persoonsnaam hoeveel bestanden ze hebben.
    Naam wordt geëxtraheerd en geformatteerd als "Voornaam Achternaam".
    """
    lb = {}
    for jaar, bestanden in files_per_jaar.items():
        teller: dict[str, int] = {}
        for f in bestanden:
            naam = extract_name(f["name"])
            if naam:
                teller[naam] = teller.get(naam, 0) + 1
            else:
                print(f"  ⚠️  Kon naam niet extraheren uit: {f['name']}")

        # Gesorteerd alfabetisch op naam (de HTML sorteert op count)
        lb[jaar] = [{"name": n, "count": c} for n, c in sorted(teller.items())]

    return lb


def vervang_blok(inhoud: str, start_marker: str, end_marker: str, nieuw_blok: str) -> str:
    """Vervang alles tussen start_marker en end_marker (inclusief) door nieuw_blok."""
    patroon = re.compile(
        re.escape(start_marker) + r'.*?' + re.escape(end_marker),
        re.DOTALL
    )
    vervanging = f"{start_marker}\n{nieuw_blok}\n  {end_marker}"
    nieuw, n = patroon.subn(vervanging, inhoud)
    if n == 0:
        print(f"  ⚠️  Marker niet gevonden: '{start_marker}'")
    return nieuw


def main():
    if not os.path.isfile(INDEX):
        print(f"❌  '{INDEX}' niet gevonden. Zorg dat je dit script in de projectmap uitvoert.")
        return

    print("▶  update_index.py — bestanden scannen en index.html bijwerken\n")

    # 1. Scan alle jaren
    files_per_jaar: dict[str, list[dict]] = {}
    for jaar in JAREN:
        bestanden = scan_jaar(jaar)
        files_per_jaar[jaar] = bestanden
        print(f"  📂 {jaar}: {len(bestanden)} bestand(en) gevonden")

    # 2. Bouw leaderboard
    leaderboard = bouw_leaderboard(files_per_jaar)
    for jaar, lb in leaderboard.items():
        print(f"  🏆 {jaar}: {len(lb)} unieke student(en) in leaderboard")

    # 3. Genereer JSON-blokken
    files_json = json.dumps(files_per_jaar, indent=4, ensure_ascii=False)
    lb_json    = json.dumps(leaderboard,    indent=4, ensure_ascii=False)

    files_blok = f"  const FILES = {files_json};"
    lb_blok    = f"  const LEADERBOARD = {lb_json};"

    # 4. Lees index.html
    with open(INDEX, "r", encoding="utf-8") as f:
        inhoud = f.read()

    # 5. Vervang blokken
    inhoud = vervang_blok(inhoud, MARKER_FILES_START, MARKER_FILES_END, files_blok)
    inhoud = vervang_blok(inhoud, MARKER_LB_START,    MARKER_LB_END,    lb_blok)

    # 6. Schrijf terug
    with open(INDEX, "w", encoding="utf-8") as f:
        f.write(inhoud)

    print(f"\n✅  '{INDEX}' succesvol bijgewerkt!")
    print(f"   • FILES-blok:       {sum(len(v) for v in files_per_jaar.values())} bestanden")
    print(f"   • LEADERBOARD-blok: {sum(len(v) for v in leaderboard.values())} unieke namen")


if __name__ == "__main__":
    main()
