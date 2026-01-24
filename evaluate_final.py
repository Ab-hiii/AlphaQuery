import json
from intent_matcher import IntentMatcher
from entity_extractor import EntityExtractor
from date_parser import DateParser

CHECK = "✅"
CROSS = "❌"

def load_tests(path="data/test_cases.json"):
    with open(path) as f:
        return json.load(f)

def fmt(val):
    return "None" if val is None else str(val)

if __name__ == "__main__":
    matcher = IntentMatcher()
    extractor = EntityExtractor()
    parser = DateParser()

    tests = load_tests()
    passed = 0

    print("\nFINAL SYSTEM EVALUATION")
    print("=" * 100)

    for t in tests:
        query = t["query"]
        expected_intent = t["intent"]
        expected_category = t.get("category")
        expected_merchant = t.get("merchant")
        date_required = t.get("date_required", False)

        intent_result = matcher.match_intent(query)
        entities = extractor.extract(query)
        start_date, end_date = parser.parse(query)

        # ---- checks ----
        intent_ok = intent_result["intent"] == expected_intent

        category_ok = True
        if expected_category is not None:
            category_ok = entities.get("category") == expected_category

        merchant_ok = True
        if expected_merchant is not None:
            merchant_ok = entities.get("merchant") == expected_merchant

        date_ok = True
        if date_required:
            date_ok = start_date is not None or end_date is not None

        all_ok = intent_ok and category_ok and merchant_ok and date_ok
        if all_ok:
            passed += 1

        # ---- output ----
        print(f"{t['id']:02d}. {query}")

        print(
            f"    Intent    : "
            f"{CHECK if intent_ok else CROSS} "
            f"(expected={expected_intent}, predicted={intent_result['intent']})"
        )

        if expected_category is not None:
            print(
                f"    Category  : "
                f"{CHECK if category_ok else CROSS} "
                f"(expected={expected_category}, predicted={fmt(entities.get('category'))})"
            )

        if expected_merchant is not None:
            print(
                f"    Merchant  : "
                f"{CHECK if merchant_ok else CROSS} "
                f"(expected={expected_merchant}, predicted={fmt(entities.get('merchant'))})"
            )

        print(
            f"    Date      : "
            f"{CHECK if date_ok else CROSS} "
            f"(parsed={start_date} → {end_date})"
        )

        print(
            f"    Amount    : "
            f"{fmt(entities.get('amount'))}"
        )

        print(
            f"    RESULT    : "
            f"{CHECK if all_ok else CROSS}"
        )

        print("-" * 100)

    print("\nSUMMARY")
    print("=" * 100)
    print(f"PASSED {passed} / {len(tests)} TEST CASES")
    print("=" * 100)
