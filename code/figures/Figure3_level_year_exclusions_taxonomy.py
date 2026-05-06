# -*- coding: utf-8 -*-
"""
GlobalGWDrought.Paper.2.Figure3.level_year_exclusions_taxonomy_v3.py

Paper 2 – Figure 3
Level–year exclusions and QC trigger taxonomy

Inputs:
    ./out_anomalies/station_flagged_years.csv

Outputs:
    ./out_paper2_figure_designs/Figure_3_HybridQC_level_year_exclusions_taxonomy_v3.png
    ./out_paper2_figure_designs/Figure_3_HybridQC_level_year_exclusions_taxonomy_v3.tif
    ./out_paper2_figure_designs/Figure_3_HybridQC_level_year_exclusions_taxonomy_v3.pdf
    ./out_paper2_figure_designs/Figure_3_HybridQC_level_year_exclusions_taxonomy_v3_caption.txt
    ./out_paper2_figure_designs/Figure_3_level_year_exclusions_by_year_v3.csv
    ./out_paper2_figure_designs/Figure_3_QC_trigger_taxonomy_counts_v3.csv
"""

from pathlib import Path as FilePath
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

BASE_DIR = FilePath(r"D:/PythonCodes/GlobalGWDrought")
if not BASE_DIR.exists():
    BASE_DIR = FilePath(__file__).resolve().parent

ANOM_DIR = BASE_DIR / "out_anomalies"
OUT_DIR = BASE_DIR / "out_paper2_figure_designs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FLAGGED_CSV = ANOM_DIR / "station_flagged_years.csv"

FIG_STEM = "Figure_3_HybridQC_level_year_exclusions_taxonomy_v3"

PNG_DPI = 400
TIFF_DPI = 600
PDF_DPI = 600

mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.linewidth": 0.8,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.04,
    "figure.facecolor": "white",
})

COLORS = {
    "robust_jump_year_level": "#6F8FB3",
    "spike_pair_year_level":  "#D98A8A",
    "cap_jump_year_level":    "#8FAE73",
    "frame": "#C7C7C7",
    "grid": "#E6E6E6",
    "text": "#26323C",
    "note_fill": "#FFFFFF",
}

LABELS = {
    "robust_jump_year_level": "Robust jump",
    "spike_pair_year_level":  "Spike pair",
    "cap_jump_year_level":    "Cap jump",
}

ORDER = [
    "robust_jump_year_level",
    "spike_pair_year_level",
    "cap_jump_year_level",
]

def human_int(x):
    return f"{int(x):,}"

def load_flagged(csv_path):
    if not csv_path.exists():
        raise FileNotFoundError(f"Could not find required input file in out_anomalies:\n  {csv_path}")
    df = pd.read_csv(csv_path)
    required = {"StnID", "Year", "Reason"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"station_flagged_years.csv is missing required columns: {sorted(missing)}")
    return df

