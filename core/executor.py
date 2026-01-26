import pandas as pd
from datetime import timedelta


class Executor:
    """
    Deterministic execution engine over pandas.
    """

    def __init__(self, csv_path="data/transactions.csv"):
        self.df = pd.read_csv(csv_path, skip_blank_lines=True)

        # Safety cleanup
        self.df = self.df[self.df["date"] != "date"]
        self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")
        self.df = self.df.dropna(subset=["date"])

    def execute(self, intent, entities, start_date, end_date):
        """
        Main intent dispatcher
        """
        df = self.df.copy()

        # ---------------- Date filter ----------------
        if start_date and end_date:
            df = df[
                (df["date"] >= pd.to_datetime(start_date)) &
                (df["date"] <= pd.to_datetime(end_date))
            ]

        # ---------------- Entity filters ----------------
        if entities.get("category"):
            df = df[df["category"] == entities["category"]]

        if entities.get("merchant"):
            df = df[df["merchant"] == entities["merchant"]]

        if entities.get("amount"):
            df = df[df["amount"] >= entities["amount"]]

        # ---------------- Intent dispatch ----------------
        if intent == "total_spend":
            return int(df["amount"].sum())

        if intent == "list_transactions":
            return df[["date", "amount", "category", "merchant"]].to_dict(
                orient="records"
            )

        if intent == "top_category":
            return self._top_category()

        if intent == "compare_periods":
            return self._compare_periods(start_date, end_date, entities)

        if intent == "average_spend":
            return float(df["amount"].mean()) if not df.empty else 0

        raise ValueError(f"Unknown intent: {intent}")

    # ---------------- FIX 1: TOP CATEGORY ----------------
    def _top_category(self):
        """
        Compute highest spending category over ENTIRE dataset.
        This is intentionally global and ignores date filters.
        """
        if self.df.empty:
            return None

        grouped = self.df.groupby("category")["amount"].sum()
        return grouped.idxmax()

    # ---------------- FIX 2: PROPER COMPARISON ----------------
    def _compare_periods(self, start_date, end_date, entities):
        """
        Compare current period vs previous period
        (e.g., this month vs last month).
        """

        if not start_date or not end_date:
            return {}

        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        # -------- Current period --------
        current_df = self.df[
            (self.df["date"] >= start) &
            (self.df["date"] <= end)
        ]

        if entities.get("category"):
            current_df = current_df[current_df["category"] == entities["category"]]

        if entities.get("merchant"):
            current_df = current_df[current_df["merchant"] == entities["merchant"]]

        current_total = int(current_df["amount"].sum())

        # -------- Previous period (same duration) --------
        delta = end - start
        prev_end = start - timedelta(seconds=1)
        prev_start = prev_end - delta

        prev_df = self.df[
            (self.df["date"] >= prev_start) &
            (self.df["date"] <= prev_end)
        ]

        if entities.get("category"):
            prev_df = prev_df[prev_df["category"] == entities["category"]]

        if entities.get("merchant"):
            prev_df = prev_df[prev_df["merchant"] == entities["merchant"]]

        prev_total = int(prev_df["amount"].sum())

        return {
            start.strftime("%Y-%m"): current_total,
            prev_start.strftime("%Y-%m"): prev_total
        }