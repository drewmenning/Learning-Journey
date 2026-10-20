from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree
import os

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "presentation")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, "AAI201 Capstone Predictive Maintenance Drew Menning.pptx")

NAVY    = RGBColor(0x21, 0x29, 0x5C)
DEEP    = RGBColor(0x06, 0x5A, 0x82)
TEAL    = RGBColor(0x1C, 0x72, 0x93)
SAND    = RGBColor(0xF2, 0xF4, 0xF7)
INK     = RGBColor(0x1A, 0x1F, 0x33)
SUBTLE  = RGBColor(0x6B, 0x73, 0x89)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
RED     = RGBColor(0xC0, 0x39, 0x2B)
GREEN   = RGBColor(0x2C, 0x7A, 0x4B)

HEADER_FONT = "Cambria"
BODY_FONT   = "Calibri"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]

def add_rect(slide, x, y, w, h, fill, line=None):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
    s.shadow.inherit = False
    return s

def add_text(slide, x, y, w, h, text, *, font=BODY_FONT, size=14, bold=False, italic=False,
             color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.15):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.margin_top = Emu(0); tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    lines = text.split("\n") if isinstance(text, str) else text
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        r.font.name = font
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
    return tb

def add_notes(slide, text):
    notes_tf = slide.notes_slide.notes_text_frame
    notes_tf.text = text

def title_strip(slide, title, *, on_dark=False):
    color_title = WHITE if on_dark else NAVY
    add_text(slide, Inches(0.6), Inches(0.45), Inches(12.1), Inches(0.7),
             title, font=HEADER_FONT, size=32, bold=True, color=color_title)

# ---- Slide 1: Title ----
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, SW, SH, NAVY)
add_rect(s, Inches(0), Inches(0), Inches(0.35), SH, DEEP)
add_text(s, Inches(0.9), Inches(2.2), Inches(11.6), Inches(0.4),
         "AAI201 MACHINE LEARNING  |  CAPSTONE PROJECT",
         font=BODY_FONT, size=14, bold=True, color=TEAL)
add_text(s, Inches(0.9), Inches(2.7), Inches(11.6), Inches(2.4),
         "Predictive Maintenance\nFailure Prediction",
         font=HEADER_FONT, size=54, bold=True, color=WHITE, line_spacing=1.05)
add_text(s, Inches(0.9), Inches(5.2), Inches(11.6), Inches(0.5),
         "Binary classification on the AI4I 2020 dataset using baseline and ensemble models",
         font=BODY_FONT, size=18, italic=True, color=SAND)
add_text(s, Inches(0.9), Inches(6.3), Inches(11.6), Inches(0.4),
         "Drew Menning   |   DMACC, Spring 2026",
         font=BODY_FONT, size=16, color=WHITE)
add_text(s, Inches(0.9), Inches(6.75), Inches(11.6), Inches(0.4),
         "github.com/drewmenning/ai4i-predictive-maintenance",
         font=BODY_FONT, size=13, color=TEAL)
add_notes(s, "Hi, I'm Drew Menning. This is my AAI201 capstone. I built a binary classifier that "
             "predicts whether an industrial machine is about to fail, using the AI4I 2020 "
             "predictive maintenance dataset from UCI. Over the next four minutes I'll walk through "
             "the problem, the data, what I built, the results on a held-out test set, one real "
             "fairness issue I found, and what I'd do next.")

# ---- Slide 2: Problem and dataset ----
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, SW, SH, SAND)
title_strip(s, "Problem and dataset")
add_rect(s, Inches(0.6), Inches(1.3), Inches(0.08), Inches(5.6), TEAL)

add_text(s, Inches(1.0), Inches(1.35), Inches(6.5), Inches(0.5),
         "Why predict machine failure?",
         font=HEADER_FONT, size=22, bold=True, color=NAVY)
add_text(s, Inches(1.0), Inches(1.95), Inches(6.5), Inches(2.5),
         "Unplanned downtime is expensive and disruptive. A model that flags machines "
         "likely to fail in the near term lets a maintenance team intervene early. The "
         "cost of a missed failure is much higher than the cost of an unnecessary "
         "inspection, so recall and threshold choice matter more than raw accuracy.",
         font=BODY_FONT, size=15, color=INK, line_spacing=1.25)

