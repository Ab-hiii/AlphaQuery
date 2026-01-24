import json
import re


class EntityExtractor:
    """
    Rule-based entity extractor with deterministic conflict resolution
    and category normalization.
    """

    # Semantic normalization map
    CATEGORY_NORMALIZATION = {
        "travel": "transport"
    }

    def __init__(
        self,
        category_path="data/categories.json",
        merchant_path="data/merchants.txt"
    ):
        with open(category_path, "r") as f:
            self.categories = json.load(f)

        with open(merchant_path, "r") as f:
            self.merchants = [line.strip().lower() for line in f if line.strip()]

        self.amount_pattern = re.compile(r"\b\d+\b")

    def extract(self, query: str):
        query_lower = query.lower()

        category = None
        merchant = None
        amount = None

        # -------------------- CATEGORY DETECTION --------------------
        category_scores = {}

        for cat, keywords in self.categories.items():
            exact_match = 1 if cat in query_lower else 0
            keyword_hits = 0
            longest_kw = 0

            for kw in keywords:
                if kw in query_lower:
                    keyword_hits += 1
                    longest_kw = max(longest_kw, len(kw))

            if exact_match or keyword_hits:
                category_scores[cat] = (
                    exact_match,
                    keyword_hits,
                    longest_kw
                )

        if category_scores:
            category = sorted(
                category_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[0][0]

        # -------------------- CATEGORY NORMALIZATION --------------------
        if category in self.CATEGORY_NORMALIZATION:
            category = self.CATEGORY_NORMALIZATION[category]

        # -------------------- MERCHANT DETECTION --------------------
        for m in self.merchants:
            if m in query_lower:
                merchant = m
                break

        # -------------------- AMOUNT DETECTION --------------------
        match = self.amount_pattern.search(query_lower)
        if match:
            amount = int(match.group())

        return {
            "category": category,
            "merchant": merchant,
            "amount": amount
        }
