import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from dataqualitycheck import (
    load_and_summarize,
    check_missing_values,
    check_duplicates,
    check_type_issues,
    check_outliers,
)

last_results = None


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


def build_recommendations(
    missing_report,
    duplicate_count,
    type_issues,
    outlier_report
):
    recommendations = []

    for col, row in missing_report.iterrows():
        pct = row["missing_pct"]

        if pct >= 50:
            recommendations.append(
                f"'{col}' is {pct:.0f}% missing. Check if you need it."
            )
        elif pct >= 5:
            recommendations.append(
                f"'{col}' has {pct:.1f}% missing. Decide how to handle it."
            )

    if duplicate_count > 0:
        recommendations.append(
            f"{duplicate_count:,} duplicate rows found. Verify and clean."
        )

    for col, issue in type_issues:
        if issue == "Mixed types on load":
            recommendations.append(
                f"'{col}' has mixed value types. Check the values."
            )
        elif issue.startswith("Looks numeric"):
            recommendations.append(
                f"'{col}' looks numeric but is text. Check and convert if needed."
            )
        elif issue == "Multiple Python types":
            recommendations.append(
                f"'{col}' has multiple Python types. Check the values."
            )

    for col, count, pct in outlier_report:
        if pct >= 5:
            recommendations.append(
                f"'{col}' has {count:,} possible outliers. Check the values."
            )

    if not recommendations:
        recommendations.append(
            "No major issues found."
        )

    return recommendations


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

        repeated_values = []

        for col in df.columns:
            value_counts = df[col].value_counts()

            for value, count in value_counts.head(5).items():
                if count > 1:
                    repeated_values.append(
                        (
                            col,
                            str(value),
                            f"{count:,}",
                            f"{count / len(df):.1%}"
                        )
                    )

        repeated_values.sort(
            key=lambda row: float(row[3].rstrip("%")),
            reverse=True
        )

        duplicate_rows.extend(repeated_values)

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

        recommendations_list.delete(0, tk.END)

        recommendations = build_recommendations(
            missing_report,
            duplicate_count,
            type_issues,
            outlier_report
        )

        for recommendation in recommendations:
            recommendations_list.insert(
                tk.END,
                "- " + recommendation
            )

        status_label.config(text="Check complete.")

        global last_results
        last_results = {
            "filepath": filepath,
            "df": df,
            "missing_report": missing_report,
            "duplicate_count": duplicate_count,
            "duplicate_pct": duplicate_pct,
            "type_issues": type_issues,
            "outlier_report": outlier_report,
            "recommendations": recommendations,
        }

    except Exception as error:
        status_label.config(text="Error loading file.")
        messagebox.showerror("Error", str(error))


