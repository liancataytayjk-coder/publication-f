"""Audit a .docx or .pptx against the Lian signature style.

  python check_style.py file.docx|file.pptx [more files ...]

Prints one line per problem and exits with status 1 if any are found.
Checks fonts, colours, sizes, page or slide geometry, tables and shadows.
It does not judge layout or overflow: for those, render the file with
render.py --png and look at every page.
"""

import sys
import zipfile
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lian_spec as S  # noqa: E402

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
OK_FONTS = {S.FONT, S.FONT_CODE, "Cambria Math", None, "+mn-lt", "+mj-lt", "+mn-ea", "+mj-ea", "+mn-cs", "+mj-cs"}
SMALL_OK = ("Footer", "Slide number", "Source")


def _xml(z, name):
    try:
        return etree.fromstring(z.read(name))
    except KeyError:
        return None


def check_docx(path):
    issues = []
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.startswith("word/") and n.endswith(".xml")]
        doc = _xml(z, "word/document.xml")
        for n in names:
            if not any(k in n for k in ("document", "styles", "footnotes", "endnotes", "header", "footer")):
                continue
            root = _xml(z, n)
            fonts = {rf.get(f"{W}ascii") for rf in root.iter(f"{W}rFonts")} | {rf.get(f"{W}hAnsi") for rf in root.iter(f"{W}rFonts")}
            bad = sorted(f for f in fonts - OK_FONTS if f)
            if bad:
                issues.append(f"{n}: fonts other than {S.FONT}: {', '.join(bad)}")
            themed = [rf for rf in root.iter(f"{W}rFonts") if rf.get(f"{W}asciiTheme")]
            if themed:
                issues.append(f"{n}: {len(themed)} run(s) use theme fonts; run docx_style.py finish")
            cols = {(c.get(f"{W}val") or "").upper() for c in root.iter(f"{W}color")} - {"AUTO", ""}
            bad = sorted(cols - S.ALLOWED_COLOURS)
            if bad:
                issues.append(f"{n}: text colours outside black, white, grey and red: {', '.join(bad)}")
            if any(True for _ in root.iter(f"{W}highlight")):
                issues.append(f"{n}: highlighting present")
        for i, sect in enumerate(doc.iter(f"{W}sectPr")):
            pg, mar = sect.find(f"{W}pgSz"), sect.find(f"{W}pgMar")
            if pg is None or mar is None:
                issues.append(f"section {i + 1}: page size or margins not set")
                continue
            w_in, h_in = int(pg.get(f"{W}w")) / 1440, int(pg.get(f"{W}h")) / 1440
            if not any(abs(w_in - a) < 0.05 and abs(h_in - b) < 0.05 for a, b in S.PAPER.values()):
                issues.append(f"section {i + 1}: page {w_in:.2f} x {h_in:.2f} in is neither Letter nor A4")
            for side in ("top", "bottom", "left", "right"):
                v = int(mar.get(f"{W}{side}")) / 1440
                if abs(v - S.MARGIN_IN) > 0.01:
                    issues.append(f"section {i + 1}: {side} margin {v:.2f} in, not {S.MARGIN_IN:.0f} in")
        footers = [n for n in z.namelist() if n.startswith("word/footer")]
        if not any(b"PAGE" in z.read(n) for n in footers):
            issues.append("no page numbers in the footer")
        for t_i, tbl in enumerate(doc.iter(f"{W}tbl")):
            b = tbl.find(f"{W}tblPr/{W}tblBorders")
            if b is None:
                issues.append(f"table {t_i + 1}: no three-line borders; run docx_style.py finish")
                continue
            for side in ("left", "right", "insideV"):
                el = b.find(f"{W}{side}")
                if el is not None and el.get(f"{W}val") not in ("nil", "none"):
                    issues.append(f"table {t_i + 1}: has vertical lines")
                    break
            if any(s.get(f"{W}fill", "auto").upper() not in ("AUTO", "FFFFFF") for s in tbl.iter(f"{W}shd")):
                issues.append(f"table {t_i + 1}: has shaded cells")
        styles = _xml(z, "word/styles.xml")
        for st in styles.iter(f"{W}style"):
            if st.get(f"{W}styleId") == "Normal":
                sz = st.find(f"{W}rPr/{W}sz")
                if sz is not None and int(sz.get(f"{W}val")) != S.BODY_PT * 2:
                    issues.append(f"Normal style is {int(sz.get(f'{W}val')) / 2:g} pt, not {S.BODY_PT} pt")
    return issues


