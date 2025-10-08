import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter


class HealthcareApp:
    def __init__(self, root):
        root.title("Samir Bhurtel - 32100095 - Healthcare Worker App")
        root.geometry("820x520")

        self.root = root
        self.df = None
        self.summary = {}

        self._build_ui()

    # ---------------- UI -----------------
    def _build_ui(self):
        header = tk.Label(
            self.root,
            text="Healthcare Worker Engagement – A2",
            font=("Segoe UI", 16, "bold"),
        )
        header.pack(pady=10)

        # Action buttons
        btns = tk.Frame(self.root)
        btns.pack(fill="x", padx=16, pady=8)

        ttk.Button(btns, text="1) Load Data", command=self.load_data).grid(
            row=0, column=0, padx=6, pady=6, sticky="w"
        )
        ttk.Button(btns, text="2) Process Summary", command=self.process_data).grid(
            row=0, column=1, padx=6, pady=6, sticky="w"
        )
        ttk.Button(btns, text="3) Pie: Dept Count", command=self.plot_dept_pie).grid(
            row=0, column=2, padx=6, pady=6, sticky="w"
        )
        ttk.Button(
            btns, text="4) Bar: Marital Status", command=self.plot_marital_bar
        ).grid(row=0, column=3, padx=6, pady=6, sticky="w")
        ttk.Button(btns, text="5) Dashboard", command=self.open_dashboard).grid(
            row=0, column=4, padx=6, pady=6, sticky="w"
        )

        # Output text area
        self.out = tk.Text(self.root, height=18, wrap="word")
        self.out.pack(fill="both", expand=True, padx=16, pady=8)
        self._log("Welcome! Use the buttons above in order.\n")

    def _log(self, msg: str):
        self.out.insert("end", msg + "\n")
        self.out.see("end")

    # ------------- Data Ops -------------
    def load_data(self):
        try:
            path = "nurs.csv"
            self.df = pd.read_csv(path)
            self._log(f"Loaded data: {len(self.df)} records from '{path}'.")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def _require_df(self):
        if self.df is None:
            messagebox.showwarning("Data not loaded", "Please load the CSV first.")
            return False
        return True

    def process_data(self):
        if not self._require_df():
            return
        df = self.df.copy()

        # Harmonize column names
        if "EmpID" not in df.columns and "EmployeeID" in df.columns:
            df = df.rename(columns={"EmployeeID": "EmpID"})
        if "YearsInCurrentRole" not in df.columns and "YearsInCurrRole" in df.columns:
            df = df.rename(columns={"YearsInCurrRole": "YearsInCurrentRole"})

        required = [
            "EmpID",
            "Age",
            "Gender",
            "MaritalStatus",
            "Education",
            "Department",
            "JobRole",
            "HourlyRate",
            "YearsAtCompany",
            "YearsInCurrentRole",
            "DistanceFromHome",
            "WorkLifeBalance",
            "YearsLastPromotion",
            "YearsCurrManager",
            "Attrition",
        ]
        missing = [c for c in required if c not in df.columns]
        if missing:
            messagebox.showerror(
                "Missing columns", f"The following columns are missing: {missing}"
            )
            return

        summary = {}
        summary["total_employees"] = int(len(df))
        summary["unique_departments"] = sorted(df["Department"].unique().tolist())
        summary["employees_per_department"] = (
            df["Department"].value_counts().astype(int).to_dict()
        )
        summary["gender_counts"] = (
            df["Gender"].value_counts().astype(int).to_dict()
        )

        def min_max_avg(series):
            return {
                "min": float(series.min()),
                "max": float(series.max()),
                "avg": float(round(series.mean(), 2)),
            }

        summary["age_stats"] = min_max_avg(df["Age"])
        summary["distance_from_home_stats"] = min_max_avg(df["DistanceFromHome"])
        summary["hourly_rate_stats"] = min_max_avg(df["HourlyRate"])

        ms_counts = df["MaritalStatus"].value_counts(normalize=True) * 100.0
        summary["marital_status_percent"] = {
            k: float(round(v, 2)) for k, v in ms_counts.to_dict().items()
        }

        summary["avg_work_life_balance"] = float(
            round(df["WorkLifeBalance"].mean(), 2)
        )
        summary["total_attritions"] = int(
            (df["Attrition"].astype(str).str.strip() == "Yes").sum()
        )

        self.df = df
        self.summary = summary
        self._log(
            "Processed summary successfully. See details below:"
            + pd.Series(summary, dtype=object).to_string()
        )

    def plot_dept_pie(self):
        if not self._require_df():
            return
        counts = self.df["Department"].value_counts()
        plt.figure()
        plt.pie(counts.values, labels=counts.index, autopct="%1.1f%%")
        plt.title("Employees per Department")
        plt.tight_layout()
        plt.show()

    def plot_marital_bar(self):
        if not self._require_df():
            return
        counts = self.df["MaritalStatus"].value_counts()
        plt.figure()
        plt.bar(counts.index, counts.values)
        plt.title("Marital Status Distribution")
        plt.xlabel("Marital Status")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.show()

    def open_dashboard(self):
        if not self.summary:
            self.process_data()
            if not self.summary:
                return

        dash = tk.Toplevel(self.root)
        dash.title("Dashboard – Key Metrics")
        dash.geometry("520x360")

        s = self.summary
        items = [
            ("Total Employees", s.get("total_employees")),
            ("Departments", ", ".join(s.get("unique_departments", []))),
            ("Gender Counts", s.get("gender_counts")),
            ("Attritions (Yes)", s.get("total_attritions")),
            ("Avg Work-Life Balance", s.get("avg_work_life_balance")),
            ("Avg Age", s.get("age_stats", {}).get("avg")),
            ("Avg Hourly Rate", s.get("hourly_rate_stats", {}).get("avg")),
            ("Avg Distance From Home", s.get("distance_from_home_stats", {}).get("avg")),
        ]

        row = 0
        for label, value in items:
            tk.Label(dash, text=f"{label}:", font=("Segoe UI", 10, "bold")).grid(
                row=row, column=0, sticky="w", padx=10, pady=6
            )
            tk.Label(dash, text=str(value)).grid(row=row, column=1, sticky="w")
            row += 1

        btns = tk.Frame(dash)
        btns.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Show Dept Pie", command=self.plot_dept_pie).pack(
            side="left", padx=6
        )
        ttk.Button(btns, text="Show Marital Bar", command=self.plot_marital_bar).pack(
            side="left", padx=6
        )


def main():
    root = tk.Tk()
    app = HealthcareApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
