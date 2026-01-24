import pandas as pd


class Executor:
    """
    Deterministic execution engine over pandas.
    One function per intent.
    """

    def __init__(self, csv_path="data/transactions.csv"):
        self.df = pd.read_csv(csv_path)
        self.df["date"] = pd.to_datetime(self.df["date"])

    def execute(self, intent, entities, start_date, end_date):
        """
        Execute intent using extracted entities and date range.
        """

        df = self.df.copy()

        # Date filtering
        if start_date is not None and end_date is not None:
            df = df[
                (df["date"] >= pd.to_datetime(start_date)) &
                (df["date"] <= pd.to_datetime(end_date))
            ]

        # Category filtering
        if entities.get("category"):
            df = df[df["category"] == entities["category"]]

        # Merchant filtering
        if entities.get("merchant"):
            df = df[df["merchant"] == entities["merchant"]]

        # Intent dispatch
        if intent == "total_spend":
            return self._total_spend(df)

        if intent == "list_transactions":
            return self._list_transactions(df)

        if intent == "top_category":
            return self._top_category(df)

        if intent == "compare_periods":
            return self._compare_periods(df)

        if intent == "average_spend":
            return self._average_spend(df)

        raise ValueError(f"Unknown intent: {intent}")

    # -------------------- Intent handlers --------------------

    def _total_spend(self, df):
        return int(df["amount"].sum())

    def _list_transactions(self, df):
        return df[["date", "amount", "category", "merchant"]].to_dict(
            orient="records"
        )

    def _top_category(self, df):
        if df.empty:
            return None
        grouped = df.groupby("category")["amount"].sum()
        return grouped.idxmax()

    def _compare_periods(self, df):
        if df.empty:
            return {}

        df["month"] = df["date"].dt.to_period("M")
        comparison = df.groupby("month")["amount"].sum()

        return {
            str(month): int(amount)
            for month, amount in comparison.items()
        }

    def _average_spend(self, df):
        if df.empty:
            return 0
        return float(df["amount"].mean())