add_text(s, Inches(1.0), Inches(4.4), Inches(6.5), Inches(0.45),
         "Dataset: AI4I 2020 (UCI ML Repository)",
         font=HEADER_FONT, size=22, bold=True, color=NAVY)
add_text(s, Inches(1.0), Inches(4.95), Inches(6.5), Inches(2.0),
         "Synthetic, tabular. Features include product type, air temperature, "
         "process temperature, rotational speed, torque, and tool wear. Target is the "
         "binary Machine failure flag.",
         font=BODY_FONT, size=15, color=INK, line_spacing=1.25)

# Stat cards on the right
def stat_card(x, y, w, h, big, small):
    add_rect(s, x, y, w, h, WHITE, line=None)
    add_rect(s, x, y, w, Inches(0.08), TEAL)
    add_text(s, x + Inches(0.3), y + Inches(0.25), w - Inches(0.6), Inches(0.9),
             big, font=HEADER_FONT, size=40, bold=True, color=DEEP)
    add_text(s, x + Inches(0.3), y + Inches(1.15), w - Inches(0.6), Inches(0.6),
             small, font=BODY_FONT, size=12, color=SUBTLE, line_spacing=1.2)

stat_card(Inches(8.2), Inches(1.4),  Inches(4.5), Inches(1.7), "10,000", "rows in the dataset")
stat_card(Inches(8.2), Inches(3.3),  Inches(4.5), Inches(1.7), "3.39%",  "machines fail (339 of 10,000), a strongly imbalanced positive class")
stat_card(Inches(8.2), Inches(5.2),  Inches(4.5), Inches(1.7), "8",      "features used (after removing IDs and per-mode failure leak columns)")

add_notes(s, "Predictive maintenance matters because unplanned downtime is expensive. The model "
             "here is a binary classifier: failure or no failure. The dataset is the AI4I 2020 "
             "synthetic predictive-maintenance set from UCI, with ten thousand rows and a 3.4 "
             "percent positive rate. That imbalance is the single most important thing to call "
             "out, because a naive model that always predicts no-failure scores 96.6 percent "
             "accuracy and is completely useless. I dropped two ID columns and the five "
             "per-mode failure indicators, since those leak the binary target. Eight features remain.")

# ---- Slide 3: Approach ----
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, SW, SH, SAND)
title_strip(s, "Approach: baseline to ensemble, with the right metric")

# Left card - models
def section_card(x, y, w, h, header):
    add_rect(s, x, y, w, h, WHITE)
    add_rect(s, x, y, w, Inches(0.5), DEEP)
    add_text(s, x + Inches(0.3), y + Inches(0.06), w - Inches(0.6), Inches(0.4),
             header, font=HEADER_FONT, size=16, bold=True, color=WHITE)

section_card(Inches(0.6), Inches(1.4), Inches(6.0), Inches(5.5), "Models compared")
items_models = [
    ("Logistic Regression",   "L2 regularized, balanced class weights"),
    ("Decision Tree",         "max_depth = 6, min_samples_leaf = 20"),
    ("Random Forest",         "300 trees, depth 12, balanced weights"),
    ("HistGradientBoosting",  "Validation early stopping at 118 iters"),
]
y = Inches(2.0)
for name, sub in items_models:
    add_text(s, Inches(0.95), y, Inches(5.3), Inches(0.35),
             name, font=HEADER_FONT, size=15, bold=True, color=NAVY)
    add_text(s, Inches(0.95), y + Inches(0.36), Inches(5.3), Inches(0.45),
             sub, font=BODY_FONT, size=13, color=SUBTLE)
    y += Inches(1.1)

