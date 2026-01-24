# AlphaQuery
# Expense NLP System

A hybrid NLP backend for understanding natural language expense queries.

## Features
- ML-based semantic intent matching using sentence-transformers
- Rule-based entity extraction (categories, merchants, amounts)
- Rule-based date parsing
- Deterministic execution using pandas
- Fully evaluated with curated test cases (50/50 passing)

## Architecture
Query  
→ Intent Detection (ML embeddings)  
→ Entity & Date Extraction (rules)  
→ Pandas Execution Engine  
→ Structured Output

## Example Query
