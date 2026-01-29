import sys
import os
from pprint import pprint

# --------------------------------------------------
# Add project root to Python path
# --------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --------------------------------------------------
# Imports now work reliably
# --------------------------------------------------
from core.intent_matcher import IntentMatcher
from core.entity_extractor import EntityExtractor
from core.date_parser import DateParser
from core.executor import Executor
from evaluation.query_validator import QueryValidator


def fmt(dt):
    return None if dt is None else dt.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    matcher = IntentMatcher()
    extractor = EntityExtractor()
    parser = DateParser()
    executor = Executor("data/transactions.csv")
    validator = QueryValidator("data/transactions.csv")

    TEST_QUERIES = [
        "What is my biggest expense category?",
        "How much did I spend on travel?",
        "How much did I spend on food in February 2025?",
        "Show my Uber transactions in March 2025",
        "Compare my spending in January and February 2025",
        "Show my Starbucks transactions"
    ]

    for query in TEST_QUERIES:
        print("=" * 100)
        print(f"QUERY: {query}\n")

        intent = matcher.match_intent(query)
        entities = extractor.extract(query)
        start_date, end_date = parser.parse(query)

        result = executor.execute(
            intent=intent["intent"],
            entities=entities,
            start_date=start_date,
            end_date=end_date
        )

        print("🧠 SYSTEM UNDERSTANDING")
        pprint({
            "intent": intent,
            "entities": entities,
            "date_range": {
                "start": fmt(start_date),
                "end": fmt(end_date)
            }
        }, sort_dicts=False)

        print("\n📊 RESULT")
        pprint(result, sort_dicts=False)

        warnings = validator.validate(
            entities, start_date, end_date, result
        )

        if warnings:
            print("\n⚠️ VALIDATION WARNINGS")
            for w in warnings:
                print(w)
        else:
            print("\n✅ Result looks semantically correct")

        print("=" * 100 + "\n")