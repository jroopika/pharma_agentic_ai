import pytest
import json
import tempfile
from pathlib import Path
from agents.market_agent import MarketAgent


@pytest.fixture
def mock_market_data():
    return {
        "market_insights": {
            "segment": "Test therapeutic area",
            "gap_score": 7.5,
            "rationale": "High unmet need in test area",
            "estimated_addressable_market_usd_m": 250,
            "key_competitors": ["CompetitorA", "CompetitorB"],
            "payer_pressure": "Low",
            "recommended_strategy": "Fast-track development approach"
        }
    }


@pytest.fixture
def temp_market_file(mock_market_data):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_market_data, f)
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink()


class TestMarketAgent:
    
    def test_load_valid_data(self, temp_market_file):
        agent = MarketAgent(data_path=temp_market_file)
        assert agent.data["market_insights"]["segment"] == "Test therapeutic area"
        assert agent.data["market_insights"]["gap_score"] == 7.5
    
    def test_load_missing_file(self):
        agent = MarketAgent(data_path="nonexistent.json")
        assert agent.data == {}
    
    def test_get_market_insight_default(self, temp_market_file):
        agent = MarketAgent(data_path=temp_market_file)
        insight = agent.get_market_insight()
        
        assert insight["segment"] == "Test therapeutic area"
        assert insight["gap_score"] == 7.5
        assert insight["estimated_addressable_market_usd_m"] == 250
        assert "note" not in insight
    
    def test_get_market_insight_matching_segment(self, temp_market_file):
        agent = MarketAgent(data_path=temp_market_file)
        insight = agent.get_market_insight("Test therapeutic area")
        
        assert insight["segment"] == "Test therapeutic area"
        assert "note" not in insight
    
    def test_get_market_insight_non_matching_segment(self, temp_market_file):
        agent = MarketAgent(data_path=temp_market_file)
        insight = agent.get_market_insight("Different segment")
        
        assert insight["segment"] == "Test therapeutic area"  # Still returns default
        assert "note" in insight
        assert "Different segment" in insight["note"]
    
    def test_get_market_insight_empty_data(self):
        agent = MarketAgent(data_path="nonexistent.json")
        insight = agent.get_market_insight()
        assert insight == {}