section_card(Inches(6.85), Inches(1.4), Inches(6.0), Inches(5.5), "Techniques")
items_tech = [
    ("Class imbalance",      "class_weight='balanced' + threshold tuning (no SMOTE on synthetic data)"),
    ("Threshold selection",  "F1-max on validation, applied unchanged to test"),
    ("Overfitting controls", "L2, depth limits, 5-fold stratified CV, early stopping"),
    ("Fairness check",       "Per-Type recall/precision (L, M, H quality grades)"),
]
y = Inches(2.0)
for name, sub in items_tech:
    add_text(s, Inches(7.2), y, Inches(5.3), Inches(0.35),
             name, font=HEADER_FONT, size=15, bold=True, color=NAVY)
    add_text(s, Inches(7.2), y + Inches(0.36), Inches(5.3), Inches(0.55),
             sub, font=BODY_FONT, size=13, color=SUBTLE, line_spacing=1.2)
    y += Inches(1.1)

add_notes(s, "I built up from simple to complex. Logistic regression and a depth-limited decision "
             "tree gave me a floor. Then Random Forest and HistGradientBoosting as the ensembles. "
             "The first three use balanced class weights to address the 3.4 percent failure rate; the "
             "booster has none and relies on the tuned threshold. The "
             "boosting model uses validation-based early stopping, which addresses my proposal "
             "feedback about avoiding leakage in early stopping. I deliberately did not use SMOTE; "
             "the dataset is already synthetic, so synthesizing minority samples on top would just "
             "compound the same modeling assumptions twice. For the failure decision threshold I "
             "chose the value that maximizes F1 on the validation set, then applied it unchanged to "
             "the test set. And I checked fairness across the three product quality grades.")

# ---- Slide 4: Model comparison ----
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, SW, SH, SAND)
title_strip(s, "Model comparison: 5-fold cross-validation PR-AUC")

# Manual horizontal bar chart
chart_x, chart_y = Inches(0.9), Inches(1.6)
chart_w, chart_h = Inches(8.6), Inches(5.3)
add_rect(s, chart_x, chart_y, chart_w, chart_h, WHITE)
models = [
    ("Logistic Regression", 0.463, 0.053),
    ("Decision Tree",       0.594, 0.019),
    ("Random Forest",       0.675, 0.064),
    ("HistGradientBoosting",0.759, 0.026),
]
inner_x = chart_x + Inches(2.3)
inner_w = chart_w - Inches(2.6)
row_h   = Inches(0.85)
top_pad = Inches(0.4)
max_val = 0.85  # axis cap
for i, (name, mean, std) in enumerate(models):
    cy = chart_y + top_pad + Inches(0.15) + i * row_h
    add_text(s, chart_x + Inches(0.15), cy + Inches(0.12), Inches(2.05), Inches(0.4),
             name, font=BODY_FONT, size=12, bold=True, color=INK, align=PP_ALIGN.RIGHT)
    bar_w = Emu(int(inner_w * (mean / max_val)))
    color = TEAL if name != "HistGradientBoosting" else DEEP
    add_rect(s, inner_x, cy + Inches(0.05), bar_w, Inches(0.5), color)
    add_text(s, inner_x + bar_w + Inches(0.1), cy + Inches(0.1), Inches(2.0), Inches(0.4),
             f"{mean:.3f}  ± {std:.3f}", font=BODY_FONT, size=12, bold=True, color=INK)

# Axis label
add_text(s, chart_x + Inches(0.15), chart_y + chart_h - Inches(0.4),
         chart_w - Inches(0.3), Inches(0.3),
         "PR-AUC (5-fold mean ± std on training set)",
         font=BODY_FONT, size=11, italic=True, color=SUBTLE)

# Right side commentary card
side_x, side_y = Inches(9.7), Inches(1.6)
side_w, side_h = Inches(3.1), Inches(5.3)
add_rect(s, side_x, side_y, side_w, side_h, NAVY)
add_text(s, side_x + Inches(0.25), side_y + Inches(0.2), side_w - Inches(0.5), Inches(0.5),
         "Why PR-AUC?", font=HEADER_FONT, size=18, bold=True, color=WHITE)
add_text(s, side_x + Inches(0.25), side_y + Inches(0.8), side_w - Inches(0.5), Inches(2.4),
         "ROC-AUC stays high on imbalanced data because true negatives dominate. PR-AUC ignores those and rewards models that actually rank failures high.",
         font=BODY_FONT, size=12, color=SAND, line_spacing=1.3)
