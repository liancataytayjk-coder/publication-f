"""One place for every number in the Lian signature style.

All other scripts import from here, so a change made here (say, 10 pt table
text to 11 pt) reaches articles, decks and the style checker together.
"""

FONT = "Times New Roman"
FONT_CODE = "Courier New"  # code listings only

# Colours: black and white first. Greys are allowed for fills and footers.
# Red is the only accent, and only when the content needs it (an error or a
# warning the reader must not miss).
BLACK = "000000"
WHITE = "FFFFFF"
GREY_TEXT = "595959"   # footers, source lines on slides
GREY_RULE = "7F7F7F"
GREY_FILL = "F2F2F2"   # slide panels
RED = "C00000"         # exception colour; use sparingly
ALLOWED_COLOURS = {BLACK, WHITE, GREY_TEXT, GREY_RULE, GREY_FILL, RED, "404040", "808080", "D9D9D9", "BFBFBF"}

# ---------------------------------------------------------------- articles
PAPER = {"letter": (8.5, 11.0), "a4": (8.27, 11.69)}  # inches
DEFAULT_PAPER = "letter"
MARGIN_IN = 1.0
BODY_PT = 12
TITLE_PT = 14
SMALL_PT = 10            # footnotes, table text, table and figure notes
BODY_LINE_SPACING = 2.0  # double spacing for body text (journal manuscript)
FIRST_LINE_INDENT_IN = 0.5
HANGING_INDENT_IN = 0.5  # reference list

# ---------------------------------------------------------------- decks
SLIDE_W_IN, SLIDE_H_IN = 13.333, 7.5  # 16:9
SLIDE = {
    "margin_x": 0.6,
    "title_y": 0.40, "title_h": 0.70, "title_pt": 28,
    "key_y": 1.08, "key_h": 0.55, "key_pt": 18,
    "rule_y": 1.70,
    "body_y": 1.90, "body_bottom": 6.80,
    "footer_y": 7.02, "footer_h": 0.32, "footer_pt": 10,
    "body_pt": 18, "panel_head_pt": 18, "table_pt": 14,
    "min_pt": 12,
    "gap": 0.35,
}
