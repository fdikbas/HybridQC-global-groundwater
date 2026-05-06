# -*- coding: utf-8 -*-
"""
GlobalGWDrought.Paper.2.Figure5.anomaly_range_and_support_by_region.py

Paper 2 – Figure 5
Annual anomaly range metadata and temporal support by region

Inputs:
    ./out_anomalies/annual_max_min_anomalies.csv

Outputs:
    ./out_paper2_figure_designs/Figure_5_HybridQC_anomaly_range_and_support_by_region.png
    ./out_paper2_figure_designs/Figure_5_HybridQC_anomaly_range_and_support_by_region.tif
    ./out_paper2_figure_designs/Figure_5_HybridQC_anomaly_range_and_support_by_region.pdf
    ./out_paper2_figure_designs/Figure_5_HybridQC_anomaly_range_and_support_by_region_caption.txt
    ./out_paper2_figure_designs/Figure_5_annual_anomaly_range_metadata_by_region.csv
"""

from pathlib import Path as FilePath
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

# =========================================================
# User settings
# =========================================================
BASE_DIR = FilePath(r"D:/PythonCodes/GlobalGWDrought")
if not BASE_DIR.exists():
    BASE_DIR = FilePath(__file__).resolve().parent

ANOM_DIR = BASE_DIR / "out_anomalies"
OUT_DIR = BASE_DIR / "out_paper2_figure_designs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

RANGE_CSV = ANOM_DIR / "annual_max_min_anomalies.csv"

FIG_STEM = "Figure_5_HybridQC_anomaly_range_and_support_by_region"

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

COL = {
    "global_fill": "#9AB6CF",
    "global_line": "#587A9A",
    "us_fill": "#D8A4A1",
    "us_line": "#B0716B",
    "eu_fill": "#B8CEA1",
    "eu_line": "#7D9B63",
    "support_global": "#587A9A",
    "support_us": "#B0716B",
    "support_eu": "#7D9B63",
    "grid": "#E6E6E6",
    "frame": "#C7C7C7",
    "text": "#26323C",
    "zero": "#9E9E9E",
}

REGION_ORDER = ["global", "US", "Europe"]
REGION_LABELS = {"global": "Global", "US": "US", "Europe": "Europe"}
FILL = {"global": COL["global_fill"], "US": COL["us_fill"], "Europe": COL["eu_fill"]}
LINE = {"global": COL["global_line"], "US": COL["us_line"], "Europe": COL["eu_line"]}


def load_range_table(path):
    if not path.exists():
        raise FileNotFoundError(f"Could not find required input file:\n  {path}")
    df = pd.read_csv(path)
    required = {"Region", "Year", "data_min", "data_max", "n_total"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"annual_max_min_anomalies.csv missing required columns: {sorted(missing)}")
    return df


def prepare(df):
    keep = ["Region", "Year", "data_min", "data_max", "n_total", "n_plotted"]
    keep = [c for c in keep if c in df.columns]
    df = df[keep].copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["data_min"] = pd.to_numeric(df["data_min"], errors="coerce")
    df["data_max"] = pd.to_numeric(df["data_max"], errors="coerce")
    df["n_total"] = pd.to_numeric(df["n_total"], errors="coerce")
    if "n_plotted" in df.columns:
        df["n_plotted"] = pd.to_numeric(df["n_plotted"], errors="coerce")
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=["Region", "Year", "data_min", "data_max", "n_total"]).copy()
    df["Year"] = df["Year"].astype(int)
    return df


def prettify_axis(ax):
    ax.grid(axis="y", color=COL["grid"], linewidth=0.6, zorder=0)
    for s in ax.spines.values():
        s.set_color(COL["frame"])
        s.set_linewidth(0.8)