add_text(s, side_x + Inches(0.25), side_y + Inches(3.3), side_w - Inches(0.5), Inches(0.5),
         "HGB has the best mean.", font=HEADER_FONT, size=14, bold=True, color=TEAL)
add_text(s, side_x + Inches(0.25), side_y + Inches(3.85), side_w - Inches(0.5), Inches(1.3),
         "0.759 mean PR-AUC (±0.026), well ahead of Random Forest at 0.675.",
         font=BODY_FONT, size=12, color=SAND, line_spacing=1.3)

add_notes(s, "Five-fold cross-validation on PR-AUC. Logistic regression and decision tree are the "
             "baselines, and you can see ensembles pull ahead. HistGradientBoosting wins with a mean "
             "PR-AUC of 0.759 and a standard deviation of 0.026, well ahead of Random Forest at 0.675. "
             "I'm using PR-AUC instead of ROC-AUC because at 3.4 percent positive rate, ROC-AUC "
             "stays high almost by default. PR-AUC is the metric that actually penalizes a model "
             "for missing failures.")

# ---- Slide 5: Final test results ----
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, SW, SH, SAND)
title_strip(s, "Final test results: HistGradientBoosting + tuned threshold")

# Left: KPI cards
def kpi(x, y, w, h, big, label, accent=DEEP):
    add_rect(s, x, y, w, h, WHITE)
    add_rect(s, x, y, Inches(0.08), h, accent)
    add_text(s, x + Inches(0.3), y + Inches(0.2), w - Inches(0.5), Inches(0.9),
             big, font=HEADER_FONT, size=36, bold=True, color=NAVY)
    add_text(s, x + Inches(0.3), y + Inches(1.0), w - Inches(0.5), Inches(0.5),
             label, font=BODY_FONT, size=12, color=SUBTLE, line_spacing=1.2)

kpi(Inches(0.6), Inches(1.4), Inches(2.95), Inches(1.6), "0.882", "PR-AUC")
kpi(Inches(3.7), Inches(1.4), Inches(2.95), Inches(1.6), "0.804", "Recall (failures caught)")
kpi(Inches(0.6), Inches(3.2), Inches(2.95), Inches(1.6), "0.911", "Precision")
kpi(Inches(3.7), Inches(3.2), Inches(2.95), Inches(1.6), "0.854", "F1 score")
kpi(Inches(0.6), Inches(5.0), Inches(2.95), Inches(1.6), "0.981", "ROC-AUC", accent=TEAL)
kpi(Inches(3.7), Inches(5.0), Inches(2.95), Inches(1.6), "0.991", "Accuracy", accent=TEAL)

# Right: confusion matrix card
cx, cy = Inches(7.0), Inches(1.4)
cw, ch = Inches(5.85), Inches(5.2)
add_rect(s, cx, cy, cw, ch, WHITE)
add_text(s, cx + Inches(0.3), cy + Inches(0.2), cw - Inches(0.6), Inches(0.5),
         "Confusion matrix (held-out test set)", font=HEADER_FONT, size=18, bold=True, color=NAVY)
add_text(s, cx + Inches(0.3), cy + Inches(0.7), cw - Inches(0.6), Inches(0.4),
         "Threshold = 0.496, chosen by F1-max on validation",
         font=BODY_FONT, size=12, italic=True, color=SUBTLE)

# 2x2 confusion matrix
mx = cx + Inches(1.4)
my = cy + Inches(1.85)
cell_w, cell_h = Inches(2.0), Inches(1.4)
# headers (moved well above cells)
add_text(s, mx, my - Inches(0.85), cell_w*2, Inches(0.3),
         "Predicted", font=BODY_FONT, size=12, italic=True, color=SUBTLE, align=PP_ALIGN.CENTER)
add_text(s, mx, my - Inches(0.45), cell_w, Inches(0.3), "No failure",
         font=BODY_FONT, size=11, bold=True, color=INK, align=PP_ALIGN.CENTER)
add_text(s, mx + cell_w, my - Inches(0.45), cell_w, Inches(0.3), "Failure",
         font=BODY_FONT, size=11, bold=True, color=INK, align=PP_ALIGN.CENTER)
