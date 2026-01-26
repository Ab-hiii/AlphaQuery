import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class IntentMatcher:
    def __init__(self, templates_path="data/intent_templates.json"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        with open(templates_path) as f:
            self.intent_templates = json.load(f)

        all_phrases = []
        self.phrase_to_intent = []

        for intent, phrases in self.intent_templates.items():
            for p in phrases:
                all_phrases.append(p)
                self.phrase_to_intent.append(intent)

        self.template_embeddings = self.model.encode(all_phrases)

    def match_intent(self, query):
        query_lower = query.lower()
        query_emb = self.model.encode([query_lower])
        sims = cosine_similarity(query_emb, self.template_embeddings)[0]

        best_idx = int(np.argmax(sims))
        best_intent = self.phrase_to_intent[best_idx]
        best_score = float(sims[best_idx])

        if best_intent == "list_transactions":
            if any(w in query_lower for w in ["show", "list"]):
                best_score = max(best_score, 0.55)

        return {
            "intent": best_intent,
            "score": round(best_score, 3)
        }