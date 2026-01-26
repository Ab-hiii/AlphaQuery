import re
from rapidfuzz import process, fuzz


class EntityExtractor:
    CATEGORY_KEYWORDS = {
        "rent": ["rent", "rental", "landlord"],
        "cafe": ["coffee", "cafe", "cafes"],
        "grocery": ["grocery", "groceries", "bigbasket", "instamart"],
        "food": ["food", "meal", "lunch", "dinner", "swiggy", "zomato"],
        "transport": ["transport", "travel", "uber", "ola", "cab"],
        "utilities": ["utilities", "bill", "electricity", "water", "internet"],
        "subscriptions": ["subscription", "subscriptions", "netflix", "spotify"],
        "entertainment": ["entertainment", "movie", "concert"],
        "gifts": ["gift", "gifts"],
        "shopping": ["shopping", "purchase", "amazon", "flipkart"]
    }

    MERCHANT_CATEGORY_MAP = {
        "starbucks": "cafe",
        "ccd": "cafe",
        "swiggy": "food",
        "zomato": "food",
        "dominos": "food",
        "uber": "transport",
        "ola": "transport",
        "amazon": "shopping",
        "flipkart": "shopping",
        "myntra": "shopping",
        "bigbasket": "grocery",
        "instamart": "grocery",
        "netflix": "subscriptions",
        "spotify": "subscriptions",
        "bookmyshow": "entertainment",
        "makemytrip": "travel",
    }

    def __init__(self, merchant_path="data/merchants.txt"):
        with open(merchant_path) as f:
            self.merchants = [m.strip().lower() for m in f if m.strip()]

    def extract(self, query: str):
        q = query.lower()
        tokens = re.findall(r"[a-zA-Z]+", q)

        category = None
        merchant = None
        amount = None

        for cat, kws in self.CATEGORY_KEYWORDS.items():
            if any(k in q for k in kws):
                category = cat
                break

        for m in self.merchants:
            if m in q:
                merchant = m
                break

        if not merchant:
            for token in tokens:
                if len(token) < 6:
                    continue

                match, score, _ = process.extractOne(
                    token, self.merchants, scorer=fuzz.ratio
                ) or (None, 0, None)

                if score >= 88:
                    merchant = match
                    break

        if merchant and not category:
            category = self.MERCHANT_CATEGORY_MAP.get(merchant)

        m = re.search(r"(above|over|greater than|>=)\s*(\d+)", q)
        if m:
            amount = int(m.group(2))

        return {
            "category": category,
            "merchant": merchant,
            "amount": amount
        }