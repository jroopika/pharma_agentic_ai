import json
from pathlib import Path


class PatentAgent:
    """Simple patent landscape agent that inspects mock patents.json."""

    def __init__(self, data_path: str | Path | None = None):
        base = Path(__file__).parents[1]
        self.data_path = Path(data_path) if data_path else base / "data" / "patents.json"
        self.patents = []
        self._load()

    def _load(self):
        try:
            with open(self.data_path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
                self.patents = payload.get("patents", [])
        except Exception:
            self.patents = []

    def search_patents_for_drug(self, drug_name: str):
        # naive string match against title and claims
        matches = []
        for p in self.patents:
            text = (p.get("title", "") + " " + p.get("claims_summary", "")).lower()
            if drug_name.lower() in text:
                matches.append(p)
        return matches

    def assess_opportunity(self, drug_name: str):
        matches = self.search_patents_for_drug(drug_name)
        if not matches:
            return {"drug": drug_name, "patent_coverage": "none_found", "opportunity": "High"}
        # check statuses
        statuses = {p.get("status"): 0 for p in matches}
        for p in matches:
            statuses[p.get("status")] = statuses.get(p.get("status"), 0) + 1
        # simple heuristic
        active = any(p.get("status", "").lower() in ("active", "granted") for p in matches)
        opportunity = "Low" if active else "Medium"
        return {"drug": drug_name, "patent_coverage": statuses, "opportunity": opportunity, "matches": matches}


if __name__ == "__main__":
    pa = PatentAgent()
    print(pa.assess_opportunity("Metformin"))