add_text(s, mx - Inches(1.25), my + Inches(0.5), Inches(1.1), Inches(0.4), "No failure",
         font=BODY_FONT, size=11, bold=True, color=INK, align=PP_ALIGN.RIGHT)
add_text(s, mx - Inches(1.25), my + cell_h + Inches(0.5), Inches(1.1), Inches(0.4), "Failure",
         font=BODY_FONT, size=11, bold=True, color=INK, align=PP_ALIGN.RIGHT)
add_text(s, mx - Inches(1.75), my + Inches(1.0), Inches(0.5), Inches(0.5),
         "Actual", font=BODY_FONT, size=12, italic=True, color=SUBTLE, align=PP_ALIGN.CENTER)

def matrix_cell(x, y, value, label, fill, fg):
    add_rect(s, x, y, cell_w, cell_h, fill)
    add_text(s, x, y + Inches(0.25), cell_w, Inches(0.7),
             str(value), font=HEADER_FONT, size=32, bold=True, color=fg, align=PP_ALIGN.CENTER)
    add_text(s, x, y + Inches(0.95), cell_w, Inches(0.4),
             label, font=BODY_FONT, size=11, color=fg, align=PP_ALIGN.CENTER)

matrix_cell(mx,           my,           1445, "True negative",  GREEN, WHITE)
matrix_cell(mx + cell_w,  my,           4,    "False positive", SUBTLE, WHITE)
matrix_cell(mx,           my + cell_h,  10,   "False negative", RED,    WHITE)
matrix_cell(mx + cell_w,  my + cell_h,  41,   "True positive",  GREEN,  WHITE)

add_text(s, cx + Inches(0.3), cy + ch - Inches(0.6), cw - Inches(0.6), Inches(0.4),
         "Caught 41 of 51 real failures with only 4 false alarms.",
         font=BODY_FONT, size=13, italic=True, color=NAVY, align=PP_ALIGN.LEFT)

add_notes(s, "On the held-out test set the gradient booster gets PR-AUC 0.882 with recall 0.80 "
             "and precision 0.91. F1 is 0.85. Accuracy is 0.99 but accuracy is not the right "
             "metric here, so I keep it on the side. The threshold I used is 0.496, chosen by "
             "maximizing F1 on the validation set and then applied unchanged to the test set. "
             "The confusion matrix tells the operational story: out of 51 real failures in the "
             "test set, the model caught 41 and missed 10. Of the 1449 non-failures, only 4 got "
             "flagged. So a maintenance team using this model would investigate 45 cases to "
             "catch 41 actual failures, which is a workable false-alarm rate.")

# ---- Slide 6: Bias finding ----
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, SW, SH, SAND)
title_strip(s, "Real finding: the model fails on Type H machines")

# Table card
tx, ty = Inches(0.6), Inches(1.4)
tw, th = Inches(8.2), Inches(4.4)
add_rect(s, tx, ty, tw, th, WHITE)
add_text(s, tx + Inches(0.3), ty + Inches(0.2), tw - Inches(0.6), Inches(0.5),
         "Validation-set performance by product quality type",
         font=HEADER_FONT, size=18, bold=True, color=NAVY)

# header row
hy = ty + Inches(0.95)
col_xs   = [tx + Inches(0.4), tx + Inches(2.0), tx + Inches(3.5), tx + Inches(5.1), tx + Inches(6.7)]
col_ws   = [Inches(1.5), Inches(1.4), Inches(1.5), Inches(1.5), Inches(1.4)]
headers  = ["Type", "n", "Failure rate", "Recall", "Precision"]
for i, h in enumerate(headers):
    add_text(s, col_xs[i], hy, col_ws[i], Inches(0.4),
             h, font=BODY_FONT, size=12, bold=True, color=SUBTLE)

