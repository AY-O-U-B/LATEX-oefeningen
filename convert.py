"""
convert.py — Zet alle .tex bestanden in de map 'oefeningen/' om naar PDF
Gebruik: python convert.py

Vereisten:
  - MiKTeX of TeX Live geïnstalleerd (pdflatex beschikbaar)
"""

import os
import subprocess
import shutil

# Mappen
TEX_DIR = "oefeningen"
PDF_DIR = "pdfs"
TEMP_DIR = "temp_latex"

def convert_all():
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    tex_files = [f for f in os.listdir(TEX_DIR) if f.endswith(".tex")]

    if not tex_files:
        print("Geen .tex bestanden gevonden in de map 'oefeningen/'.")
        return

    print(f"▶ {len(tex_files)} bestand(en) gevonden.\n")

    success = 0
    failed = []

    for tex_file in sorted(tex_files):
        name = os.path.splitext(tex_file)[0]
        src = os.path.abspath(os.path.join(TEX_DIR, tex_file))
        out_pdf = os.path.join(PDF_DIR, f"{name}.pdf")

        print(f"  Verwerken: {tex_file} ...", end=" ", flush=True)

        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", TEMP_DIR, src],
                capture_output=True,
                text=True,
                timeout=60
            )

            temp_pdf = os.path.join(TEMP_DIR, f"{name}.pdf")
            if os.path.exists(temp_pdf):
                shutil.copy(temp_pdf, out_pdf)
                print(f"✅ OK → pdfs/{name}.pdf")
                success += 1
            else:
                print("❌ Mislukt (geen PDF aangemaakt)")
                failed.append(tex_file)

        except FileNotFoundError:
            print("\n\n❌ FOUT: pdflatex niet gevonden!")
            print("   Zorg dat MiKTeX of TeX Live geïnstalleerd is.")
            print("   Download: https://miktex.org/download")
            return
        except subprocess.TimeoutExpired:
            print("❌ Timeout (bestand duurt te lang)")
            failed.append(tex_file)

    # Opruimen tijdelijke bestanden
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    print(f"\n✅ Klaar! {success}/{len(tex_files)} bestanden omgezet.")
    if failed:
        print(f"❌ Mislukt: {', '.join(failed)}")
        print("   Controleer of deze .tex bestanden geldig zijn.")

if __name__ == "__main__":
    convert_all()
