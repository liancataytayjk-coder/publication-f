# Decks: full specification

The deck style keeps the structure of Lian's critical-review decks:
a title and a one-sentence key message on every slide, two-column bodies,
three-line tables, boxed callouts, a takeaway slide and a closing slide. It
drops institutional colour and branding, and redraws everything in black and
white Times New Roman.

## Page and geometry (16:9, 13.333 × 7.5 in)

| Zone | Position | Content |
|---|---|---|
| Side margins | 0.6 in | Nothing outside them |
| Title | top 0.40 in, 0.70 in tall | 28 pt bold (24 pt if it needs a second line) |
| Key message | top 1.08 in | 18 pt italic, **one sentence, one line** |
| Rule | at 1.70 in | 0.75 pt black, the full content width |
| Body | 1.90 to 6.80 in | Text, panels, tables, figures, callouts |
| Footer | at 7.02 in | Short title on the left, slide number on the right, 10 pt grey |

Colours: black text on white; panels light grey (#F2F2F2) with no outline;
callouts white with a 1 pt black outline; footer text grey (#595959). Red
(#C00000) only when the content demands it. No shadows, gradients, pictures
of buildings, crests, logos or banners.

## Type sizes

| Element | Size |
|---|---|
| Title slide title | 36 pt bold (32 pt for long titles) |
| Slide title | 28 pt bold |
| Key message | 18 pt italic |
| Body text, panel text, callout | 18 pt; shrinks to a minimum of 12 pt only when needed |
| Panel and column headings | 18 pt bold |
| Tables | 14–16 pt; header row bold |
| Captions, source lines | 12 pt |
| Footer | 10 pt |

The builder shrinks text 1 pt at a time until it fits and warns when it
still does not fit at the minimum. If it shrinks below 16 pt, cut words
rather than accepting small text.

## Slide grammar

1. **Title slide:** the title; a short centred rule; the citation or subtitle
   lines (journal names in italics); "Prepared by: **Lian Cataytay**";
   optionally a course or date line. Nothing else: no logo, no slogan, no
   institution banner.
2. **Content slides:** the title says the topic, often numbered to follow
   the reviewed paper or the talk's outline ("1. Research problem and gap").
   The key message says the point in one full sentence. The body supports
   it.
3. **Takeaway slide:** the label "TAKEAWAY", a headline sentence, a rule,
   and two to four bold-led bullets.
4. **Closing slide:** "Thank you" and "Questions and discussion".
5. Optional **section slides** to divide a long talk.

Writing rules for slides:

- Five bullets at most per column, each no longer than two lines.
- Lead with the key term in **bold** ("**Small sample:** 31 yearly
  observations ..."). Bold replaces the coloured highlights of the old
  template.
- Define terms once (a "Key terms" table slide works well) and use them the
  same way on every slide.
- Numbers need units and the source, given in a `source()` line or a table
  note.
- At most one callout per slide, labelled "Research question:", "Critical
  view:", "Watch-out:" or "Key point:".

## Layout catalogue (from the reference deck)

| Need | Calls |
|---|---|
| Two columns of points | `left, right = d.columns(2)`, then `d.text(s, left, items, heading=...)` for each |
| Points plus a fact box | `d.text(...)` on the left, `d.panel(...)` on the right |
| Body plus a callout strip | `top, bottom = d.split(d.body(), 1.0)`, then `d.callout(s, bottom, "Critical view:", "...")` |
| Unequal columns | `d.columns(2, widths=[1.4, 1])` |
| Four findings | `for box in d.grid(2, 2): d.panel(s, box, [text], heading=..., bullets=False)` |
| Steps | `d.text(s, box, steps, numbered=True)` |
| Definitions or data table | `d.table(s, d.body(), rows, col_widths=[1, 3], first_col_bold=True, size=16)` |
| Results table | `d.table(s, top, rows, col_widths=[...], align=["l", "r", "r", "l"], size=14)`, then `d.source(s, "Source: ...")` |
| Figure | `d.image(s, box, "fig.png", caption="Figure 1. ...")` (black-and-white figures only) |
| Speaker notes | `d.notes(s, "...")` |

## Deck API

`Deck(short_title="...", footer=True)` loads `assets/lian-deck-template.pptx`.

- **Geometry** (all in inches, returning `Box(x, y, w, h)`): `body()`,
  `columns(n, box=None, widths=None)`, `rows(n, box=None, heights=None)`,
  `grid(r, c, box=None)`, `split(box, bottom_h)` → `(top, bottom)`.
- **Slides:** `title_slide(title, subtitle_lines, byline=None, date=None)`,
  `slide(title, key_message=None)`, `section_slide(title, subtitle=None)`,
  `takeaway(headline, items)`, `closing(title, subtitle)`.
- **Content:** `text(slide, box, items, heading=None, size=None,
  bullets=True, numbered=False)`, `panel(...)` (the same arguments, on a
  grey card), `callout(slide, box, label, text)`, `table(slide, box, rows,
  col_widths=None, size=None, header=True, first_col_bold=False,
  align=None)`, `image(slide, box, path, caption=None)`, `source(slide,
  text)`, `notes(slide, text)`.
- **Items:** a string, or `(1, "sub-point")` for a second level. Inline
  markup: `**bold**`, `*italic*`, `^{sup}`, `_{sub}`. Superscripts and
  subscripts may sit inside bold or italic text.
- `save(path)` prints any overflow warnings. Read them, then look at the
  rendered slides.

`scripts/example_deck.py` rebuilds the Agbola and Acupan (2010) critical
review deck and uses every layout. Copy its patterns.

## Editing decks the user made

To restyle an existing deck, extract each slide's text and tables with
python-pptx and rebuild the deck with `Deck`, keeping the wording and order.
If the user wants only small edits to a deck that must stay in its original
template, use the pptx skill, and keep Times New Roman and black text where
the template allows.
