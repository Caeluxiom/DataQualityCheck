import pandas as pd 
import argparse

def load_and_summarize(filepath):
    df = pd.read_csv(filepath)
    print (f"\nfile: {filepath}")
    print (f"Rows: {df.shape[0]: , }")
    print (f"Columns:{df.shape[1]}")
    return df

    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="View a CSV file's internals quality.")
        parser.add_argument("filepath", help="File Location")
        args = parser.parse_args()
    load_and_summarize(args.filepath)

def check_missing_values(df):
    missing_count = df.isna().sum()
    missing_pct = (missing_count / len(df)) * 100

    report = pd.DataFrame({
        "missing_count": missing_count,
        "missing_pct": missing_pct.round(1)
    })

    report = report[report["missing_count"] > 0] .sort_values("missing_pct", ascending=False)

    print("\n---missing values---")
    if report.empty:
        print("no missing values found")
    
    else:
             print(report)

    return report