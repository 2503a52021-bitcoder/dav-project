import argparse

import numpy as np
import pandas as pd

# Any |reported - expected| gap larger than this (in MT) is treated as an anomaly.
ANOMALY_THRESHOLD_MT = 0.05
ANOMALY_LABEL = 'Unrecorded Leakage / Audit Flag'
NO_DATA_LABEL = 'Insufficient Data'
NORMAL_LABEL = 'Normal'

NUMERIC_COLS = ['plastic_waste_mt', 'fishing_waste_mt', 'other_waste_mt',
                'waste_collected_mt', 'waste_recycled_mt', 'ocean_waste_mt', 'management_efficiency_%']


def clean_ocean_waste_data(file_path: str, output_path: str = "cleaned_ocean_waste_data.csv") -> pd.DataFrame:
    """
    Loads raw ocean waste data, validates records, cleans inconsistencies,
    and calculates derived metrics including ocean leakage discrepancy flags.

    Missing or non-numeric values are kept as NaN (NOT replaced with 0), so a blank cell
    can never create a fake zero or a false anomaly. Derived metrics that depend on a
    missing value are NaN too, and those years are flagged 'Insufficient Data'.
    """
    # Load dataset
    df = pd.read_csv(file_path)

    # 1. Clean Column Names
    df.columns = (df.columns.str.strip().str.lower()
                  .str.replace(' ', '_', regex=False)
                  .str.replace('(', '', regex=False)
                  .str.replace(')', '', regex=False))

    required = ['year'] + NUMERIC_COLS
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing expected column(s) after cleaning names: {missing_cols}. "
                         f"Columns found: {list(df.columns)}")

    # 2. Data Integrity Checks
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)
    df = df.drop_duplicates(subset=['year']).sort_values('year').reset_index(drop=True)

    # 3. Handle Missing Values: convert to numbers, keep gaps as NaN
    for col in NUMERIC_COLS:
        before_missing = df[col].isna().sum()
        df[col] = pd.to_numeric(df[col], errors='coerce')
        coerced = df[col].isna().sum() - before_missing
        if coerced:
            print(f"Warning: {coerced} non-numeric value(s) in '{col}' were treated as missing.")

    incomplete = df[df[NUMERIC_COLS].isna().any(axis=1)]
    if not incomplete.empty:
        print(f"Note: {len(incomplete)} year(s) have missing values and were left blank "
              f"(not zero-filled): {incomplete['year'].tolist()}")

    # 4. Derive Feature Engineering Metrics (NaN in -> NaN out)
    df['total_waste_generated_mt'] = df['plastic_waste_mt'] + df['fishing_waste_mt'] + df['other_waste_mt']
    df['expected_ocean_waste_mt'] = df['total_waste_generated_mt'] - df['waste_collected_mt']
    # "+ 0.0" turns floating-point "-0.00" into a clean 0.00
    df['reporting_gap_mt'] = (df['ocean_waste_mt'] - df['expected_ocean_waste_mt']).round(2) + 0.0

    # Derived Rates (NaN where the denominator is zero or an input is missing)
    total = df['total_waste_generated_mt']
    collected = df['waste_collected_mt']
    df['collection_rate_%'] = ((collected / total) * 100).where(total > 0).round(2)
    df['recycling_rate_%'] = ((df['waste_recycled_mt'] / collected) * 100).where(collected > 0).round(2)
    df['plastic_share_%'] = ((df['plastic_waste_mt'] / total) * 100).where(total > 0).round(2)

    # Discrepancy Anomaly Flag: any year (positive OR negative gap) beyond the threshold
    gap = df['reporting_gap_mt']
    df['anomaly_flag'] = np.select(
        [gap.isna(), gap.abs() > ANOMALY_THRESHOLD_MT],
        [NO_DATA_LABEL, ANOMALY_LABEL],
        default=NORMAL_LABEL,
    )

    # Save cleaned dataset
    df.to_csv(output_path, index=False)
    flagged = df.loc[df['anomaly_flag'] == ANOMALY_LABEL, 'year'].tolist()
    print(f"Data successfully cleaned and saved to '{output_path}'. Total records: {len(df)}")
    print(f"Anomaly years flagged: {flagged if flagged else 'none'}")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean the raw ocean waste dataset.")
    parser.add_argument("input", nargs="?", default="Ocean_Waste_Management_1900_2026_excel_data.csv",
                        help="path to the raw CSV (default: Ocean_Waste_Management_1900_2026_excel_data.csv)")
    parser.add_argument("output", nargs="?", default="cleaned_ocean_waste_data.csv",
                        help="where to save the cleaned CSV (default: cleaned_ocean_waste_data.csv)")
    args = parser.parse_args()
    clean_ocean_waste_data(args.input, args.output)
