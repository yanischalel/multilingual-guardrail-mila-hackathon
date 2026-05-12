"""Architecture diagram, modern card aesthetic.

Design principles:
- Light tinted cards with strong borders, drop shadows for depth.
- One accent color per semantic category (input, model, decision, outcome, human).
- Dark text inside cards for clean typography hierarchy.
- Single column primary flow, fail-safe as a clearly secondary side card.
- Real diamond for decision, elbow connectors for outcome convergence.
- Transparent background so the diagram reads on both light and dark themes.
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, PathPatch
from matplotlib.path import Path as MplPath

OUT = Path("/Users/yanis/multilingual-guardrail-mila-hackathon/assets/architecture.png")

# ============================================================
# Color system
# ============================================================
# Each category has: fill (very light tint), border (mid), accent (dark for title text)
PALETTE = {
    "input":    {"fill": "#EFF6FF", "border": "#3B82F6", "accent": "#1E3A8A"},
    "model":    {"fill": "#F5F3FF", "border": "#8B5CF6", "accent": "#4C1D95"},
    "decision": {"fill": "#FEF3C7", "border": "#F59E0B", "accent": "#78350F"},
    "high":     {"fill": "#FEE2E2", "border": "#EF4444", "accent": "#7F1D1D"},
    "low":      {"fill": "#D1FAE5", "border": "#10B981", "accent": "#065F46"},
    "human":    {"fill": "#F1F5F9", "border": "#64748B", "accent": "#1E293B"},
    "failsafe": {"fill": "#F8FAFC", "border": "#94A3B8", "accent": "#475569"},
}

INK_TITLE = "#111827"       # title text
INK_BODY = "#374151"        # body text
INK_MUTED = "#6B7280"       # subtitle / arrow labels
INK_SUBTLE = "#9CA3AF"      # footer / very secondary

# ============================================================
# Canvas
# ============================================================
CANVAS_W, CANVAS_H = 16.5, 13
CX = 7.0  # primary column center (kept left-of-center to leave room for side annotation)

fig, ax = plt.subplots(figsize=(CANVAS_W, CANVAS_H), dpi=120)
ax.set_xlim(0, CANVAS_W)
ax.set_ylim(0, CANVAS_H)
ax.axis("off")
fig.patch.set_alpha(0.0)


# ============================================================
# Drawing primitives
# ============================================================
def card(cx, cy, w, h, category, dashed_border=False, shadow=True,
         rounding=0.22, lw=1.4):
    p = PALETTE[category]
    if shadow:
        sh = FancyBboxPatch(
            (cx - w / 2 + 0.06, cy - h / 2 - 0.08), w, h,
            boxstyle=f"round,pad=0,rounding_size={rounding}",
            linewidth=0, facecolor="black", alpha=0.08, zorder=1,
        )
        ax.add_patch(sh)
    body = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle=f"round,pad=0,rounding_size={rounding}",
        linewidth=lw,
        edgecolor=p["border"],
        facecolor=p["fill"],
        linestyle=((0, (5, 3)) if dashed_border else "-"),
        zorder=2,
    )
    ax.add_patch(body)


def title(cx, cy, s, category, size=14, weight="bold"):
    ax.text(cx, cy, s, ha="center", va="center",
            fontsize=size, fontweight=weight,
            color=PALETTE[category]["accent"], zorder=3)


def subtitle(cx, cy, s, size=10, color=INK_MUTED, style="normal"):
    ax.text(cx, cy, s, ha="center", va="center",
            fontsize=size, color=color, fontstyle=style, zorder=3)


def body(cx, cy, s, size=10.5, color=INK_BODY, weight="normal", style="normal",
         ha="center"):
    ax.text(cx, cy, s, ha=ha, va="center",
            fontsize=size, color=color, fontweight=weight, fontstyle=style,
            zorder=3)


def arrow(x1, y1, x2, y2, lbl=None, lbl_off=(0.2, 0),
          dashed=False, color=INK_MUTED, lbl_color=INK_MUTED,
          lbl_size=10, lbl_style="italic", lw=1.4):
    ls = (0, (4, 3)) if dashed else "-"
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>,head_length=10,head_width=6.5",
        linewidth=lw, color=color, linestyle=ls,
        shrinkA=0, shrinkB=0, zorder=1, mutation_scale=1.0,
    ))
    if lbl:
        ax.text((x1 + x2) / 2 + lbl_off[0], (y1 + y2) / 2 + lbl_off[1],
                lbl, fontsize=lbl_size, color=lbl_color,
                ha="left", va="center", fontstyle=lbl_style, zorder=4)


def elbow(x1, y1, x2, y2, color=INK_MUTED, lw=1.4):
    """Vertical-then-horizontal connector with arrowhead at end."""
    verts = [(x1, y1), (x1, y2), (x2, y2)]
    codes = [MplPath.MOVETO, MplPath.LINETO, MplPath.LINETO]
    ax.add_patch(PathPatch(
        MplPath(verts, codes),
        facecolor="none", edgecolor=color, linewidth=lw, zorder=1,
        capstyle="round", joinstyle="round",
    ))
    # arrowhead at end (short overlay segment)
    sign = 1 if x2 > x1 else -1
    ax.add_patch(FancyArrowPatch(
        (x2 - sign * 0.05, y2), (x2, y2),
        arrowstyle="-|>,head_length=10,head_width=6.5",
        linewidth=lw, color=color, shrinkA=0, shrinkB=0, zorder=2,
    ))


# ============================================================
# STAGE 1 : Input
# ============================================================
INPUT_Y, INPUT_H, INPUT_W = 12.0, 1.05, 7.6
card(CX, INPUT_Y, INPUT_W, INPUT_H, "input")
title(CX, INPUT_Y + 0.22, "Conversation history", "input", size=14)
subtitle(CX, INPUT_Y - 0.22, "EN  ·  FR  ·  Franglais       1 to 28 turns",
         size=10.5)

# ============================================================
# STAGE 2 : mmBERT classifier
# ============================================================
CLF_Y, CLF_H, CLF_W = 10.0, 1.45, 7.6
card(CX, CLF_Y, CLF_W, CLF_H, "model")
title(CX, CLF_Y + 0.42, "mmBERT classifier", "model", size=14)
body(CX, CLF_Y + 0.03,
     "jhu-clsp/mmBERT-base, fine-tuned on 459 multi-turn conversations",
     size=10.5)
subtitle(CX, CLF_Y - 0.42, "~20 ms on GPU", size=10, style="italic")

arrow(CX, INPUT_Y - INPUT_H / 2, CX, CLF_Y + CLF_H / 2,
      lbl="full conversation thread", lbl_off=(0.18, 0))

# ============================================================
# STAGE 3 : Cohere LLM judge
# ============================================================
LLM_Y, LLM_H, LLM_W = 6.7, 3.1, 8.2
card(CX, LLM_Y, LLM_W, LLM_H, "model")
title(CX, LLM_Y + 1.25, "Cohere c4ai LLM judge", "model", size=14)
subtitle(CX, LLM_Y + 0.88,
         "CohereLabs/c4ai-command-a-03-2025      ~900 ms per call",
         size=10, style="italic")

# Section header
body(CX, LLM_Y + 0.48, "Chain-of-thought reasoning",
     size=11, weight="bold", color=PALETTE["model"]["accent"])

cot = [
    "1.  Opening intent",
    "2.  Escalation",
    "3.  Crisis signals",
    "4.  Vulnerability",
    "5.  Trajectory",
]
for i, line in enumerate(cot):
    body(CX, LLM_Y + 0.18 - i * 0.28, line, size=10.5, color=INK_BODY)

subtitle(CX, LLM_Y - 1.35,
         "Output:  JSON  (per-question reasoning  +  label  +  confidence)",
         size=10, style="italic")

arrow(CX, CLF_Y - CLF_H / 2, CX, LLM_Y + LLM_H / 2,
      lbl="risk score in [0, 1],  injected into prompt as primer",
      lbl_off=(0.18, 0))

# ============================================================
# STAGE 4 : Decision diamond
# ============================================================
DEC_CX, DEC_CY = CX, 3.6
DEC_W, DEC_H = 3.0, 1.55
p_dec = PALETTE["decision"]
# Shadow
diamond_shadow = Polygon(
    [(DEC_CX + 0.06, DEC_CY + DEC_H / 2 - 0.08),
     (DEC_CX + DEC_W / 2 + 0.06, DEC_CY - 0.08),
     (DEC_CX + 0.06, DEC_CY - DEC_H / 2 - 0.08),
     (DEC_CX - DEC_W / 2 + 0.06, DEC_CY - 0.08)],
    closed=True, facecolor="black", alpha=0.08, linewidth=0, zorder=1,
)
ax.add_patch(diamond_shadow)
diamond = Polygon(
    [(DEC_CX, DEC_CY + DEC_H / 2),
     (DEC_CX + DEC_W / 2, DEC_CY),
     (DEC_CX, DEC_CY - DEC_H / 2),
     (DEC_CX - DEC_W / 2, DEC_CY)],
    closed=True, facecolor=p_dec["fill"], edgecolor=p_dec["border"],
    linewidth=1.4, zorder=2,
)
ax.add_patch(diamond)
body(DEC_CX, DEC_CY + 0.18, "confidence", size=11.5, weight="bold",
     color=p_dec["accent"])
body(DEC_CX, DEC_CY - 0.18, ">=  0.45", size=13, weight="bold",
     color=p_dec["accent"])

arrow(CX, LLM_Y - LLM_H / 2, DEC_CX, DEC_CY + DEC_H / 2,
      lbl="confidence in [0, 1]", lbl_off=(0.18, 0))

# ============================================================
# STAGE 5 : Outcomes
# ============================================================
OUT_Y, OUT_W, OUT_H = 2.0, 2.5, 0.9
HI_CX, LO_CX = 3.4, 10.6

card(HI_CX, OUT_Y, OUT_W, OUT_H, "high")
title(HI_CX, OUT_Y, "high_risk", "high", size=14)

card(LO_CX, OUT_Y, OUT_W, OUT_H, "low")
title(LO_CX, OUT_Y, "low_risk", "low", size=14)

arrow(DEC_CX - DEC_W / 2, DEC_CY, HI_CX + OUT_W / 2, OUT_Y + OUT_H / 2,
      lbl="yes", lbl_off=(-0.35, 0.18), lbl_style="normal",
      lbl_color=INK_TITLE, lbl_size=11)
arrow(DEC_CX + DEC_W / 2, DEC_CY, LO_CX - OUT_W / 2, OUT_Y + OUT_H / 2,
      lbl="no", lbl_off=(0.18, 0.18), lbl_style="normal",
      lbl_color=INK_TITLE, lbl_size=11)

# ============================================================
# STAGE 6 : Human-in-the-loop
# ============================================================
HUM_Y, HUM_H, HUM_W = 0.4, 0.8, 9.0
card(CX, HUM_Y, HUM_W, HUM_H, "human")
body(CX, HUM_Y + 0.10, "Flag returned to VA layer",
     size=11.5, weight="bold", color=PALETTE["human"]["accent"])
body(CX, HUM_Y - 0.18, "KHP counsellor decides final escalation",
     size=10, color=INK_BODY, style="italic")

# Straight vertical drops from each outcome into the human-handoff bar.
# Both outcomes flag the VA layer; counsellor decides escalation either way.
arrow(HI_CX, OUT_Y - OUT_H / 2, HI_CX, HUM_Y + HUM_H / 2, color=INK_MUTED)
arrow(LO_CX, OUT_Y - OUT_H / 2, LO_CX, HUM_Y + HUM_H / 2, color=INK_MUTED)

# ============================================================
# SIDE : Fail-safe annotation (dashed border, visually secondary)
# ============================================================
FS_CX, FS_CY, FS_W, FS_H = 14.4, 6.7, 3.2, 2.0
card(FS_CX, FS_CY, FS_W, FS_H, "failsafe", dashed_border=True)
title(FS_CX, FS_CY + 0.65, "Fail-safe", "failsafe", size=12)
body(FS_CX, FS_CY + 0.28, "Any LLM error", size=10, color=INK_BODY)
body(FS_CX, FS_CY + 0.02, "(timeout, refusal,", size=9.5, color=INK_MUTED)
body(FS_CX, FS_CY - 0.22, "malformed JSON)", size=9.5, color=INK_MUTED)
body(FS_CX, FS_CY - 0.58, "defaults to", size=10, color=INK_BODY)
body(FS_CX, FS_CY - 0.85, "high_risk", size=11, weight="bold",
     color=PALETTE["high"]["accent"])

# Dashed connector from LLM judge right edge to fail-safe left edge
arrow(CX + LLM_W / 2, LLM_Y, FS_CX - FS_W / 2, FS_CY,
      dashed=True, color=PALETTE["failsafe"]["border"],
      lbl="on error", lbl_off=(0.0, 0.18),
      lbl_color=PALETTE["failsafe"]["accent"])

# ============================================================
# Footer
# ============================================================
ax.text(
    CANVAS_W / 2, -0.30,
    "The guardrail augments human judgment, never replaces it. "
    "All final escalation decisions remain with trained KHP counsellors.",
    ha="center", va="center", fontsize=9.5, color=INK_SUBTLE, style="italic",
)

plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.02)
plt.savefig(OUT, dpi=170, bbox_inches="tight", transparent=True, pad_inches=0.3)
print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
