# Articles: full specification

These settings apply to articles, papers, manuscripts, critical reviews,
proposals and reports. They follow standard journal manuscript practice; the
numbers live in `scripts/lian_spec.py`.

## Page

| Item | Setting |
|---|---|
| Paper | US Letter (8.5 × 11 in); A4 only when the venue asks (`--paper a4`) |
| Margins | 1 in on all four sides; header and footer 0.5 in from the edge |
| Page numbers | Arabic, centred in the footer, 12 pt, on every page |
| Running head, logos, watermarks | None |

## Type and spacing

| Element | Font and size | Spacing and alignment |
|---|---|---|
| Body text | Times New Roman 12 | Double-spaced, flush left (ragged right), first line indented 0.5 in, no space between paragraphs |
| First paragraph after a heading | 12 | Not indented |
| Title | 14 bold | Centred, single-spaced |
| Author, affiliation, date | 12 | Centred; affiliation and acknowledgements go in a footnote on the author's name |
| "Abstract" label | 12 bold | Centred |
| Abstract | 12 | Single-spaced, indented 0.5 in on both sides, justified; 150–250 words |
| Keywords, JEL codes | 12, label in bold | In the abstract block, one line each |
| Heading 1 | 12 bold | Numbered "1", "2" ...; flush left |
| Heading 2 | 12 bold italic | Numbered "1.1" ... |
| Heading 3 | 12 italic | Numbered "1.1.1" ... ; avoid going deeper |
| Block quotation (40+ words) | 12 | Single-spaced, indented 0.5 in on both sides |
| Footnotes | 10 | Single-spaced; prefer footnotes to endnotes |
| Table text | 10 | Single-spaced |
| Table and figure notes, sources | 10 | Single-spaced, flush left |
| Reference list | 12 | Single-spaced, 0.5 in hanging indent, 6 pt between entries |
| Code (rare) | Courier New 10 | |

Spacing options: `finish --spacing onehalf` or `--spacing single` change the
body and heading spacing when there is a page limit or the user asks. Say
which spacing you used.

## Structure

The default order is title block, abstract, numbered sections, then the
unnumbered References, then any appendices (A, B, ...). For an empirical
paper the sections are: Introduction, Literature (or Theoretical framework),
Data, Method, Results, Discussion or Robustness, Conclusion. A critical
review follows the reviewed paper's own structure, then adds an assessment
and suggestions.

## Tables

- Three lines only: a 1.5 pt rule above the table, a 0.75 pt rule under the
  header row, a 1.5 pt rule below. No vertical lines, no inner horizontal
  lines, no shading, no colour. `docx_style.py finish` applies this to every
  table.
- Title above the table, flush left: "Table 1. Title in sentence case". The
  header row is not bold (journal style).
- Numbers right-aligned or decimal-aligned. Negative numbers use a true
  minus sign (−), not a hyphen.
- Regression tables report standard errors (or *t*-statistics, if the
  source does) in parentheses under or beside the coefficients. Stars:
  \*\*\* *p* < 0.01, \*\* *p* < 0.05, \* *p* < 0.10, defined in the note.
- Under the table: "*Notes:* ..." then "*Source:* ...", in 10 pt.
- Tables are for data and estimates. Write lists of ideas as paragraphs.

## Figures

- Black and white, following empirical-econ-study's figure rules: a serif
  font, no title inside the image, line styles and markers to tell series
  apart, grey bands, 300 dpi.
- Centred. The caption goes below, flush left: "Figure 1. A full sentence
  saying what is plotted, the units and what the bands mean." Notes and the
  source follow in 10 pt.

## Equations

Display equations are centred and numbered in parentheses. In pandoc
Markdown write the number inside the display:
`$$ y_t = \alpha + \beta x_t + \varepsilon_t \qquad\qquad (1) $$`. Refer to
it as "equation (1)". Define every symbol in the sentence after the equation.

## Citations and references

Use author–date citations: (Todaro 1969), Todaro (1969), (Agbola and Acupan
2010, 390). Pandoc's default citation style is Chicago author–date, so with
`--citeproc` and a `.bib` file nothing else is needed. A journal's own
style replaces it in submission mode (pass `--csl=<journal>.csl`). Every
in-text citation has a reference-list entry, and every entry is cited.

## Pandoc Markdown cheat sheet

```markdown
---
title: "Title of the Article"
author:
  - "Lian Cataytay[^aff]"
date: "October 2026"
abstract: |
  One paragraph, 150–250 words.

  **Keywords:** word, word, word

  **JEL codes:** F22, J61
---

[^aff]: Affiliation; acknowledgements; contact e-mail.

# Introduction

Text with a citation [@todaro1969] and a footnote.[^1]

[^1]: Footnote text.

| Variable     | Coefficient | SE      |
|:-------------|------------:|--------:|
| Unemployment | 0.236\*\*\* | (0.051) |

Table: Table 1. Title of the table

::: {custom-style="Table Note"}
*Notes:* Standard errors in parentheses. \*\*\* *p* < 0.01.

*Source:* Authors' calculations.
:::

![Figure 1. Caption sentence.](figures/fig1.png){width=80%}

::: {custom-style="Figure Note"}
*Source:* ...
:::

# References {-}

::: {#refs}
:::
```

Build with `--number-sections`. `{-}` leaves a heading unnumbered. A worked
example is in `references/example_article.md`, with its `.bib` file in
`references/example_references.bib`.

## Other routes

- **python-docx:** `Document("<skill>/assets/lian-article-reference.docx")`
  gives an empty document with every style above ("Title", "Author",
  "Abstract", "Heading 1–3", "First Paragraph", "Body Text", "Table Caption",
  "Table Note", "Image Caption", "Figure Note", "Bibliography", "Footnote
  Text"). Use the styles rather than direct formatting, then run `finish`.
- **docx-js** (empirical-econ-study's route for exact Word layouts): set
  `font: "Times New Roman"`, `size: 24` (half-points), and margins of 1440
  twips, then run `finish` on the result.
- **Existing Word files:** run `finish` on a copy. It changes fonts, colours,
  margins, tables and the paragraph styles. It does not rewrite
  direct paragraph formatting that someone typed by hand, so look at the
  rendered pages afterwards.

## Submission mode

When a journal, school or conference supplies a template or author guide,
follow it exactly: its paper size, spacing, heading style, reference style
and word limits. Keep this house style only where the guide is silent.
Run `check_style.py` anyway. Its warnings about margins or spacing are
expected when the guide asks for something different, and you should say so
rather than "fix" them.
