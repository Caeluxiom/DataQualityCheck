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
