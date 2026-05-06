# -*- coding: utf-8 -*-
"""
GlobalGWDrought.Paper.2.Figure4.retained_global_outlier_anomalies_v2.py

Paper 2 – Figure 4
Retained global outlier anomalies (non-destructive inspection product)

Inputs:
    ./out_anomalies/global_outlier_anomalies.csv

Outputs:
    ./out_paper2_figure_designs/Figure_4_HybridQC_retained_global_outlier_anomalies_v2.png
    ./out_paper2_figure_designs/Figure_4_HybridQC_retained_global_outlier_anomalies_v2.tif
    ./out_paper2_figure_designs/Figure_4_HybridQC_retained_global_outlier_anomalies_v2.pdf
    ./out_paper2_figure_designs/Figure_4_HybridQC_retained_global_outlier_anomalies_v2_caption.txt
    ./out_paper2_figure_designs/Figure_4_retained_outlier_annual_counts_v2.csv
    ./out_paper2_figure_designs/Figure_4_retained_outlier_summary_v2.csv
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

OUTLIER_CSV = ANOM_DIR / "global_outlier_anomalies.csv"

FIG_STEM = "Figure_4_HybridQC_retained_global_outlier_anomalies_v2"

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
    "negative": "#D98A8A",
    "positive": "#7FA3C8",
    "frame": "#C7C7C7",
    "grid": "#E6E6E6",
    "text": "#26323C",
    "note_fill": "#FFFFFF",
}

def human_int(x):
    return f"{int(x):,}"

def load_outliers(csv_path):
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Could not find required input file in out_anomalies:\n  {csv_path}"
        )
    df = pd.read_csv(csv_path)
    required = {"StnID", "Year", "Anomaly"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"global_outlier_anomalies.csv is missing required columns: {sorted(missing)}")
    return df

def main():
    print("Loading retained outlier table...")
    df = load_outliers(OUTLIER_CSV)

    keep_cols = [c for c in ["StnID", "Year", "Lat", "Lon", "Anomaly", "SourceType"] if c in df.columns]
    df = df[keep_cols].copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Anomaly"] = pd.to_numeric(df["Anomaly"], errors="coerce")
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=["StnID", "Year", "Anomaly"]).copy()
    df["Year"] = df["Year"].astype(int)

    df["Sign"] = np.where(df["Anomaly"] < 0, "Negative", "Positive")
    df = df[df["Anomaly"] != 0].copy()

    total_outliers = len(df)
    n_stations = df["StnID"].nunique()
    year_min = int(df["Year"].min())
    year_max = int(df["Year"].max())

    neg = df[df["Sign"] == "Negative"].copy()
    pos = df[df["Sign"] == "Positive"].copy()

    annual = (
        df.groupby(["Year", "Sign"])
          .size()
          .rename("n")
          .reset_index()
          .pivot(index="Year", columns="Sign", values="n")
          .fillna(0)
    )
    for c in ["Negative", "Positive"]:
        if c not in annual.columns:
            annual[c] = 0
    annual = annual[["Negative", "Positive"]].sort_index()
    annual_csv_path = OUT_DIR / "Figure_4_retained_outlier_annual_counts_v2.csv"
    annual.reset_index().to_csv(annual_csv_path, index=False)

    summary = pd.DataFrame({
        "Metric": [
            "Total retained outlier anomalies",
            "Stations with >=1 retained outlier anomaly",
            "Year minimum",
            "Year maximum",
            "Negative retained outlier anomalies",
            "Positive retained outlier anomalies",
            "Median negative anomaly",
            "Median positive anomaly",
            "Minimum anomaly",
            "Maximum anomaly",
        ],
        "Value": [
            total_outliers,
            n_stations,
            year_min,
            year_max,
            len(neg),
            len(pos),
            round(float(neg["Anomaly"].median()), 3) if len(neg) else np.nan,
            round(float(pos["Anomaly"].median()), 3) if len(pos) else np.nan,
            round(float(df["Anomaly"].min()), 3),
            round(float(df["Anomaly"].max()), 3),
        ]
    })
    summary_csv_path = OUT_DIR / "Figure_4_retained_outlier_summary_v2.csv"
    summary.to_csv(summary_csv_path, index=False)

    fig = plt.figure(figsize=(14.2, 6.4))
    ax1 = fig.add_axes([0.07, 0.14, 0.56, 0.76])
    ax2 = fig.add_axes([0.70, 0.14, 0.25, 0.76])

    years = annual.index.values
    neg_counts = annual["Negative"].values.astype(float)
    pos_counts = annual["Positive"].values.astype(float)

    ax1.bar(years, neg_counts, width=0.9, color=COLORS["negative"], edgecolor="none", label="Negative", zorder=3)
    ax1.bar(years, pos_counts, bottom=neg_counts, width=0.9, color=COLORS["positive"], edgecolor="none", label="Positive", zorder=3)

    ax1.set_xlim(year_min - 1, year_max + 1)
    ax1.set_ylabel("Retained outlier anomalies")
    ax1.set_xlabel("Year")
    start_tick = int(np.floor(year_min / 20.0) * 20)
    ax1.set_xticks(np.arange(start_tick, year_max + 21, 20))
    ax1.grid(axis="y", color=COLORS["grid"], linewidth=0.6, zorder=0)

    for spine in ax1.spines.values():
        spine.set_color(COLORS["frame"])
        spine.set_linewidth(0.8)

    ax1.text(0.0, 1.02, "(a)", transform=ax1.transAxes,
             ha="left", va="bottom", fontsize=12, fontweight="bold", color=COLORS["text"])

    leg = ax1.legend(loc="upper left", frameon=True, fontsize=9.2, borderpad=0.4, handlelength=1.4)
    leg.get_frame().set_facecolor("white")
    leg.get_frame().set_edgecolor(COLORS["frame"])
    leg.get_frame().set_linewidth(0.8)

    # narrowed and moved slightly lower
    note_x, note_y = 0.015, 0.70
    note_w, note_h = 0.235, 0.145
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
        f"Total retained: {human_int(total_outliers)}\n"
        f"Stations: {human_int(n_stations)}\n"
        f"Negative: {human_int(len(neg))}\n"
        f"Positive: {human_int(len(pos))}",
        transform=ax1.transAxes,
        ha="left", va="top",
        fontsize=8.9,
        color=COLORS["text"],
        zorder=5
    )

    bins = np.arange(-100, 105, 5)
    ax2.hist(neg["Anomaly"].values, bins=bins, color=COLORS["negative"], alpha=0.85,
             edgecolor="white", linewidth=0.25, label="Negative", zorder=3)
    ax2.hist(pos["Anomaly"].values, bins=bins, color=COLORS["positive"], alpha=0.85,
             edgecolor="white", linewidth=0.25, label="Positive", zorder=3)
    ax2.axvline(0, color=COLORS["frame"], linewidth=0.9, zorder=2)

    ax2.set_xlabel("Retained anomaly value")
    ax2.set_ylabel("Frequency")
    ax2.grid(axis="y", color=COLORS["grid"], linewidth=0.6, zorder=0)
    for spine in ax2.spines.values():
        spine.set_color(COLORS["frame"])
        spine.set_linewidth(0.8)

    ax2.text(0.0, 1.02, "(b)", transform=ax2.transAxes,
             ha="left", va="bottom", fontsize=12, fontweight="bold", color=COLORS["text"])

    med_neg = float(neg["Anomaly"].median()) if len(neg) else np.nan
    med_pos = float(pos["Anomaly"].median()) if len(pos) else np.nan
    txt = (
        f"Median negative: {med_neg:.2f}\n"
        f"Median positive: {med_pos:.2f}\n"
        f"Range: {df['Anomaly'].min():.2f} to {df['Anomaly'].max():.2f}"
    )
    ax2.text(
        0.98, 0.97, txt,
        transform=ax2.transAxes,
        ha="right", va="top",
        fontsize=8.9, color=COLORS["text"],
        bbox=dict(boxstyle="round,pad=0.28", facecolor="white",
                  edgecolor=COLORS["frame"], linewidth=0.8)
    )

    png_path = OUT_DIR / f"{FIG_STEM}.png"
    tif_path = OUT_DIR / f"{FIG_STEM}.tif"
    pdf_path = OUT_DIR / f"{FIG_STEM}.pdf"
    cap_path = OUT_DIR / f"{FIG_STEM}_caption.txt"

    fig.savefig(png_path, dpi=PNG_DPI)
    fig.savefig(tif_path, dpi=TIFF_DPI)
    fig.savefig(pdf_path, dpi=PDF_DPI)
    plt.close(fig)

    caption = (
        "Figure 4. Retained global outlier anomalies as a non-destructive inspection product. "
        "(a) Annual counts of retained outlier anomalies separated by sign. "
        "(b) Frequency distribution of retained anomaly values. The retained outlier table contains "
        "2,885 anomalies at 1,760 stations spanning 1906–2022, with near-balanced negative "
        "(1,435) and positive (1,450) extremes. Rather than removing these records, HybridQC "
        "externalizes them as a separate inspection layer to preserve anomaly lineage while allowing "
        "downstream analyses to proceed from a stable anomaly contract."
    )
    cap_path.write_text(caption, encoding="utf-8")

    print("Saved:")
    print(png_path)
    print(tif_path)
    print(pdf_path)
    print(cap_path)
    print(annual_csv_path)
    print(summary_csv_path)

if __name__ == "__main__":
    main()
