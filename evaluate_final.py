import json
from pprint import pprint
from intent_matcher import IntentMatcher
from entity_extractor import EntityExtractor
from date_parser import DateParser
from executor import Executor

CHECK = "✅"
CROSS = "❌"


def load_tests(path="data/test_cases.json"):
    with open(path) as f:
        return json.load(f)


def normalize_date(dt):
    if dt is None:
        return None
    return dt.isoformat()


def swagger_response(query, intent_result, entities, start_date, end_date, result):
    return {
        "query": query,
        "intent": intent_result,
        "entities": entities,
        "start_date": normalize_date(start_date),
        "end_date": normalize_date(end_date),
        "result": result
    }


def matches_expected(actual, expected):
    """
    Only validate fields that exist in expected test case.
    """
    # intent
    if actual["intent"]["intent"] != expected["intent"]:
        return False, "intent"

    # category
    if "category" in expected:
        if actual["entities"]["category"] != expected["category"]:
            return False, "category"

    # merchant
    if "merchant" in expected:
        if actual["entities"]["merchant"] != expected["merchant"]:
            return False, "merchant"

    # amount
    if "amount" in expected:
        if actual["entities"]["amount"] != expected["amount"]:
            return False, "amount"

    # date
    if expected.get("date_required", False):
        if actual["start_date"] is None or actual["end_date"] is None:
            return False, "date"

    return True, None


if __name__ == "__main__":
    matcher = IntentMatcher()
    extractor = EntityExtractor()
    parser = DateParser()
    executor = Executor()

    tests = load_tests()
    passed = 0

    print("\nFINAL SYSTEM EVALUATION (Swagger-aligned)")
    print("=" * 100)

    for t in tests:
        query = t["query"]

        intent_result = matcher.match_intent(query)
        entities = extractor.extract(query)
        start_date, end_date = parser.parse(query)
        result = executor.execute(
            intent_result["intent"],
            entities,
            start_date,
            end_date
        )

        actual = swagger_response(
            query,
            intent_result,
            entities,
            start_date,
            end_date,
            result
        )

        ok, failed_field = matches_expected(actual, t)

        print(f"{t['id']:02d}. {query}")
        pprint(actual, sort_dicts=False)

        if ok:
            print(f"\nRESULT: {CHECK} PASSED\n")
            passed += 1
        else:
            print(f"\nRESULT: {CROSS} FAILED → mismatch in `{failed_field}`\n")

        print("-" * 100)

    print("\nSUMMARY")
    print("=" * 100)
    print(f"PASSED {passed} / {len(tests)} TEST CASES")
    print("=" * 100)
