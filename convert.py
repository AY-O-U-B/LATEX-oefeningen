"""
convert.py — Zet .tex bestanden om naar PDF
Gebruik:
  python convert.py 2025-2026     → converteert alleen dat jaar
  python convert.py               → converteert BEIDE jaren

Mappenstructuur:
  oefeningen/2025-2026/*.tex  →  pdfs/2025-2026/*.pdf
  oefeningen/2024-2025/*.tex  →  pdfs/2024-2025/*.pdf
"""

import os
import subprocess
import shutil
import sys

JAREN = ["2025-2026", "2024-2025"]
TEMP  = "temp_latex"

def converteer_jaar(jaar):
    tex_dir = os.path.join("oefeningen", jaar)
    pdf_dir = os.path.join("pdfs", jaar)

    if not os.path.isdir(tex_dir):
        print(f"  ⚠️  Map '{tex_dir}' bestaat niet — overgeslagen.")
        return

    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(TEMP, exist_ok=True)

    bestanden = [f for f in os.listdir(tex_dir) if f.endswith(".tex")]
    if not bestanden:
        print(f"  Geen .tex bestanden gevonden in {tex_dir}.")
        return

    print(f"\n  📂 {jaar}  ({len(bestanden)} bestand(en))")

    ok, fout = 0, []

    for tex in sorted(bestanden):
        naam = os.path.splitext(tex)[0]
        src  = os.path.abspath(os.path.join(tex_dir, tex))
        doel = os.path.join(pdf_dir, naam + ".pdf")

        print(f"    {tex} ...", end=" ", flush=True)

        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode",
                 "-output-directory", TEMP, src],
                capture_output=True, text=True, timeout=60
            )
            tmp_pdf = os.path.join(TEMP, naam + ".pdf")
            if os.path.exists(tmp_pdf):
                shutil.copy(tmp_pdf, doel)
                print(f"✅  → pdfs/{jaar}/{naam}.pdf")
                ok += 1
            else:
                print("❌  geen PDF aangemaakt")
                fout.append(tex)

        except FileNotFoundError:
            print("\n\n❌  FOUT: pdflatex niet gevonden!")
            print("   Installeer MiKTeX via https://miktex.org/download")
            shutil.rmtree(TEMP, ignore_errors=True)
            return
        except subprocess.TimeoutExpired:
            print("❌  timeout")
            fout.append(tex)

    print(f"  ✅  {ok}/{len(bestanden)} gelukt", end="")
    if fout:
        print(f"  |  ❌ mislukt: {', '.join(fout)}", end="")
    print()


def main():
    # Welke jaren verwerken?
    if len(sys.argv) > 1:
        jaar_arg = sys.argv[1]
        if jaar_arg not in JAREN:
            print(f"❌  Onbekend jaar '{jaar_arg}'. Kies uit: {', '.join(JAREN)}")
            return
        te_doen = [jaar_arg]
    else:
        te_doen = JAREN

    print(f"▶  LaTeX → PDF converter")
    print(f"   Jaren: {', '.join(te_doen)}\n")

    for jaar in te_doen:
        converteer_jaar(jaar)

    shutil.rmtree(TEMP, ignore_errors=True)
    print("\nKlaar!")


if __name__ == "__main__":
    main()
