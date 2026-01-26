# Expense NLP API Contract

## Base URL
http://127.0.0.1:8000

---

## Endpoint

### GET /query

Processes a natural language expense query and returns structured results.

---

## Query Parameters

| Name | Type | Required | Description |
|----|----|----|----|
| q | string | Yes | Natural language expense query |

---

## Example Request

GET /query?q=How much did I spend on food last month?

---

## Example Response

```json
{
  "query": "How much did I spend on food last month?",
  "intent": {
    "intent": "total_spend",
    "score": 0.62
  },
  "entities": {
    "category": "food",
    "merchant": null,
    "amount": null
  },
  "start_date": "2025-12-01T00:00:00",
  "end_date": "2025-12-31T23:59:59",
  "result": 4500
}