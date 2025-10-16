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
        insights = self.data.get("market_insights", [])
        
        # Handle both old format (single dict) and new format (array)
        if isinstance(insights, dict):
            insights = [insights]
        
        if not segment:
            # Return first insight if no segment specified
            return insights[0] if insights else {}
        
        # Search for matching segment
        for insight in insights:
            if insight.get("segment", "").lower() == segment.lower():
                return insight
        
        # If no match found, return first with a note
        if insights:
            mi = insights[0].copy()
            mi["note"] = f"Requested segment '{segment}' not found; returning '{mi.get('segment', 'default')}'."
            return mi
        
        return {}


if __name__ == "__main__":
    ma = MarketAgent()
    print(ma.get_market_insight())
