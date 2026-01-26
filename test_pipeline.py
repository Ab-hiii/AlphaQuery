from core.intent_matcher import IntentMatcher
from core.entity_extractor import EntityExtractor
from core.date_parser import DateParser
from core.executor import Executor



def load_test_queries(path="data/test_queries.txt"):
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def run_query(query: str, intent_matcher, extractor, parser, executor):
    print(f"USER QUERY: {query}")
    print("-" * 60)

    intent_result = intent_matcher.match_intent(query)
    intent = intent_result["intent"]

    print("Intent Detection")
    print(f"  Intent: {intent}")
    print(f"  Similarity Score: {intent_result['score']:.4f}")
    print(f"  Margin: {intent_result['margin']:.4f}\n")

    entities = extractor.extract(query)
    print("Entity Extraction")
    print(entities, "\n")

    start_date, end_date = parser.parse(query)
    print("Date Parsing")
    print(f"  Start: {start_date}, End: {end_date}\n")

    result = executor.execute(intent, entities, start_date, end_date)
    print("Execution Result")
    print(result)
    print("=" * 80, "\n")


if __name__ == "__main__":
    intent_matcher = IntentMatcher()
    extractor = EntityExtractor()
    parser = DateParser()
    executor = Executor()

    queries = load_test_queries()

    for q in queries:
        run_query(q, intent_matcher, extractor, parser, executor)
