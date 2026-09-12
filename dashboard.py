import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from dataqualitycheck import (
    load_and_summarize,
    check_missing_values,
    check_duplicates,
    check_type_issues,
    check_outliers,
)


def clear_table(table):
    for item in table.get_children():
        table.delete(item)


def fill_table(table, rows):
    clear_table(table)

    for row in rows:
        table.insert("", "end", values=row)


def create_table(parent, columns, widths):
    frame = ttk.Frame(parent)

    table = ttk.Treeview(
        frame,
        columns=columns,
        show="headings"
    )

    for column, width in zip(columns, widths):
        table.heading(column, text=column)
        table.column(column, width=width)

    scrollbar = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=table.yview
    )

    table.configure(yscrollcommand=scrollbar.set)

    table.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return frame, table


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
        status_label.config(text="Loading CSV...")
        window.update()

        df, type_warnings = load_and_summarize(filepath)

        missing_report = check_missing_values(df)
        duplicate_count, duplicate_pct = check_duplicates(df)
        type_issues = check_type_issues(df, type_warnings)
        outlier_report = check_outliers(df)

        rows_value.config(text=f"{len(df):,}")
        columns_value.config(text=f"{len(df.columns):,}")
        missing_value.config(text=f"{len(missing_report):,}")
        duplicate_value.config(text=f"{duplicate_count:,}")
        type_value.config(text=f"{len(type_issues):,}")
        outlier_value.config(text=f"{len(outlier_report):,}")

        missing_rows = []

        for col, row in missing_report.iterrows():
            missing_rows.append(
                (
                    col,
                    f"{row['missing_count']:,.0f}",
                    f"{row['missing_pct']:.1f}%"
                )
            )

        fill_table(missing_table, missing_rows)

        duplicate_rows = []

        if duplicate_count > 0:
            duplicate_rows.append(
                (
                    "Full duplicate rows",
                    f"{duplicate_count:,}",
                    f"{duplicate_pct:.1f}%"
                )
            )

        fill_table(duplicate_table, duplicate_rows)

        type_rows = []

        for col, issue in type_issues:
            type_rows.append((col, issue))

        fill_table(type_table, type_rows)

        outlier_rows = []

        for col, count, pct in outlier_report:
            outlier_rows.append(
                (
                    col,
                    f"{count:,}",
                    f"{pct:.1f}%"
                )
            )

        fill_table(outlier_table, outlier_rows)

        status_label.config(text="Check complete.")

    except Exception as error:
        status_label.config(text="Error loading file.")
        messagebox.showerror("Error", str(error))


def create_summary(parent, title):
    frame = ttk.LabelFrame(parent, text=title)
    frame.pack(side="left", fill="both", expand=True, padx=5)

    value = ttk.Label(
        frame,
        text="-",
        font=("Arial", 16)
    )

    value.pack(pady=12)

    return value


window = tk.Tk()
window.title("Data Quality Checker")
window.geometry("850x650")
window.minsize(750, 550)

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
outlier_value = create_summary(summary_frame, "Outlier Columns")

notebook = ttk.Notebook(window)
notebook.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=15
)

missing_tab = ttk.Frame(notebook)
notebook.add(missing_tab, text="Missing Values")

missing_frame, missing_table = create_table(
    missing_tab,
    ("Column", "Missing Count", "Missing %"),
    (400, 150, 120)
)

missing_frame.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

duplicate_tab = ttk.Frame(notebook)
notebook.add(duplicate_tab, text="Duplicates")

duplicate_frame, duplicate_table = create_table(
    duplicate_tab,
    ("Check", "Count", "Percentage"),
    (400, 150, 120)
)

duplicate_frame.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

type_tab = ttk.Frame(notebook)
notebook.add(type_tab, text="Type Issues")

type_frame, type_table = create_table(
    type_tab,
    ("Column", "Issue"),
    (400, 300)
)

type_frame.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

outlier_tab = ttk.Frame(notebook)
notebook.add(outlier_tab, text="Outliers")

outlier_frame, outlier_table = create_table(
    outlier_tab,
    ("Column", "Outlier Count", "Outlier %"),
    (400, 150, 120)
)

outlier_frame.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

status_label = ttk.Label(
    window,
    text="Choose a CSV file to begin."
)

status_label.pack(pady=(0, 10))

window.mainloop()