def main():
    print("Loading level-year exclusion table...")
    df = load_flagged(FLAGGED_CSV)

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Reason"] = df["Reason"].astype(str)
    df = df.dropna(subset=["Year", "Reason"]).copy()
    df["Year"] = df["Year"].astype(int)
    df = df[df["Reason"].str.len() > 0].copy()

    total_flagged = len(df)
    unique_stations = df["StnID"].nunique()
    year_min = int(df["Year"].min())
    year_max = int(df["Year"].max())

    annual = (
        df.groupby(["Year", "Reason"])
          .size()
          .rename("n")
          .reset_index()
          .pivot(index="Year", columns="Reason", values="n")
          .fillna(0)
    )
    for r in ORDER:
        if r not in annual.columns:
            annual[r] = 0
    annual = annual[ORDER].sort_index()

    annual_csv = annual.reset_index().rename(columns={r: LABELS[r] for r in ORDER})
    annual_csv_path = OUT_DIR / "Figure_3_level_year_exclusions_by_year_v3.csv"
    annual_csv.to_csv(annual_csv_path, index=False)

    tax = (
        df["Reason"].value_counts()
        .rename_axis("Reason")
        .reset_index(name="Count")
    )
    tax["Percent"] = 100.0 * tax["Count"] / total_flagged
    tax["Label"] = tax["Reason"].map(LABELS).fillna(tax["Reason"])
    tax["order"] = tax["Reason"].map({r: i for i, r in enumerate(ORDER)})
    tax = tax.sort_values(["order", "Count"], ascending=[True, False]).drop(columns="order").reset_index(drop=True)
    tax_csv_path = OUT_DIR / "Figure_3_QC_trigger_taxonomy_counts_v3.csv"
    tax.to_csv(tax_csv_path, index=False)

    fig = plt.figure(figsize=(14.4, 6.6))
    ax1 = fig.add_axes([0.06, 0.14, 0.60, 0.77])
    ax2 = fig.add_axes([0.73, 0.20, 0.24, 0.68])

    years = annual.index.values
    bottom = np.zeros(len(years), dtype=float)

    for r in ORDER:
        vals = annual[r].values.astype(float)
        ax1.bar(
            years, vals, bottom=bottom, width=0.9,
            color=COLORS[r], edgecolor="none",
            label=LABELS[r], zorder=3
        )
        bottom += vals

    ax1.set_xlim(year_min - 1, year_max + 1)
    ax1.set_ylabel("Flagged level-years")
    ax1.set_xlabel("Year")
    start_tick = int(np.floor(year_min / 20.0) * 20)
    ticks = np.arange(start_tick, year_max + 21, 20)
    ax1.set_xticks(ticks)
    ax1.grid(axis="y", color=COLORS["grid"], linewidth=0.6, zorder=0)

    for spine in ax1.spines.values():
        spine.set_color(COLORS["frame"])
        spine.set_linewidth(0.8)

    ax1.text(0.0, 1.02, "(a)", transform=ax1.transAxes,
             ha="left", va="bottom", fontsize=12, fontweight="bold", color=COLORS["text"])

    leg = ax1.legend(
        loc="upper left",
        bbox_to_anchor=(0.015, 0.985),
        frameon=True,
        fontsize=9.2,
        borderpad=0.4,
        handlelength=1.4
    )
    leg.get_frame().set_facecolor("white")
    leg.get_frame().set_edgecolor(COLORS["frame"])
    leg.get_frame().set_linewidth(0.8)

    # Narrower and lower summary note box, clearly below legend
    note_x, note_y = 0.018, 0.50
    note_w, note_h = 0.205, 0.115
    rect = FancyBboxPatch(
        (note_x, note_y), note_w, note_h,
        transform=ax1.transAxes,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        facecolor=COLORS["note_fill"],
        edgecolor=COLORS["frame"],
        linewidth=0.8,
        alpha=0.98,
        zorder=4
    )
    ax1.add_patch(rect)
    ax1.text(
        note_x + 0.013, note_y + note_h - 0.016,
        f"Total flagged: {human_int(total_flagged)}\n"
        f"Flagged stations: {human_int(unique_stations)}\n"
        f"Years with flags: {year_min}–{year_max}",
        transform=ax1.transAxes,
        ha="left", va="top",
        fontsize=8.8,
        color=COLORS["text"],
        zorder=5
    )

    y = np.arange(len(tax))
    counts = tax["Count"].values
    labels = tax["Label"].values
    bar_colors = [COLORS.get(r, "#999999") for r in tax["Reason"]]

    ax2.barh(
        y, counts,
        color=bar_colors,
        edgecolor="none",
        height=0.58,
        zorder=3
    )
    ax2.set_yticks(y)
    ax2.set_yticklabels(labels)
    ax2.invert_yaxis()
    ax2.set_xlabel("Flagged level-years")
    ax2.grid(axis="x", color=COLORS["grid"], linewidth=0.6, zorder=0)
    for spine in ax2.spines.values():
        spine.set_color(COLORS["frame"])
        spine.set_linewidth(0.8)

    xmax = counts.max() * 1.22
    ax2.set_xlim(0, xmax)

    for i, (_, row) in enumerate(tax.iterrows()):
        ax2.text(
            row["Count"] + xmax * 0.02, i,
            f'{human_int(row["Count"])} ({row["Percent"]:.1f}%)',
            va="center", ha="left",
            fontsize=9.2, color=COLORS["text"]
        )

    ax2.text(0.0, 1.02, "(b)", transform=ax2.transAxes,
             ha="left", va="bottom", fontsize=12, fontweight="bold", color=COLORS["text"])

    png_path = OUT_DIR / f"{FIG_STEM}.png"
    tif_path = OUT_DIR / f"{FIG_STEM}.tif"
    pdf_path = OUT_DIR / f"{FIG_STEM}.pdf"
    cap_path = OUT_DIR / f"{FIG_STEM}_caption.txt"

    fig.savefig(png_path, dpi=PNG_DPI)
    fig.savefig(tif_path, dpi=TIFF_DPI)
    fig.savefig(pdf_path, dpi=PDF_DPI)
    plt.close(fig)

    caption = (
        "Figure 3. Level–year exclusions and QC trigger taxonomy. "
        "(a) Annual counts of level–year exclusions recorded by HybridQC, shown as stacked bars by trigger class. "
        "(b) Aggregate trigger taxonomy across all flagged level-years. In the present dataset, 1,420 level-years "
        "were excluded at 1,327 stations, dominated by robust-jump triggers (852; 60.0%), followed by spike-pair "
        "triggers (482; 33.9%) and cap-jump triggers (86; 6.1%)."
    )
    cap_path.write_text(caption, encoding="utf-8")

    print("Saved:")
    print(png_path)
    print(tif_path)
    print(pdf_path)
    print(cap_path)
    print(annual_csv_path)
    print(tax_csv_path)

if __name__ == "__main__":
    main()
