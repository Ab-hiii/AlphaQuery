from fastapi import FastAPI
from intent_matcher import IntentMatcher
from entity_extractor import EntityExtractor
from date_parser import DateParser
from executor import Executor

app = FastAPI(title="Expense NLP API")

# Initialize backend components once
intent_matcher = IntentMatcher()
entity_extractor = EntityExtractor()
date_parser = DateParser()
executor = Executor()


@app.get("/query")
def process_query(q: str):
    """
    Process a natural language expense query and return structured output.
    """

    intent_result = intent_matcher.match_intent(q)
    entities = entity_extractor.extract(q)
    start_date, end_date = date_parser.parse(q)

    result = executor.execute(
        intent=intent_result["intent"],
        entities=entities,
        start_date=start_date,
        end_date=end_date
    )

    return {
        "query": q,
        "intent": intent_result,
        "entities": entities,
        "start_date": start_date,
        "end_date": end_date,
        "result": result
    }
