# -*- coding: utf-8 -*-
"""
GlobalGWDrought.Paper.2.Figure1.v9.workflow_diagram.py

Fixes:
- resolves the Path name collision between pathlib.Path and matplotlib.path.Path
- keeps curved 90-degree orthogonal connectors
- saves outputs to ./out_paper2_figure_designs/
"""

from pathlib import Path as FilePath
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, PathPatch
from matplotlib.path import Path as MplPath
import numpy as np

# =========================================================
# User settings
# =========================================================
BASE_DIR = FilePath(r"D:/PythonCodes/GlobalGWDrought")
if not BASE_DIR.exists():
    BASE_DIR = FilePath(__file__).resolve().parent

OUT_DIR = BASE_DIR / "out_paper2_figure_designs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FIG_STEM = "Figure_1_HybridQC_workflow_diagram_v9"

PNG_DPI = 400
TIFF_DPI = 600
PDF_DPI = 600

# =========================================================
# Style
# =========================================================
mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.linewidth": 0.8,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.035,
    "figure.facecolor": "white",
})

COL = {
    "main_fill":      "#DDE7F4",
    "main_edge":      "#355F96",
    "contract_fill":  "#E8E0F4",
    "contract_edge":  "#6C58A7",
    "audit_fill":     "#FAE5D8",
    "audit_edge":     "#C56C42",
    "meta_fill":      "#E4F0D8",
    "meta_edge":      "#4E7C3A",
    "reuse_fill":     "#F4E8BF",
    "reuse_edge":     "#B18211",
    "output_fill":    "#D9EEE8",
    "output_edge":    "#2F8B81",
    "wire_main":      "#4A70A2",
    "wire_contract":  "#6D59A8",
    "wire_audit":     "#C56C42",
    "wire_out":       "#5B8546",
    "text":           "#24313C",
}

fig = plt.figure(figsize=(16.4, 9.0))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")


# =========================================================
# Helpers
# =========================================================
def draw_box(ax, x, y, w, h, text, fc, ec, fontsize=11, weight="normal", lw=1.8):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.016",
        linewidth=lw, edgecolor=ec, facecolor=fc
    )
    ax.add_patch(patch)
    ax.text(
        x + w/2, y + h/2, text,
        ha="center", va="center",
        fontsize=fontsize, fontweight=weight,
        color=COL["text"], linespacing=1.16
    )
    return {"x": x, "y": y, "w": w, "h": h}

def left_mid(b):   return (b["x"], b["y"] + b["h"]/2)
def right_mid(b):  return (b["x"] + b["w"], b["y"] + b["h"]/2)
def top_mid(b):    return (b["x"] + b["w"]/2, b["y"] + b["h"])
def bot_mid(b):    return (b["x"] + b["w"]/2, b["y"])

def _unit(v):
    n = np.hypot(v[0], v[1])
    if n == 0:
        return np.array([0.0, 0.0])
    return np.array(v) / n

def rounded_ortho_arrow(ax, pts, color, lw=2.0, radius=0.018, arrow_ms=14):
    """
    Draw a polyline with orthogonal segments and rounded 90° corners.
    pts: list of (x, y) control points; consecutive segments must be horizontal/vertical.
    The arrowhead is added on the final segment and ends exactly at pts[-1].
    """
    pts = [np.array(p, dtype=float) for p in pts]
    verts = [tuple(pts[0])]
    codes = [MplPath.MOVETO]

    for i in range(1, len(pts) - 1):
        p_prev = pts[i - 1]
        p = pts[i]
        p_next = pts[i + 1]

        v_in = p - p_prev
        v_out = p_next - p
        u_in = _unit(v_in)
        u_out = _unit(v_out)

        if np.allclose(u_in, u_out) or np.allclose(u_in, -u_out):
            verts.append(tuple(p))
            codes.append(MplPath.LINETO)
            continue

        r = min(radius, np.hypot(*(p - p_prev)) / 2.5, np.hypot(*(p_next - p)) / 2.5)
        p1 = p - u_in * r
        p2 = p + u_out * r

        verts.append(tuple(p1))
        codes.append(MplPath.LINETO)
        verts.append(tuple(p))
        codes.append(MplPath.CURVE3)
        verts.append(tuple(p2))
        codes.append(MplPath.CURVE3)

    verts.append(tuple(pts[-1]))
    codes.append(MplPath.LINETO)

    path = MplPath(verts, codes)
    patch = PathPatch(path, facecolor="none", edgecolor=color, lw=lw,
                      capstyle="round", joinstyle="round")
    ax.add_patch(patch)

    pA = pts[-2]
    pB = pts[-1]
    arr = FancyArrowPatch(
        pA, pB,
        arrowstyle="-|>",
        mutation_scale=arrow_ms,
        linewidth=lw,
        color=color,
        shrinkA=0, shrinkB=0,
        connectionstyle="arc3,rad=0"
    )
    ax.add_patch(arr)


