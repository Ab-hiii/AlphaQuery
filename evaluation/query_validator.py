import pandas as pd


class QueryValidator:
    """
    Validates whether a query result is semantically reasonable
    with respect to the dataset.
    """

    def __init__(self, csv_path="data/transactions.csv"):
        self.df = pd.read_csv(csv_path)
        self.df["date"] = pd.to_datetime(self.df["date"])

        self.min_date = self.df["date"].min()
        self.max_date = self.df["date"].max()
        self.categories = set(self.df["category"].unique())

    def validate(self, entities, start_date, end_date, result):
        warnings = []

        # 1. Date range sanity
        if start_date and end_date:
            if start_date > self.max_date or end_date < self.min_date:
                warnings.append(
                    "⚠️ Parsed date range is outside dataset range"
                )

        # 2. Category mismatch
        cat = entities.get("category")
        if cat and cat not in self.categories:
            warnings.append(
                f"⚠️ Category '{cat}' not present in dataset categories {self.categories}"
            )

        # 3. Suspicious zero result
        if isinstance(result, (int, float)) and result == 0:
            warnings.append(
                "⚠️ Result is zero — check filters or date alignment"
            )

        if isinstance(result, list) and len(result) == 0:
            warnings.append(
                "⚠️ Empty result set — may indicate over-filtering"
            )

        return warnings