rows = [
    ("L", "924", "4.0%", "0.649", "0.96", False),
    ("M", "459", "2.2%", "0.700", "0.70", False),
    ("H", "118", "3.4%", "0.000", "0.00", True),
]
ry = hy + Inches(0.45)
for r in rows:
    label, n, fr, rec, prec, highlight = r
    if highlight:
        add_rect(s, tx + Inches(0.15), ry - Inches(0.05),
                 tw - Inches(0.3), Inches(0.65), RGBColor(0xFD, 0xEC, 0xEA))
    color = RED if highlight else INK
    weight = True if highlight else False
    add_text(s, col_xs[0], ry, col_ws[0], Inches(0.5), label,
             font=BODY_FONT, size=15, bold=True, color=color)
    add_text(s, col_xs[1], ry, col_ws[1], Inches(0.5), n,
             font=BODY_FONT, size=15, color=color, bold=weight)
    add_text(s, col_xs[2], ry, col_ws[2], Inches(0.5), fr,
             font=BODY_FONT, size=15, color=color, bold=weight)
    add_text(s, col_xs[3], ry, col_ws[3], Inches(0.5), rec,
             font=BODY_FONT, size=15, color=color, bold=weight)
    add_text(s, col_xs[4], ry, col_ws[4], Inches(0.5), prec,
             font=BODY_FONT, size=15, color=color, bold=weight)
    ry += Inches(0.7)

add_text(s, tx + Inches(0.3), ty + th - Inches(0.6), tw - Inches(0.6), Inches(0.4),
         "On Type H machines, the model caught 0 of 4 failures.",
         font=BODY_FONT, size=14, italic=True, color=RED)

# Right side: implication
side_x, side_y = Inches(9.0), Inches(1.4)
side_w, side_h = Inches(3.85), Inches(4.4)
add_rect(s, side_x, side_y, side_w, side_h, NAVY)
add_text(s, side_x + Inches(0.25), side_y + Inches(0.25), side_w - Inches(0.5), Inches(0.5),
         "Why this matters", font=HEADER_FONT, size=18, bold=True, color=WHITE)
add_text(s, side_x + Inches(0.25), side_y + Inches(0.85), side_w - Inches(0.5), Inches(3.4),
         "H is the smallest grade: 118 of the 1,501 validation machines. With four real failures in "
         "validation, the model has almost nothing to learn from. The result generalizes: any "
         "deployment plan would need stratified sampling, a separate H-specific model, or an "
         "explicit out-of-scope flag for that grade.",
         font=BODY_FONT, size=12, color=SAND, line_spacing=1.35)

# Bottom note
add_text(s, Inches(0.6), Inches(6.1), Inches(12.1), Inches(0.6),
         "Took the proposal's fairness check seriously and it surfaced a real problem, not a checkbox.",
         font=BODY_FONT, size=14, italic=True, color=NAVY)

add_notes(s, "This is the most important slide in the deck. The proposal asked me to compare "
             "performance across product quality types, L, M, and H. On L and M the model is "
             "fine, recall around 65 to 70 percent. On Type H the model has zero recall. It "
             "caught zero of four real failures. The reason is data scale: H is only about six "
             "percent of the dataset, so the validation set has only four H failures, and that's "
             "not enough signal to learn from. The takeaway is that overall accuracy hides this "
             "completely, which is exactly why fairness checks belong in the workflow. A "
             "production deployment would need either stratified resampling, a separate H-specific "
             "model, or an explicit warning that the model is out of scope for high-grade machines.")

# ---- Slide 7: Reflection and next steps ----
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, SW, SH, NAVY)
add_text(s, Inches(0.6), Inches(0.5), Inches(12.1), Inches(0.7),
         "Reflection and next steps", font=HEADER_FONT, size=32, bold=True, color=WHITE)

def takeaway_card(x, y, w, h, header, body, accent=TEAL):
    add_rect(s, x, y, w, h, RGBColor(0x2D, 0x36, 0x6E))
    add_rect(s, x, y, Inches(0.08), h, accent)
    add_text(s, x + Inches(0.3), y + Inches(0.2), w - Inches(0.5), Inches(0.5),
             header, font=HEADER_FONT, size=16, bold=True, color=WHITE)
    add_text(s, x + Inches(0.3), y + Inches(0.75), w - Inches(0.5), h - Inches(0.9),
             body, font=BODY_FONT, size=12, color=SAND, line_spacing=1.35)

