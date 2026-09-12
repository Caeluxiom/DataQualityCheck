import pandas as pd
import argparse
import warnings


def load_and_summarize(filepath):
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        df = pd.read_csv(filepath)

    type_warnings = []

    for warning in caught_warnings:
        if warning.category == pd.errors.DtypeWarning:
            message = str(warning.message)

            columns_text = (
                message
                .split("Columns (")[1]
                .split(") have mixed types")[0]
            )

            columns = columns_text.split(",")

            for column in columns:
                column_name = column.split(": ", 1)[1]
                type_warnings.append(column_name)

    print("\n--- Data Types ---")
    print(df.dtypes)

    print(f"\nFile: {filepath}")
    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")

    return df, type_warnings


def check_missing_values(df):
    missing_count = df.isna().sum()
    missing_pct = (missing_count / len(df)) * 100

    report = pd.DataFrame({
        "missing_count": missing_count,
        "missing_pct": missing_pct.round(1)
    })

    report = report[
        report["missing_count"] > 0
    ].sort_values("missing_pct", ascending=False)

    print("\n--- Missing Values ---")

    if report.empty:
        print("No missing values found")
    else:
        print(report)

    return report


def check_duplicates(df):
    full_dupes = df.duplicated().sum()

    print("\n--- Duplicate Rows ---")
    print(f"Fully duplicated rows: {full_dupes}")

    if full_dupes > 0:
        pct = (full_dupes / len(df)) * 100
        print(f"({pct:.1f}% of the dataset)")

    return full_dupes


def check_type_issues(df, type_warnings):
    print("\n--- Potential Type Issues ---")

    flagged = []

    if type_warnings:
        print("Mixed types detected during CSV loading:")

        for col in type_warnings:
            print(f"- '{col}'")

    for col in df.select_dtypes(
        include=["object", "string"]
    ).columns:

        sample = df[col].dropna().head(1000)

        types = sample.map(type).unique()

        if len(types) > 1:
            print(
                f"'{col}' contains multiple Python types: {types}"
            )

        looks_numeric = sample.str.match(
            r"^-?(?:[₹$€£¥]\s*)?"
            r"(?:\d{1,3}(?:,\d{3})+|\d+)"
            r"(?:\.\d+)?$"
        ).mean()

        if looks_numeric > 0.8:
            flagged.append(col)

            print(
                f"'{col}' is stored as text but looks numeric "
                f"({looks_numeric:.0%} of the sample "
                f"matches a number pattern)"
            )

    if not flagged and not type_warnings:
        print("No obvious type issues detected.")

    return flagged


def check_outliers(df):
    print("\n--- Potential Outliers (IQR) ---")

    numeric_cols = df.select_dtypes(
        include="number"
    ).columns

    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outlier_count = (
            (df[col] < lower) | (df[col] > upper)
        ).sum()

        if outlier_count > 0:
            pct = (outlier_count / len(df)) * 100

            print(
                f"'{col}': {outlier_count} potential outliers "
                f"({pct:.1f}%)"
            )


def run_check(filepath):
    df, type_warnings = load_and_summarize(filepath)

    missing_report = check_missing_values(df)
    full_dupes = check_duplicates(df)
    flagged_types = check_type_issues(df, type_warnings)
    check_outliers(df)

    print("\nCheck Complete!\n")

    return df, missing_report, full_dupes, flagged_types


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check a CSV quality."
    )

    parser.add_argument(
        "filepath",
        help="Path to the CSV file"
    )

    args = parser.parse_args()

    run_check(args.filepath)
