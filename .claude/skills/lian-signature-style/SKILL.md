---
name: lian-signature-style
description: Lian Cataytay's house style for every article and slide deck: clean, academic, black and white, Times New Roman, standard journal layout, no logos. Use this skill whenever you create, rewrite, restyle, convert or export an article, paper, manuscript, critical review, proposal, report, essay or any other Word (.docx) or PDF document, or a slide deck, presentation or .pptx, for this user, even if they never mention style, templates or this skill, and even when another skill (docx, pdf, pptx, empirical-econ-study) handles the file mechanics. It supplies the Word template, the deck builder, a finishing script and a style checker, so every output has the same look.
---

# Lian signature style

Every article and deck made for Lian should look like it came from the same
hand: clean, academic and black and white. This skill fixes that look. Other
skills still do the file mechanics (the docx, pdf and pptx skills;
empirical-econ-study for research documents). This skill decides how the
result looks, and its scripts make it look that way.

## Rules that always apply

1. **Black and white.** Text is black on white. Greys are allowed for slide
   panels, rules and footers. Use colour only when the content needs it,
   and then only red (#C00000), for example to mark an error the reader must
   not miss. Figures follow the black-and-white figure rules in
   empirical-econ-study: line styles and markers, grey fills, no colour.
2. **Times New Roman** everywhere, including headings, tables, captions,
   footnotes and slide text. Courier New is allowed only for code, and
   Cambria Math only for Word equations.
3. **Articles: 12 pt and standard margins.** Body text is 12 pt, with 1-inch
   margins on Letter paper (A4 only when the venue asks for it).
   Footnotes, table text and table or figure notes are 10 pt, as in
   journals. Body text is double-spaced. Everything else is single-spaced.
4. **Decks: Times New Roman sized for a screen.** 12 pt is unreadable on a
   slide, so on slides 12 pt is the *minimum*. Body text is 18 pt, titles
   28 pt and tables 14 to 16 pt. Only the footer is 10 pt.
5. **No logos, crests, wordmarks, monograms, banners, mottos or decorative
   images.** Do not invent anything logo-like. The output itself is the
   signature.
6. **Clean and academic.** No shadows, gradients, clip art, icons, WordArt or
   coloured table fills. Tables have three lines (a rule above, a rule under
   the header row, a rule below) and no vertical lines. Show emphasis with
   bold or italic, never colour.
7. **Anything not decided here follows standard journal style.** That means
   author–date citations (Chicago author–date, pandoc's default), numbered
   sections, the table title above the table, the figure caption below the
   figure, notes and the source under each table or figure, and equations
   numbered (1), (2) and so on.

**Precedence.** The user's explicit instruction in the current request comes
first. Next comes a template the user supplies from a journal, school or
conference: follow it exactly ("submission mode") and keep this style only
where the template is silent. Then this skill. Then generic defaults.

## Which file to make

Lian's outputs are **articles** and **decks**. Make real files:

- **Articles:** `.docx`. Also make a `.pdf` when the user asks for one or the
  file is going to be submitted or printed.
- **Decks:** `.pptx`, plus a `.pdf` copy when asked.

If the user asks for "a document" or "a deck" without naming a format, make
the file in this style. Do not switch to a claude.ai Doc or a Slides page
unless the user asks for one. If they do, carry over as much as the format
allows: Times New Roman, black text, the same structure.

## Articles: how to build one

Read `references/articles.md` for the full specification: the title page,
heading levels, tables, figures, equations, footnotes and references.

The preferred route is Markdown, then pandoc with the template, then the
finishing script:

```bash
SK=<this skill's directory>
pandoc article.md -o article.docx \
  --reference-doc=$SK/assets/lian-article-reference.docx \
  --number-sections --citeproc --bibliography=references.bib
python3 $SK/scripts/docx_style.py finish article.docx          # enforce the style
python3 $SK/scripts/render.py article.docx --png               # PDF + page images
python3 $SK/scripts/check_style.py article.docx                # audit
```

- **A document built another way** (docx-js, python-docx, an edited Word
  file, or the empirical-econ-study pipeline) still goes through
  `docx_style.py finish`. The script sets Times New Roman and black text,
  1-inch margins, page numbers, three-line tables and the paragraph styles.
  If you are writing python-docx code, start from
  `Document("$SK/assets/lian-article-reference.docx")`, which has every style
  already defined.
- **Spacing:** `finish --spacing onehalf` or `--spacing single` when there
  is a page limit or the user asks. `--paper a4` gives A4. `--allow-red`
  keeps red text that is there on purpose.
- **empirical-econ-study documents:** add
  `--reference-doc=$SK/assets/lian-article-reference.docx` to its pandoc call
  (`render_doc.py`), then run `finish`.
- **Restyling an existing .docx:** run `finish` on a copy, and never on the
  user's only original.
- **Starting by hand in Word:** `assets/lian-article-template.dotx`.

## Decks: how to build one

Read `references/decks.md` for the slide grammar, the layouts and the full
`Deck` API.

```python
import sys; sys.path.insert(0, "<this skill's directory>/scripts")
from lian_deck import Deck
d = Deck(short_title="Critical review · Agbola and Acupan (2010)")
d.title_slide("Title", ["Author (year)", "*Journal*, vol, pages"], byline="Prepared by: **Lian Cataytay**")
s = d.slide("1. Research problem and gap", "One-sentence key message.")
top, bottom = d.split(d.body(), 1.0)
left, right = d.columns(2, top)
d.text(s, left, ["point with **bold** key term", "second point"], heading="The problem")
d.panel(s, right, ["..."], heading="The gap")
d.callout(s, bottom, "Research question:", "How do ...?")
d.takeaway("Headline sentence.", ["...", "..."])
d.closing()
d.save("deck.pptx")
```

Then run `render.py deck.pptx --png` and `check_style.py deck.pptx`.
`scripts/example_deck.py` is a complete worked example covering every
layout, and `references/example_article.md` is the matching article.

- **Restyling an existing deck:** extract its text with python-pptx, then
  rebuild it with `Deck`. Do not repaint the old shapes. Keep the author's
  wording and structure, and drop institutional branding (banners, crests,
  slogans, copyright strips) unless the user asks to keep it.
- **Branded templates:** when the user must present on a school or
  conference template, that is submission mode. Use their template, and
  keep Times New Roman, black text and three-line tables where it allows.

## Before handing anything over

1. `check_style.py` reports OK. Fix every issue, or say why one stays.
2. Look at every page or slide image from `render.py --png`. Check for text
   running out of its box, collisions, orphaned headings, tables split
   badly, and empty slides. The builder's overflow warnings are estimates.
   The images are the test.
3. Times New Roman may be missing from the machine. LibreOffice then uses
   Liberation Serif, which has the same letter widths, so the layout is
   identical. In that case, tell the user the PDF was made with that
   stand-in, and that exporting from Word or PowerPoint gives true Times New
   Roman.
4. If the document has equations and `render.py` stops because the
   LibreOffice Math module is missing, install it
   (`apt-get install -y libreoffice-math`) rather than shipping a PDF with
   the equations missing.

## Files

- `assets/lian-article-reference.docx`: Word styles for pandoc, python-docx and the finisher.
- `assets/lian-article-template.dotx`: the same styles as a Word template.
- `assets/lian-deck-template.pptx`: 16:9, Times New Roman theme, black-and-white colour scheme.
- `scripts/lian_spec.py`: every size, colour and margin in one place; change it there.
- `scripts/docx_style.py`: `template` rebuilds the Word assets; `finish` enforces the style on any .docx.
- `scripts/lian_deck.py`: the deck builder; `python3 lian_deck.py template` rebuilds the deck template.
- `scripts/render.py`: .docx or .pptx to PDF, with page images and a contact sheet.
- `scripts/check_style.py`: audits fonts, colours, sizes, geometry, tables and shadows.
- `scripts/example_deck.py`, `references/example_article.md` (with `example_references.bib`): worked examples.
- `references/articles.md`, `references/decks.md`: the full specifications.