def main():
    print("Loading annual range metadata...")
    df = prepare(load_range_table(RANGE_CSV))

    df = df[df["Region"].isin(REGION_ORDER)].copy()
    if df.empty:
        raise ValueError("No supported regions found. Expected one or more of: global, US, Europe")

    # Save cleaned table
    out_csv = OUT_DIR / "Figure_5_annual_anomaly_range_metadata_by_region.csv"
    df.sort_values(["Region", "Year"]).to_csv(out_csv, index=False)

    years_all = sorted(df["Year"].unique())
    year_min, year_max = min(years_all), max(years_all)

    # Determine common y-range across range panels
    ymin = float(df["data_min"].min())
    ymax = float(df["data_max"].max())
    pad = 0.05 * max(abs(ymin), abs(ymax), 1.0)
    ymin_plot = ymin - pad
    ymax_plot = ymax + pad

    fig = plt.figure(figsize=(13.8, 9.0))
    ax_g = fig.add_axes([0.08, 0.70, 0.84, 0.20])
    ax_u = fig.add_axes([0.08, 0.44, 0.84, 0.20])
    ax_e = fig.add_axes([0.08, 0.18, 0.84, 0.20])
    ax_s = fig.add_axes([0.08, 0.04, 0.84, 0.10])

    axes = [ax_g, ax_u, ax_e]

    for ax, region, panel in zip(axes, REGION_ORDER, ["(a)", "(b)", "(c)"]):
        sub = df[df["Region"] == region].sort_values("Year").copy()
        x = sub["Year"].values
        ylo = sub["data_min"].values
        yhi = sub["data_max"].values

        ax.fill_between(x, ylo, yhi, color=FILL[region], alpha=0.65, linewidth=0, zorder=2)
        ax.plot(x, ylo, color=LINE[region], linewidth=1.1, zorder=3)
        ax.plot(x, yhi, color=LINE[region], linewidth=1.1, zorder=3)
        ax.axhline(0, color=COL["zero"], linewidth=0.8, zorder=1)

        ax.set_xlim(year_min, year_max)
        ax.set_ylim(ymin_plot, ymax_plot)
        ax.set_ylabel("Anomaly")
        prettify_axis(ax)

        ax.text(0.0, 1.02, panel, transform=ax.transAxes,
                ha="left", va="bottom", fontsize=12, fontweight="bold", color=COL["text"])
        ax.text(0.055, 1.02, REGION_LABELS[region], transform=ax.transAxes,
                ha="left", va="bottom", fontsize=11, color=COL["text"])

        if ax is not ax_e:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel("Year")

    # Support counts panel
    for region in REGION_ORDER:
        sub = df[df["Region"] == region].sort_values("Year").copy()
        ax_s.plot(
            sub["Year"].values, sub["n_total"].values,
            linewidth=1.6,
            color=LINE[region],
            label=REGION_LABELS[region],
            zorder=3
        )

    ax_s.set_xlim(year_min, year_max)
    ax_s.set_ylabel("n_total")
    ax_s.set_xlabel("Year")
    prettify_axis(ax_s)
    ax_s.text(0.0, 1.02, "(d)", transform=ax_s.transAxes,
              ha="left", va="bottom", fontsize=12, fontweight="bold", color=COL["text"])

    leg = ax_s.legend(loc="upper left", ncol=3, frameon=True, fontsize=9.1,
                      borderpad=0.35, handlelength=2.0, columnspacing=1.2)
    leg.get_frame().set_facecolor("white")
    leg.get_frame().set_edgecolor(COL["frame"])
    leg.get_frame().set_linewidth(0.8)

    # x ticks
    xt = np.arange(int(np.floor(year_min / 20.0) * 20), year_max + 21, 20)
    for ax in axes + [ax_s]:
        ax.set_xticks(xt)

    # Save
    png_path = OUT_DIR / f"{FIG_STEM}.png"
    tif_path = OUT_DIR / f"{FIG_STEM}.tif"
    pdf_path = OUT_DIR / f"{FIG_STEM}.pdf"
    cap_path = OUT_DIR / f"{FIG_STEM}_caption.txt"

    fig.savefig(png_path, dpi=PNG_DPI)
    fig.savefig(tif_path, dpi=TIFF_DPI)
    fig.savefig(pdf_path, dpi=PDF_DPI)
    plt.close(fig)

    # Summary stats for caption context
    stats = []
    for region in REGION_ORDER:
        sub = df[df["Region"] == region]
        if len(sub) == 0:
            continue
        stats.append(
            f"{REGION_LABELS[region]}: {int(sub['Year'].min())}–{int(sub['Year'].max())}, "
            f"n_total max={int(sub['n_total'].max()):,}, "
            f"range min={sub['data_min'].min():.2f}, max={sub['data_max'].max():.2f}"
        )

    caption = (
        "Figure 5. Annual anomaly range metadata and temporal support by region. "
        "(a–c) Year-by-year envelopes defined by the annual minimum and maximum anomaly values for the "
        "global, US, and Europe subsets, respectively, using the immutable annual range metadata table. "
        "(d) Corresponding annual anomaly support counts (n_total) by region. Together, these panels "
        "document the temporal evolution of anomaly-domain breadth and analytical support after HybridQC, "
        "providing transparent context for interpretation of retained anomaly ranges and regional sampling depth."
    )
    cap_path.write_text(caption, encoding="utf-8")

    print("Saved:")
    print(png_path)
    print(tif_path)
    print(pdf_path)
    print(cap_path)
    print(out_csv)
    print("Summary:")
    for s in stats:
        print(" -", s)


if __name__ == "__main__":
    main()
