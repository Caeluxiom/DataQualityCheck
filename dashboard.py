import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from dataqualitycheck import (
    load_and_summarize,
    check_missing_values,
    check_duplicates,
    check_type_issues,
    check_outliers,
)


def browse_file():
    filepath = filedialog.askopenfilename(
        title="Choose CSV file",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    if filepath:
        file_path.set(filepath)


def run_check():
    filepath = file_path.get()

    if not filepath:
        messagebox.showwarning(
            "No file selected",
            "Please choose a CSV file first."
        )
        return

    try:
        df, type_warnings = load_and_summarize(filepath)

        missing_report = check_missing_values(df)
        duplicate_count = check_duplicates(df)
        type_issues = check_type_issues(df, type_warnings)
        check_outliers(df)

        rows_value.config(text=f"{len(df):,}")
        columns_value.config(text=f"{len(df.columns):,}")
        missing_value.config(text=f"{len(missing_report):,}")
        duplicate_value.config(text=f"{duplicate_count:,}")
        type_value.config(text=f"{len(type_issues):,}")

        status_label.config(text="Check complete.")

    except Exception as error:
        status_label.config(text="Error loading file.")
        messagebox.showerror("Error", str(error))


def create_summary(parent, title):
    frame = ttk.LabelFrame(parent, text=title)
    frame.pack(side="left", fill="both", expand=True, padx=5)

    value = ttk.Label(frame, text="-", font=("Arial", 16))
    value.pack(pady=12)

    return value


window = tk.Tk()
window.title("Data Quality Checker")
window.geometry("800x500")

title = ttk.Label(
    window,
    text="Data Quality Checker",
    font=("Arial", 20)
)
title.pack(pady=(15, 5))

subtitle = ttk.Label(
    window,
    text="Check a CSV for common data quality problems."
)
subtitle.pack(pady=(0, 15))

file_frame = ttk.Frame(window)
file_frame.pack(fill="x", padx=20)

file_path = tk.StringVar()

file_entry = ttk.Entry(
    file_frame,
    textvariable=file_path
)
file_entry.pack(side="left", fill="x", expand=True)

browse_button = ttk.Button(
    file_frame,
    text="Browse",
    command=browse_file
)
browse_button.pack(side="left", padx=(10, 0))

run_button = ttk.Button(
    window,
    text="Run Check",
    command=run_check
)
run_button.pack(pady=15)

summary_frame = ttk.Frame(window)
summary_frame.pack(fill="x", padx=20, pady=5)

rows_value = create_summary(summary_frame, "Rows")
columns_value = create_summary(summary_frame, "Columns")
missing_value = create_summary(summary_frame, "Missing Columns")
duplicate_value = create_summary(summary_frame, "Duplicates")
type_value = create_summary(summary_frame, "Type Issues")

status_label = ttk.Label(
    window,
    text="Choose a CSV file to begin."
)
status_label.pack(pady=20)

window.mainloop()