def check_pptx(path):
    issues = []
    with zipfile.ZipFile(path) as z:
        pres = _xml(z, "ppt/presentation.xml")
        sz = pres.find(f"{P}sldSz")
        cx, cy = int(sz.get("cx")), int(sz.get("cy"))
        if abs(cx / cy - 16 / 9) > 0.01:
            issues.append(f"slide size {cx / 914400:.2f} x {cy / 914400:.2f} in is not 16:9")
        for n in z.namelist():
            if n.startswith("ppt/theme/") and n.endswith(".xml"):
                th = _xml(z, n)
                for tag in ("majorFont", "minorFont"):
                    lat = th.find(f".//{A}{tag}/{A}latin")
                    if lat is not None and lat.get("typeface") != S.FONT:
                        issues.append(f"{n}: theme {tag} is {lat.get('typeface')}")
        slides = sorted((n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")),
                        key=lambda s: int("".join(c for c in s if c.isdigit())))
        for n in slides:
            label = Path(n).stem
            root = _xml(z, n)
            for sp in root.iter(f"{P}sp", f"{P}cxnSp", f"{P}pic", f"{P}graphicFrame"):
                nv = sp.find(f".//{P}cNvPr")
                name = nv.get("name") if nv is not None else "?"
                off = sp.find(f".//{A}off")
                ext = sp.find(f".//{A}ext")
                if off is not None and ext is not None and ext.get("cx"):
                    x, y, w, h = (int(off.get("x")), int(off.get("y")), int(ext.get("cx")), int(ext.get("cy")))
                    if x < 0 or y < 0 or x + w > cx + 9144 or y + h > cy + 9144:
                        issues.append(f"{label}: '{name}' runs off the slide")
                if sp.find(f"{P}style/{A}effectRef") is not None and sp.find(f"{P}style/{A}effectRef").get("idx") != "0":
                    issues.append(f"{label}: '{name}' carries a theme effect (shadow); remove its p:style")
                if sp.tag == f"{P}pic" and "logo" in name.lower():
                    issues.append(f"{label}: '{name}' looks like a logo; the style uses none")
                for r in sp.iter(f"{A}rPr", f"{A}defRPr", f"{A}endParaRPr"):
                    lat = r.find(f"{A}latin")
                    if lat is not None and lat.get("typeface") not in OK_FONTS:
                        issues.append(f"{label}: '{name}' uses {lat.get('typeface')}")
                    size = r.get("sz")
                    if r.tag == f"{A}rPr" and size and int(size) / 100 < S.SLIDE["min_pt"] and name not in SMALL_OK:
                        issues.append(f"{label}: '{name}' has {int(size) / 100:g} pt text (minimum {S.SLIDE['min_pt']})")
                for c in sp.iter(f"{A}srgbClr"):
                    if c.get("val", "").upper() not in S.ALLOWED_COLOURS:
                        issues.append(f"{label}: '{name}' uses colour #{c.get('val')}")
                        break
    seen, out = set(), []
    for i in issues:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def main(paths):
    bad = 0
    for p in paths:
        p = Path(p)
        issues = check_docx(p) if p.suffix.lower() in (".docx", ".dotx") else check_pptx(p)
        if issues:
            bad += 1
            print(f"{p.name}: {len(issues)} issue(s)")
            for i in issues:
                print("  -", i)
        else:
            print(f"{p.name}: OK")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
