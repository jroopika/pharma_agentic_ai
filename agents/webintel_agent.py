import json
from pathlib import Path
from typing import List


class WebIntelAgent:
    """Summarizes literature samples from a local JSON file.

    This is a mock of a web intelligence agent that would call an LLM in a real system.
    """

    def __init__(self, data_path: str | Path | None = None):
        base = Path(__file__).parents[1]
        self.data_path = Path(data_path) if data_path else base / "data" / "literature_samples.json"
        self.articles: List[dict] = []
        self._load()

    def _load(self):
        try:
            with open(self.data_path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
                self.articles = payload.get("articles", [])
        except Exception:
            self.articles = []

    def summarize_for_drug(self, drug_name: str) -> dict:
        # naive: return combined abstracts and a short synthesized summary
        relevant = [a for a in self.articles if drug_name.lower() in (a.get("title", "") + " " + a.get("abstract", "")).lower()]
        combined = "\n\n".join([f"{a.get('title')} ({a.get('year')}): {a.get('abstract')}" for a in relevant])
        # produce a short mock summary
        if not relevant:
            summary = f"No literature matches found for {drug_name}."
        else:
            summary = (
                f"Found {len(relevant)} article(s). Preclinical and epidemiological signals suggest {drug_name} modulates metabolic pathways (AMPK/mTOR)"
            )
        return {"drug": drug_name, "count": len(relevant), "summary": summary, "combined": combined, "matches": relevant}


if __name__ == "__main__":
    w = WebIntelAgent()
    print(w.summarize_for_drug("Metformin"))
