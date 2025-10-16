import json
from pathlib import Path


class ClinicalAgent:
    """Reads clinical trial mock data and provides simple search/summarize helpers."""

    def __init__(self, data_path: str | Path | None = None):
        base = Path(__file__).parents[1]
        self.data_path = Path(data_path) if data_path else base / "data" / "clinical_trials.json"
        self.trials = []
        self._load()

    def _load(self):
        try:
            with open(self.data_path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
                self.trials = payload.get("trials", [])
        except Exception:
            self.trials = []

    def find_trials_for_drug(self, drug_name: str):
        return [t for t in self.trials if t.get("drug", "").lower() == drug_name.lower()]

    def summarize_trials(self, drug_name: str):
        trials = self.find_trials_for_drug(drug_name)
        summary = {
            "drug": drug_name,
            "count": len(trials),
            "phases": {},
            "statuses": {},
            "examples": trials[:3],
        }
        for t in trials:
            p = t.get("phase") or "unknown"
            summary["phases"][p] = summary["phases"].get(p, 0) + 1
            s = t.get("status") or "unknown"
            summary["statuses"][s] = summary["statuses"].get(s, 0) + 1
        return summary


if __name__ == "__main__":
    ca = ClinicalAgent()
    print(ca.summarize_trials("Metformin"))