def export_report():
    if last_results is None:
        messagebox.showwarning(
            "Nothing to export",
            "Run a check first, then export the report."
        )
        return

    save_path = filedialog.asksaveasfilename(
        title="Save report as",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if not save_path:
        return

    r = last_results
    lines = []

    lines.append(f"Data Quality Report: {r['filepath']}")
    lines.append(f"Rows: {len(r['df']):,} | Columns: {len(r['df'].columns):,}")

    lines.append("\n--- Missing Values ---")
    if r["missing_report"].empty:
        lines.append("No missing values found")
    else:
        lines.append(r["missing_report"].to_string())

    lines.append("\n--- Duplicate Rows ---")
    lines.append(f"Fully duplicated rows: {r['duplicate_count']} ({r['duplicate_pct']:.1f}%)")

    lines.append("\n--- Potential Type Issues ---")
    if r["type_issues"]:
        for col, issue in r["type_issues"]:
            lines.append(f"'{col}': {issue}")
    else:
        lines.append("No obvious type issues detected.")

    lines.append("\n--- Potential Outliers (IQR) ---")
    if r["outlier_report"]:
        for col, count, pct in r["outlier_report"]:
            lines.append(f"'{col}': {count} potential outliers ({pct:.1f}%)")
    else:
        lines.append("No outliers detected.")

    lines.append("\n--- Recommendations ---")
    for rec in r["recommendations"]:
        lines.append(f"- {rec}")

    with open(save_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    status_label.config(text=f"Report saved to {save_path}")
    messagebox.showinfo("Export complete", f"Report saved to:\n{save_path}")


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

style = ttk.Style()
style.theme_use("clam")

style.configure("TFrame", background="#202020")
style.configure("TLabel", background="#202020", foreground="#eeeeee")
style.configure("TLabelframe", background="#202020", foreground="#eeeeee")
style.configure("TLabelframe.Label", background="#202020", foreground="#eeeeee")
style.configure("TButton", background="#303030", foreground="#eeeeee", borderwidth=1)

style.map(
    "TButton",
    background=[("active", "#404040"), ("pressed", "#505050")],
    foreground=[("active", "#ffffff")]
)

style.configure("TEntry", fieldbackground="#303030", foreground="#eeeeee")
style.configure("TNotebook", background="#202020", borderwidth=0)
style.configure("TNotebook.Tab", background="#303030", foreground="#eeeeee", padding=[10, 5])

style.map(
    "TNotebook.Tab",
    background=[("selected", "#404040"), ("active", "#383838")],
    foreground=[("selected", "#ffffff"), ("active", "#ffffff")]
)

style.configure("Treeview", background="#282828", foreground="#eeeeee", fieldbackground="#282828")
style.configure("Treeview.Heading", background="#303030", foreground="#eeeeee")

style.map(
    "Treeview",
    background=[("selected", "#404040")],
    foreground=[("selected", "#ffffff")]
)

window.configure(background="#202020")

title = ttk.Label(window, text="Data Quality Checker", font=("Arial", 20))
title.pack(pady=(15, 5))

subtitle = ttk.Label(window, text="Check a CSV for data quality problems.")
subtitle.pack(pady=(0, 15))

file_frame = ttk.Frame(window)
file_frame.pack(fill="x", padx=20)

file_path = tk.StringVar()

file_entry = ttk.Entry(file_frame, textvariable=file_path)
file_entry.pack(side="left", fill="x", expand=True)

browse_button = ttk.Button(file_frame, text="Browse", command=browse_file)
browse_button.pack(side="left", padx=(10, 0))

run_button = ttk.Button(window, text="Run Check", command=run_check)
run_button.pack(pady=15)

export_button = ttk.Button(window, text="Export Report", command=export_report)
export_button.pack(pady=(0, 15))

summary_frame = ttk.Frame(window)
summary_frame.pack(fill="x", padx=20, pady=5)

rows_value = create_summary(summary_frame, "Rows")
columns_value = create_summary(summary_frame, "Columns")
missing_value = create_summary(summary_frame, "Missing Columns")
duplicate_value = create_summary(summary_frame, "Duplicates")
type_value = create_summary(summary_frame, "Type Issues")
outlier_value = create_summary(summary_frame, "Outlier Columns")

notebook = ttk.Notebook(window)
notebook.pack(fill="both", expand=True, padx=20, pady=15)

missing_tab = ttk.Frame(notebook)
notebook.add(missing_tab, text="Missing Values")

missing_frame, missing_table = create_table(
    missing_tab,
    ("Column", "Missing Count", "Missing %"),
    (400, 150, 120)
)
missing_frame.pack(fill="both", expand=True, padx=10, pady=10)

duplicate_tab = ttk.Frame(notebook)
notebook.add(duplicate_tab, text="Duplicates")

duplicate_frame, duplicate_table = create_table(
    duplicate_tab,
    ("Column / Check", "Value / Count", "Count", "% of Rows"),
    (250, 250, 100, 100)
)
duplicate_frame.pack(fill="both", expand=True, padx=10, pady=10)

type_tab = ttk.Frame(notebook)
notebook.add(type_tab, text="Type Issues")

type_frame, type_table = create_table(
    type_tab,
    ("Column", "Issue"),
    (400, 300)
)
type_frame.pack(fill="both", expand=True, padx=10, pady=10)

outlier_tab = ttk.Frame(notebook)
notebook.add(outlier_tab, text="Outliers")

outlier_frame, outlier_table = create_table(
    outlier_tab,
    ("Column", "Outlier Count", "Outlier %"),
    (400, 150, 120)
)
outlier_frame.pack(fill="both", expand=True, padx=10, pady=10)

recommendations_tab = ttk.Frame(notebook)
notebook.add(recommendations_tab, text="Recommendations")

recommendations_list = tk.Listbox(
    recommendations_tab,
    font=("Arial", 11),
    bg="#282828",
    fg="#eeeeee",
    selectbackground="#404040"
)
recommendations_list.pack(fill="both", expand=True, padx=10, pady=10)

status_label = ttk.Label(window, text="Choose a CSV file to begin.")
status_label.pack(pady=(0, 10))

window.mainloop()