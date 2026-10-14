"""
Figure 2 district plots
-----------------------
Draws one square plot per district with:
  - Kelch13 prevalence (%) on the left y-axis as grouped bars
  - Yearly malaria incidence per 1,000 on the right y-axis as a line with points
  - A dotted 10% prevalence threshold
  - Large fonts and a square plotting area
  - No per-panel legend

Expected input file:
    Figure2_plot_data_revised.xlsx

Expected worksheet:
    Figure2_Plot_Data

Expected columns:
    District
    Year
    Incidence /1,000
    Combined prevalence (%)
    C469Y
    C469F
    A675V
    R561H
    P441L

Outputs:
    One PNG and one PDF per district.
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------
# USER SETTINGS
# ---------------------------------------------------------------------

INPUT_FILE = "Figure2_plot_data_revised.xlsx"
SHEET_NAME = "Figure2_Plot_Data"
OUTPUT_DIR = Path("figure2_district_plots")

DISTRICT_ORDER = [
    "Katakwi", "Lamwo", "Kaabong", "Agago",
    "Rukiga", "Hoima", "Mubende", "Kanungu",
    "Tororo", "Kasese", "Kapchorwa", "Kole",
    "Koboko", "Arua", "Amolatar", "Jinja",
]

YEARS = [2017, 2018, 2019, 2020, 2021, 2022]

PREVALENCE_SERIES = [
    "Combined prevalence (%)",
    "C469Y",
    "C469F",
    "A675V",
    "R561H",
    "P441L",
]

# Colour-blind-conscious palette.
# Change these hex values if you want different colours.
COLOURS = {
    "Combined prevalence (%)": "#4D4D4D",
    "C469Y": "#0072B2",
    "C469F": "#56B4E9",
    "A675V": "#E69F00",
    "R561H": "#CC79A7",
    "P441L": "#009E73",
    "Incidence": "#6A1B9A",
    "Threshold": "#777777",
}

# Plot limits used across all districts so panels are comparable.
PREVALENCE_YMAX = 70
INCIDENCE_YMAX = 2000

# Bar geometry.
BAR_WIDTH = 0.12


# ---------------------------------------------------------------------
# PLOTTING FUNCTION
# ---------------------------------------------------------------------

def plot_district(data: pd.DataFrame, district: str, output_dir: Path) -> None:
    """Create one square district plot and export PNG + PDF."""

    district_data = (
        data.loc[data["District"] == district]
        .sort_values("Year")
        .copy()
    )

    if district_data.empty:
        print(f"Skipping {district}: no data found.")
        return

    # One figure per district.
    # The axes box itself is forced to a 1:1 aspect ratio.
    fig = plt.figure(figsize=(8.8, 8.8))
    ax_prev = fig.add_axes([0.12, 0.12, 0.72, 0.72])
    ax_inc = ax_prev.twinx()
    ax_prev.set_box_aspect(1)

    # Position six prevalence bars around each annual x position.
    offsets = {
        series: (i - (len(PREVALENCE_SERIES) - 1) / 2) * BAR_WIDTH
        for i, series in enumerate(PREVALENCE_SERIES)
    }

    # Grouped prevalence bars.
    for series in PREVALENCE_SERIES:
        x_values = []
        y_values = []

        for year in YEARS:
            row = district_data.loc[district_data["Year"] == year]

            if row.empty:
                value = 0.0
            else:
                value = row.iloc[0][series]
                value = 0.0 if pd.isna(value) else float(value)

            x_values.append(year + offsets[series])
            y_values.append(value)

        ax_prev.bar(
            x_values,
            y_values,
            width=BAR_WIDTH * 0.88,
            color=COLOURS[series],
            edgecolor="none",
            zorder=2,
        )

    # 10% prevalence threshold.
    ax_prev.axhline(
        10,
        color=COLOURS["Threshold"],
        linestyle=":",
        linewidth=2.0,
        zorder=1,
    )

    # Yearly malaria incidence on the right y-axis.
    incidence = []
    for year in YEARS:
        row = district_data.loc[district_data["Year"] == year]
        if row.empty or pd.isna(row.iloc[0]["Incidence /1,000"]):
            incidence.append(float("nan"))
        else:
            incidence.append(float(row.iloc[0]["Incidence /1,000"]))

    ax_inc.plot(
        YEARS,
        incidence,
        color=COLOURS["Incidence"],
        linewidth=3.2,
        marker="o",
        markersize=6.5,
        zorder=4,
    )

    # -----------------------------------------------------------------
    # FORMATTING
    # -----------------------------------------------------------------

    ax_prev.set_title(
        district,
        loc="left",
        fontsize=20,
        fontweight="bold",
        pad=10,
    )

    # X-axis.
    ax_prev.set_xlim(2016.35, 2022.65)
    ax_prev.set_xticks(YEARS)
    ax_prev.set_xticklabels(
        [str(year) for year in YEARS],
        rotation=90,
        fontsize=14,
    )
    ax_prev.set_xlabel("Year", fontsize=16, labelpad=12)

    # Left y-axis: prevalence.
    ax_prev.set_ylim(0, PREVALENCE_YMAX)
    ax_prev.set_yticks(range(0, PREVALENCE_YMAX + 1, 10))
    ax_prev.tick_params(axis="y", labelsize=14)
    ax_prev.set_ylabel("Kelch13 prevalence (%)", fontsize=16)

    # Right y-axis: incidence.
    ax_inc.set_ylim(0, INCIDENCE_YMAX)
    ax_inc.set_yticks([0, 500, 1000, 1500, 2000])
    ax_inc.tick_params(axis="y", labelsize=14)
    ax_inc.set_ylabel(
        "Malaria incidence per 1,000",
        fontsize=16,
        rotation=270,
        labelpad=24,
    )

    # Light horizontal grid only.
    ax_prev.grid(
        axis="y",
        linewidth=0.7,
        alpha=0.22,
        zorder=0,
    )

    # Clean white background.
    fig.patch.set_facecolor("white")
    ax_prev.set_facecolor("white")

    # Remove top border for a cleaner manuscript style.
    ax_prev.spines["top"].set_visible(False)
    ax_inc.spines["top"].set_visible(False)

    # -----------------------------------------------------------------
    # EXPORT
    # -----------------------------------------------------------------

    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = district.replace(" ", "_")
    png_path = output_dir / f"{safe_name}.png"
    pdf_path = output_dir / f"{safe_name}.pdf"

    fig.savefig(
        png_path,
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
    )
    fig.savefig(
        pdf_path,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(fig)

    print(f"Saved {district}:")
    print(f"  {png_path}")
    print(f"  {pdf_path}")


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main() -> None:
    data = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)

    required_columns = [
        "District",
        "Year",
        "Incidence /1,000",
        *PREVALENCE_SERIES,
    ]

    missing = [column for column in required_columns if column not in data.columns]
    if missing:
        raise ValueError(
            "The input file is missing required columns: "
            + ", ".join(missing)
        )

    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")

    for district in DISTRICT_ORDER:
        plot_district(data, district, OUTPUT_DIR)


if __name__ == "__main__":
    main()