# =========================================================
# Symmetric grid layout
# =========================================================
c1, c2, c3, c4, c5 = 0.04, 0.24, 0.44, 0.64, 0.84
y1 = 0.83
y2 = 0.65
y3 = 0.45
y4 = 0.25
y5 = 0.06
h = 0.075

b_input = draw_box(ax, c1, y1, 0.15, h, "Input archive\nannual groundwater observations",
                   COL["main_fill"], COL["main_edge"], fontsize=11.6)
b_harm  = draw_box(ax, c2, y1, 0.15, h, "Minimal harmonization\nto wetness-like annual level",
                   COL["main_fill"], COL["main_edge"], fontsize=11.4)
b_anom  = draw_box(ax, c3, y1, 0.17, h, "Strict consecutive-year\nanomaly construction\n(no gap infilling)",
                   COL["main_fill"], COL["main_edge"], fontsize=11.2)
b_qc    = draw_box(ax, c5, y1, 0.10, h, "Level–year QC",
                   COL["main_fill"], COL["main_edge"], fontsize=12.0, weight="bold")

b_contract = draw_box(ax, 0.60, y2, 0.22, h, "Fixed anomaly contract\nstation_anomalies_all.csv",
                      COL["contract_fill"], COL["contract_edge"], fontsize=12.0, weight="bold")

b_excl   = draw_box(ax, c1, y3, 0.16, h, "Exclusion ledger\nstation_flagged_years.csv",
                    COL["audit_fill"], COL["audit_edge"], fontsize=10.8)
b_insp   = draw_box(ax, c2, y3, 0.17, h, "Retained extremes\nglobal_outlier_anomalies.csv",
                    COL["audit_fill"], COL["audit_edge"], fontsize=10.8)
b_range  = draw_box(ax, c4, y3, 0.16, h, "Annual range metadata\nannual_max_min_anomalies.csv",
                    COL["meta_fill"], COL["meta_edge"], fontsize=10.6)
b_decad  = draw_box(ax, c5, y3, 0.10, h, "Decadal summaries\nstation_decadal_stats.csv",
                    COL["meta_fill"], COL["meta_edge"], fontsize=10.1)

b_reuse = draw_box(ax, 0.31, y4, 0.34, h, "Deterministic downstream reuse",
                   COL["reuse_fill"], COL["reuse_edge"], fontsize=14.0, weight="bold", lw=2.0)

b_join = draw_box(ax, c1, y5, 0.18, h, "Joins and derived tables\n(aquifer links, summaries)",
                  COL["output_fill"], COL["output_edge"], fontsize=10.4)
b_diag = draw_box(ax, 0.40, y5, 0.18, h, "Diagnostic products\n(QC diagnostics, inspection products)",
                  COL["output_fill"], COL["output_edge"], fontsize=10.2)
b_map  = draw_box(ax, 0.70, y5, 0.18, h, "Mapped and manuscript outputs\n(figures, publication-ready tables)",
                  COL["output_fill"], COL["output_edge"], fontsize=10.0)

# =========================================================
# Bus / trunk levels
# =========================================================
y_bus_qc_to_contract = 0.77
y_bus_qc_branch = 0.585
y_bus_contract_branch = 0.545
y_bus_to_reuse_1 = 0.355
y_bus_to_reuse_2 = 0.335
y_bus_to_reuse_3 = 0.315
y_bus_from_reuse_1 = 0.185
y_bus_from_reuse_2 = 0.165
y_bus_from_reuse_3 = 0.145

# =========================================================
# Connections
# =========================================================
rounded_ortho_arrow(ax, [
    right_mid(b_input),
    (b_harm["x"] - 0.03, right_mid(b_input)[1]),
    left_mid(b_harm)
], COL["wire_main"], lw=2.2, radius=0.014)

