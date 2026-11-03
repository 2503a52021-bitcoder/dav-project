import argparse

import pandas as pd
import numpy as np

ANOMALY_LABEL = 'Unrecorded Leakage / Audit Flag'
NO_DATA_LABEL = 'Insufficient Data'


def _year_span(years) -> str:
    """Format a list of years as '2022' or '2022-2025'."""
    years = sorted(int(y) for y in years)
    return str(years[0]) if years[0] == years[-1] else f"{years[0]}-{years[-1]}"


def run_statistical_analysis(cleaned_file_path: str):
    """
    Performs multi-decade statistical evaluation, calculates correlations,
    and summaries milestone year trends.
    """
    df = pd.read_csv(cleaned_file_path)

    print("=" * 60)
    print("OCEAN WASTE MANAGEMENT: STATISTICAL ANALYSIS REPORT")
    print("=" * 60)

    # 1. Historical Growth & Summary Statistics
    valid = df.dropna(subset=['ocean_waste_mt'])
    start_year = valid.iloc[0]
    peak_year = valid.loc[valid['ocean_waste_mt'].idxmax()]
    latest_year = valid.iloc[-1]

    if start_year['ocean_waste_mt'] > 0:
        growth_text = f"{peak_year['ocean_waste_mt'] / start_year['ocean_waste_mt']:.1f}x Expansion"
    else:
        growth_text = "n/a (starting value is zero)"

    print(f"\n--- 1. Ocean Waste Expansion Summary ---")
    print(f"Initial Ocean Waste ({int(start_year['year'])}): {start_year['ocean_waste_mt']:.2f} MT")
    print(f"Peak Ocean Waste ({int(peak_year['year'])}): {peak_year['ocean_waste_mt']:.2f} MT")
    print(f"Growth Multiple: {growth_text}")
    print(f"{int(latest_year['year'])} Modeled Ocean Waste: {latest_year['ocean_waste_mt']:.2f} MT")
    if peak_year['anomaly_flag'] == ANOMALY_LABEL:
        print(f"  (Note: the peak year {int(peak_year['year'])} is flagged as a reporting anomaly, "
              f"so the peak and growth multiple may be inflated.)")

    # 2. Key Milestones Table Analysis
    milestone_years = [1900, 1950, 1980, 2000, 2020, 2026]
    milestones_df = df[df['year'].isin(milestone_years)][
        ['year', 'plastic_waste_mt', 'ocean_waste_mt', 'waste_collected_mt',
         'waste_recycled_mt', 'management_efficiency_%', 'plastic_share_%', 'collection_rate_%']
    ]
    print("\n--- 2. Historical Milestone Summary ---")
    print(milestones_df.to_string(index=False))
    absent = sorted(set(milestone_years) - set(df['year']))
    if absent:
        print(f"(Milestone year(s) not present in the data: {absent})")

    # 3. Correlation Matrix (missing values are ignored pairwise)
    corr_cols = ['ocean_waste_mt', 'plastic_waste_mt', 'fishing_waste_mt',
                 'other_waste_mt', 'waste_collected_mt', 'management_efficiency_%']
    correlation_matrix = df[corr_cols].corr()
    print("\n--- 3. Correlation with Ocean Waste ---")
    print(correlation_matrix['ocean_waste_mt'].sort_values(ascending=False).to_string())

    # 4. Anomaly Audit Summary (period is taken from the data, not hard-coded)
    anomalies = df[df['anomaly_flag'] == ANOMALY_LABEL][
        ['year', 'ocean_waste_mt', 'expected_ocean_waste_mt', 'reporting_gap_mt']]
    period = f" ({_year_span(anomalies['year'])})" if not anomalies.empty else ""
    print(f"\n--- 4. Reporting Anomaly Audit{period} ---")
    if anomalies.empty:
        print("No reporting anomalies found.")
    else:
        print(anomalies.to_string(index=False))

    no_data = df[df['anomaly_flag'] == NO_DATA_LABEL]['year'].tolist()
    if no_data:
        print(f"\nYears that could not be audited (missing inputs): {no_data}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the statistical analysis on the cleaned ocean waste CSV.")
    parser.add_argument("input", nargs="?", default="cleaned_ocean_waste_data.csv",
                        help="path to the cleaned CSV (default: cleaned_ocean_waste_data.csv)")
    args = parser.parse_args()
    run_statistical_analysis(args.input)