takeaway_card(Inches(0.6), Inches(1.5), Inches(4.0), Inches(2.6),
              "What I learned",
              "The model mattered more than the threshold. In cross-validation the booster's "
              "PR-AUC was 0.76 against 0.59 for the decision tree, and tuning only moved the "
              "cutoff from 0.5 to 0.496. PR-AUC split the models far more clearly than ROC-AUC.")
takeaway_card(Inches(4.75), Inches(1.5), Inches(4.0), Inches(2.6),
              "Hardest decision",
              "Choosing the failure threshold. F1-max on validation picked 0.496, close to the "
              "default 0.5, and lifted validation recall from 0.588 to 0.608 without needing a "
              "cost ratio I couldn't justify on synthetic data.")
takeaway_card(Inches(8.9), Inches(1.5), Inches(4.0), Inches(2.6),
              "Honest limitation",
              "AI4I 2020 is synthetic. Feature distributions and failure logic are generated, "
              "not measured. The model is a credible result on this dataset but not a guarantee "
              "on a real shop floor with sensor noise and timing offsets.")

add_text(s, Inches(0.6), Inches(4.45), Inches(12.1), Inches(0.5),
         "Next steps", font=HEADER_FONT, size=22, bold=True, color=WHITE)

next_items = [
    ("Real data",        "Validate against NASA C-MAPSS or PHM Society datasets to test transfer."),
    ("Cost-based threshold", "Replace F1-max with a threshold tied to documented FN vs FP costs."),
    ("Type H repair",    "Stratified resampling, an H-specific model, or an explicit out-of-scope flag."),
    ("Drift monitoring", "Add input-feature drift checks and a recalibration trigger in production."),
]
nx, ny = Inches(0.6), Inches(5.05)
nw = Inches(6.0)
nh = Inches(0.85)
for i, (label, desc) in enumerate(next_items):
    cx = nx + (i % 2) * Inches(6.35)
    cy = ny + (i // 2) * Inches(1.05)
    add_rect(s, cx, cy, Inches(0.5), Inches(0.5), TEAL)
    add_text(s, cx + Inches(0.05), cy + Inches(0.06), Inches(0.4), Inches(0.4),
             str(i+1), font=HEADER_FONT, size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, cx + Inches(0.7), cy, Inches(5.4), Inches(0.4),
             label, font=HEADER_FONT, size=14, bold=True, color=WHITE)
    add_text(s, cx + Inches(0.7), cy + Inches(0.4), Inches(5.4), Inches(0.6),
             desc, font=BODY_FONT, size=11, color=SAND, line_spacing=1.3)

add_text(s, Inches(0.6), Inches(7.15), Inches(12.1), Inches(0.3),
         "github.com/drewmenning/ai4i-predictive-maintenance",
         font=BODY_FONT, size=12, italic=True, color=TEAL)

add_notes(s, "The biggest thing I learned is that the model family mattered more than I expected. "
             "In cross-validation the booster reached a PR-AUC of 0.76 against 0.59 for the "
             "decision tree, while threshold tuning barely moved the cutoff, from 0.5 to 0.496, "
             "and lifted validation recall from 0.588 to 0.608. The hardest decision was picking "
             "the failure threshold without a real cost ratio, so I used the F1-max threshold "
             "from validation. Honest limitation: this is "
             "a synthetic dataset, so the result is credible on AI4I but not a deployment "
             "guarantee. Next steps in priority order: validate on a real predictive-maintenance "
             "dataset like NASA C-MAPSS, replace F1 with a cost-based threshold, fix the Type H "
             "blind spot, and add drift monitoring. Thanks for watching, the GitHub link is on "
             "this slide.")

import datetime
now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None, microsecond=0)
cp = prs.core_properties
cp.author = "Drew Menning"
cp.last_modified_by = "Drew Menning"
cp.title = "Predicting Machine Failures on the AI4I 2020 Dataset"
cp.created = now
cp.modified = now
cp.revision = 1
prs.save(OUT_PATH)
print(f"Saved: {OUT_PATH}")
