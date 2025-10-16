import json
from pathlib import Path


class MarketAgent:
    """Reads market_data.json and returns simple market insights."""

    def __init__(self, data_path: str | Path | None = None):
        base = Path(__file__).parents[1]
        self.data_path = Path(data_path) if data_path else base / "data" / "market_data.json"
        self.data = {}
        self._load()

    def _load(self):
        try:
            with open(self.data_path, "r", encoding="utf-8") as fh:
                self.data = json.load(fh)
        except Exception:
            self.data = {}

    def get_market_insight(self, segment: str | None = None):
        mi = self.data.get("market_insights", {})
        if segment and mi.get("segment", "").lower() != segment.lower():
            # if segment mismatch, return the stored insight with a note
            mi = {**mi, "note": f"Requested segment '{segment}' not found; returning default."}
        return mi


if __name__ == "__main__":
    ma = MarketAgent()
    print(ma.get_market_insight())