rounded_ortho_arrow(ax, [
    right_mid(b_harm),
    (b_anom["x"] - 0.03, right_mid(b_harm)[1]),
    left_mid(b_anom)
], COL["wire_main"], lw=2.2, radius=0.014)

rounded_ortho_arrow(ax, [
    right_mid(b_anom),
    (b_qc["x"] - 0.03, right_mid(b_anom)[1]),
    left_mid(b_qc)
], COL["wire_main"], lw=2.2, radius=0.014)

qc_b = bot_mid(b_qc)
contract_t = top_mid(b_contract)
rounded_ortho_arrow(ax, [
    qc_b,
    (qc_b[0], y_bus_qc_to_contract),
    (contract_t[0], y_bus_qc_to_contract),
    contract_t
], COL["wire_contract"], lw=2.0, radius=0.017)

for tgt_box, clr in [(b_excl, COL["wire_audit"]), (b_insp, COL["wire_audit"]), (b_range, COL["wire_audit"])]:
    tgt = top_mid(tgt_box)
    rounded_ortho_arrow(ax, [
        qc_b,
        (qc_b[0], y_bus_qc_branch),
        (tgt[0], y_bus_qc_branch),
        tgt
    ], clr, lw=1.85, radius=0.017)

contract_b = bot_mid(b_contract)
for tgt_box in [b_range, b_decad]:
    tgt = top_mid(tgt_box)
    rounded_ortho_arrow(ax, [
        contract_b,
        (contract_b[0], y_bus_contract_branch),
        (tgt[0], y_bus_contract_branch),
        tgt
    ], COL["wire_contract"], lw=1.8, radius=0.016)

reuse_t = top_mid(b_reuse)
for src_box, ybus in [(b_insp, y_bus_to_reuse_1), (b_range, y_bus_to_reuse_2), (b_decad, y_bus_to_reuse_3)]:
    src = bot_mid(src_box)
    x_in = src[0] if src_box is b_insp else (reuse_t[0] - 0.07 if src_box is b_range else reuse_t[0] + 0.07)
    rounded_ortho_arrow(ax, [
        src,
        (src[0], ybus),
        (x_in, ybus),
        (x_in, reuse_t[1]),
        (x_in, reuse_t[1])
    ], COL["wire_out"], lw=1.82, radius=0.016)

reuse_b = bot_mid(b_reuse)
for tgt_box, ybus in [(b_join, y_bus_from_reuse_1), (b_diag, y_bus_from_reuse_2), (b_map, y_bus_from_reuse_3)]:
    tgt = top_mid(tgt_box)
    rounded_ortho_arrow(ax, [
        reuse_b,
        (reuse_b[0], ybus),
        (tgt[0], ybus),
        tgt
    ], COL["wire_out"], lw=1.82, radius=0.016)

# =========================================================
# Save
# =========================================================
png_path = OUT_DIR / f"{FIG_STEM}.png"
tif_path = OUT_DIR / f"{FIG_STEM}.tif"
pdf_path = OUT_DIR / f"{FIG_STEM}.pdf"
svg_path = OUT_DIR / f"{FIG_STEM}.svg"
cap_path = OUT_DIR / f"{FIG_STEM}_caption.txt"

fig.savefig(png_path, dpi=PNG_DPI)
fig.savefig(tif_path, dpi=TIFF_DPI)
fig.savefig(pdf_path, dpi=PDF_DPI)
fig.savefig(svg_path)
plt.close(fig)

caption = (
    "Figure 1. HybridQC workflow and output lineage. The diagram summarizes the HybridQC "
    "architecture from heterogeneous annual groundwater observations through minimal harmonization, "
    "strict consecutive-year anomaly construction, and level–year quality control. The workflow then "
    "separates destructive exclusion (station_flagged_years.csv) from non-destructive inspection of "
    "retained extremes (global_outlier_anomalies.csv), externalizes annual range metadata "
    "(annual_max_min_anomalies.csv), generates decadal summaries (station_decadal_stats.csv), and "
    "supports joins, diagnostics, maps, and publication-ready outputs through a fixed anomaly contract "
    "(station_anomalies_all.csv) and deterministic downstream reuse."
)
cap_path.write_text(caption, encoding="utf-8")

print("Saved:")
print(png_path)
print(tif_path)
print(pdf_path)
print(svg_path)
print(cap_path)
