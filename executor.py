import pandas as pd


class Executor:
    """
    Deterministic execution engine over pandas.
    """

    def __init__(self, csv_path="data/transactions.csv"):
        self.df = pd.read_csv(csv_path, skip_blank_lines=True)
        self.df = self.df[self.df["date"] != "date"]
        self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")
        self.df = self.df.dropna(subset=["date"])

    def execute(self, intent, entities, start_date, end_date):
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
            if df.empty:
                return None
            return df.groupby("category")["amount"].sum().idxmax()

        if intent == "compare_periods":
            return self._compare_periods(df, start_date, end_date)

        if intent == "average_spend":
            return float(df["amount"].mean()) if not df.empty else 0

        raise ValueError(f"Unknown intent: {intent}")

    # ---------------- FIXED COMPARISON LOGIC ----------------
    def _compare_periods(self, df, start_date, end_date):
        """
        Always return ALL months in the requested range,
        even if spending is zero.
        """
        if not start_date or not end_date:
            return {}

        # Generate all months in range
        periods = pd.period_range(
            start=pd.to_datetime(start_date),
            end=pd.to_datetime(end_date),
            freq="M"
        )

        results = {}

        for p in periods:
            month_df = df[
                (df["date"].dt.year == p.year) &
                (df["date"].dt.month == p.month)
            ]
            results[str(p)] = int(month_df["amount"].sum())

        return results
