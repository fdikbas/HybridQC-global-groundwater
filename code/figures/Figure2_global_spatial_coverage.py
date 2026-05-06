# -*- coding: utf-8 -*-
"""
GlobalGWDrought.Paper.2.Figure2.global_spatial_coverage.py

Paper 2 – Figure 2
Global spatial coverage of stations contributing to the anomaly contract

Input:
    ./out_anomalies/station_anomalies_all.csv
    or
    ./out_anomalies/station_anomalies_all.zip

Optional basemap:
    ./in_shapefile/ne_110m_admin_0_countries.shp

Outputs:
    ./out_paper2_figure_designs/Figure_2_HybridQC_global_spatial_coverage.png
    ./out_paper2_figure_designs/Figure_2_HybridQC_global_spatial_coverage.tif
    ./out_paper2_figure_designs/Figure_2_HybridQC_global_spatial_coverage.pdf
    ./out_paper2_figure_designs/Figure_2_HybridQC_global_spatial_coverage_caption.txt
"""

from pathlib import Path as FilePath
import zipfile
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

try:
    import geopandas as gpd
    HAS_GPD = True
except Exception:
    HAS_GPD = False


# =========================================================
# User settings
# =========================================================
BASE_DIR = FilePath(r"D:/PythonCodes/GlobalGWDrought")
if not BASE_DIR.exists():
    BASE_DIR = FilePath(__file__).resolve().parent

ANOM_DIR = BASE_DIR / "out_anomalies"
OUT_DIR = BASE_DIR / "out_paper2_figure_designs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

STATION_ANOM_CSV = ANOM_DIR / "station_anomalies_all.csv"
STATION_ANOM_ZIP = ANOM_DIR / "station_anomalies_all.zip"
WORLD_SHP = BASE_DIR / "in_shapefile" / "ne_110m_admin_0_countries.shp"

FIG_STEM = "Figure_2_HybridQC_global_spatial_coverage"

PNG_DPI = 400
TIFF_DPI = 600
PDF_DPI = 600

# map extent for consistency with prior network figures
LON_MIN, LON_MAX = -180.0, 180.0
LAT_MIN, LAT_MAX = -60.0, 85.0

# journal-style restrained palette
COLORS = {
    "world_fill": "#FAFAFA",
    "world_edge": "#B8B8B8",
    "stations": "#557A9E",
    "grid": "#E4E4E4",
    "frame": "#C6C6C6",
    "text": "#25313B",
    "note_fill": "#FFFFFF",
}

mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.linewidth": 0.8,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.04,
    "figure.facecolor": "white",
})


# =========================================================
# Helpers
# =========================================================
def human_int(x):
    return f"{int(x):,}"

def load_station_anomalies(csv_path, zip_path):
    if csv_path.exists():
        return pd.read_csv(csv_path)
    if zip_path.exists():
        with zipfile.ZipFile(zip_path) as z:
            csv_names = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if not csv_names:
                raise FileNotFoundError("No CSV found inside station_anomalies_all.zip")
            with z.open(csv_names[0]) as f:
                return pd.read_csv(f)
    raise FileNotFoundError(
        f"Could not find anomaly contract in out_anomalies:\n"
        f"  {csv_path}\n"
        f"  {zip_path}"
    )

def maybe_plot_world(ax, shp_path):
    if not HAS_GPD:
        return False
    if not shp_path.exists():
        return False
    try:
        world = gpd.read_file(shp_path)
        if world.crs is not None:
            world = world.to_crs("EPSG:4326")
        world.plot(
            ax=ax,
            color=COLORS["world_fill"],
            edgecolor=COLORS["world_edge"],
            linewidth=0.45,
            zorder=1
        )
        return True
    except Exception as e:
        print(f"[WARN] Could not read world shapefile: {e}")
        return False


