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

    def check_duplicates(df):
        full_dupes = df.duplicated().sum()
        print("\n--- Duplicate Rows ---")
        print(f"fully duplicated rows: {full_dupes}")

        if full_dupes>0:
            pct = (full_dupes / len(df)) *100
            print(f"({pct: .1f}% of the dataset)")

        return full_dupes

    def check_type_issues(df):
     print("\n--- POTENTIAL TYPE ISSUES ---")
     flagged = []

     for col in df.select_dtypes(include="object").columns:
      sample = df[col].dropna().astype(str).head(50)
      looks_numeric = sample.str.replace(",", "",regex=False).str.replace("$", "", regex=False).str.match(r"^-?\d+\.?\
d*$").mean()
    
    if looks_numeric > 0.8:
       flagged.append(col)
       print(f"'{col}' is stored as a text but looks numeric ({looks_numeric: .0%} of the sample matches a number pattern)")

    if not flagged:
        print("no obvious issues detected but i am still just python code, recheck regardless if paranoid.") 

        return flagged    