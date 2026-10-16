"""Turn a finished .docx or .pptx into a PDF, and optionally PNG previews.

  python render.py file.docx|file.pptx [--outdir DIR] [--png] [--dpi 60]

Uses LibreOffice (soffice). Two things it checks, because both fail silently:

* Equations. LibreOffice drops Word equations from the PDF when its Math
  module (libsmlo.so, package libreoffice-math) is missing. If the file has
  equations and the module is missing, the script stops and says so.
* Fonts. Where Times New Roman is not installed, LibreOffice uses Liberation
  Serif, which has the same letter widths, so line and page breaks match.
  The script reports which serif ended up in the PDF.

With --png it also writes one PNG per page and a contact sheet
(<name>-sheet.png) for a visual check.
"""

import argparse
import glob
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def has_equations(path):
    if path.suffix.lower() != ".docx":
        return False
    with zipfile.ZipFile(path) as z:
        return b"<m:oMath" in z.read("word/document.xml")


def math_module_present():
    for d in ("/usr/lib/libreoffice/program", "/opt/libreoffice/program", "/usr/lib64/libreoffice/program",
              "/Applications/LibreOffice.app/Contents/Frameworks"):
        if glob.glob(f"{d}/libsmlo.*"):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--outdir")
    ap.add_argument("--png", action="store_true")
    ap.add_argument("--dpi", type=int, default=60)
    a = ap.parse_args()
    src = Path(a.src).resolve()
    outdir = Path(a.outdir).resolve() if a.outdir else src.parent
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        sys.exit("LibreOffice (soffice) is not installed; cannot make the PDF.")
    if has_equations(src) and not math_module_present():
        sys.exit("This document has equations, but LibreOffice's Math module is missing, so they would vanish "
                 "from the PDF. Install it (apt-get install -y libreoffice-math) and run again.")
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(src)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = outdir / (src.stem + ".pdf")
    if not pdf.exists():
        sys.exit(f"LibreOffice did not write {pdf}")
    fonts = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout if shutil.which("pdffonts") else ""
    serif = "Times New Roman" if "TimesNewRoman" in fonts.replace(" ", "") else ("Liberation Serif (same metrics as Times New Roman)" if "LiberationSerif" in fonts else "unknown")
    print(f"wrote {pdf}  [serif in PDF: {serif}]")
    if a.png:
        from PIL import Image
        prefix = outdir / f"{src.stem}-page"
        for old in glob.glob(f"{prefix}-*.png"):
            Path(old).unlink()
        subprocess.run(["pdftoppm", "-r", str(a.dpi), "-png", str(pdf), str(prefix)], check=True)
        pages = sorted(glob.glob(f"{prefix}-*.png"))
        ims = [Image.open(p) for p in pages]
        w, h = ims[0].size
        cols = 4 if w > h else 3
        rows = -(-len(ims) // cols)
        sheet = Image.new("RGB", (w * min(cols, len(ims)), h * rows), "white")
        for i, im in enumerate(ims):
            sheet.paste(im, ((i % cols) * w, (i // cols) * h))
        sheet_path = outdir / f"{src.stem}-sheet.png"
        sheet.save(sheet_path)
        print(f"wrote {len(pages)} page images and {sheet_path}")


if __name__ == "__main__":
    main()