# =========================================================
# Main
# =========================================================
def main():
    print("Loading anomaly contract...")
    df = load_station_anomalies(STATION_ANOM_CSV, STATION_ANOM_ZIP)

    required = {"StnID", "Lat", "Lon", "Year", "Anomaly"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"station_anomalies_all is missing required columns: {sorted(missing)}")

    df = df[["StnID", "Lat", "Lon", "Year", "Anomaly"]].copy()
    df["Lat"] = pd.to_numeric(df["Lat"], errors="coerce")
    df["Lon"] = pd.to_numeric(df["Lon"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Anomaly"] = pd.to_numeric(df["Anomaly"], errors="coerce")

    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=["StnID", "Lat", "Lon", "Year", "Anomaly"]).copy()

    stations = df[["StnID", "Lat", "Lon"]].drop_duplicates(subset=["StnID"]).copy()
    stations = stations[
        stations["Lat"].between(-90, 90) &
        stations["Lon"].between(-180, 180)
    ].copy()

    n_stations = len(stations)
    n_anom = len(df)
    year_min = int(df["Year"].min())
    year_max = int(df["Year"].max())

    print(f"Stations with valid coordinates: {n_stations:,}")
    print(f"Anomaly-years: {n_anom:,}")
    print(f"Year range in anomaly contract: {year_min}-{year_max}")

    fig = plt.figure(figsize=(13.8, 6.8))
    ax = fig.add_axes([0.045, 0.08, 0.93, 0.86])

    # optional world basemap
    plotted_world = maybe_plot_world(ax, WORLD_SHP)
    if not plotted_world:
        ax.set_facecolor("white")

    # stations
    ax.scatter(
        stations["Lon"], stations["Lat"],
        s=0.45,
        c=COLORS["stations"],
        alpha=0.38,
        linewidths=0,
        rasterized=True,
        zorder=2
    )

    # extent and axes
    ax.set_xlim(LON_MIN, LON_MAX)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_xticks(np.arange(-180, 181, 60))
    ax.set_yticks(np.arange(-60, 91, 30))
    ax.grid(color=COLORS["grid"], linewidth=0.5, zorder=0)

    for spine in ax.spines.values():
        spine.set_color(COLORS["frame"])
        spine.set_linewidth(0.8)

    # summary note
    note_x, note_y = 0.018, 0.035
    note_w, note_h = 0.235, 0.13
    rect = FancyBboxPatch(
        (note_x, note_y), note_w, note_h,
        transform=ax.transAxes,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        facecolor=COLORS["note_fill"],
        edgecolor=COLORS["frame"],
        linewidth=0.8,
        alpha=0.97,
        zorder=3
    )
    ax.add_patch(rect)
    ax.text(
        note_x + 0.015, note_y + note_h - 0.025,
        f"Stations: {human_int(n_stations)}\n"
        f"Anomaly-years: {human_int(n_anom)}\n"
        f"Anomaly years: {year_min}–{year_max}",
        transform=ax.transAxes,
        ha="left", va="top",
        fontsize=9.4,
        color=COLORS["text"],
        zorder=4
    )

    # save
    png_path = OUT_DIR / f"{FIG_STEM}.png"
    tif_path = OUT_DIR / f"{FIG_STEM}.tif"
    pdf_path = OUT_DIR / f"{FIG_STEM}.pdf"
    cap_path = OUT_DIR / f"{FIG_STEM}_caption.txt"

    fig.savefig(png_path, dpi=PNG_DPI)
    fig.savefig(tif_path, dpi=TIFF_DPI)
    fig.savefig(pdf_path, dpi=PDF_DPI)
    plt.close(fig)

    caption = (
        "Figure 2. Global spatial coverage of stations contributing to the anomaly contract. "
        "The map shows the global distribution of monitoring stations contributing at least one "
        "retained annual anomaly to the HybridQC anomaly contract. The station network provides "
        "252,374 unique stations and 2,884,808 anomaly-years spanning 1901–2022. The figure is "
        "intended to document spatial coverage of the anomaly product rather than to imply uniform "
        "observation density across regions."
    )
    cap_path.write_text(caption, encoding="utf-8")

    print("Saved:")
    print(png_path)
    print(tif_path)
    print(pdf_path)
    print(cap_path)


if __name__ == "__main__":
    main()
