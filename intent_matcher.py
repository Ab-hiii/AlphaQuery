from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class IntentMatcher:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.intent_templates = {
            "total_spend": [
                "how much did i spend",
                "total spending",
                "total expenses",
                "how much money did i spend",
                "spend on"
            ],
            "list_transactions": [
                "show my",
                "show all",
                "list my",
                "list all",
                "show expenses",
                "show purchases",
                "show transactions"
            ],
            "top_category": [
                "highest spending category",
                "biggest expense",
                "most spent on",
                "top spending category"
            ],
            "compare_periods": [
                "compare my spending",
                "compare expenses",
                "versus",
                "vs"
            ],
            "average_spend": [
                "average spending",
                "average expense",
                "average spend"
            ]
        }

        self.intent_names = list(self.intent_templates.keys())

        all_phrases = []
        self.phrase_to_intent = []

        for intent, phrases in self.intent_templates.items():
            for p in phrases:
                all_phrases.append(p)
                self.phrase_to_intent.append(intent)

        self.template_embeddings = self.model.encode(all_phrases)

    def match_intent(self, query):
        query_emb = self.model.encode([query])
        sims = cosine_similarity(query_emb, self.template_embeddings)[0]

        best_idx = int(np.argmax(sims))
        best_intent = self.phrase_to_intent[best_idx]
        best_score = float(sims[best_idx])

        return {
            "intent": best_intent,
            "score": round(best_score, 3)
        }
