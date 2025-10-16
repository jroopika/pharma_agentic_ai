import pytest
import json
import tempfile
from pathlib import Path
from agents.webintel_agent import WebIntelAgent


@pytest.fixture
def mock_literature_data():
    return {
        "articles": [
            {
                "pmid": "12345678",
                "title": "TestDrug mechanisms in cellular pathways",
                "abstract": "This study investigates how TestDrug modulates key cellular signaling pathways involved in disease progression.",
                "year": 2020
            },
            {
                "pmid": "87654321",
                "title": "Clinical outcomes with TestDrug therapy",
                "abstract": "A comprehensive analysis of clinical outcomes in patients treated with TestDrug showing promising results.",
                "year": 2021
            },
            {
                "pmid": "11111111",
                "title": "Novel approaches in cancer treatment",
                "abstract": "This paper explores various novel therapeutic approaches for cancer treatment including innovative compounds.",
                "year": 2019
            }
        ]
    }


@pytest.fixture
def temp_literature_file(mock_literature_data):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_literature_data, f)
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink()


class TestWebIntelAgent:
    
    def test_load_valid_data(self, temp_literature_file):
        agent = WebIntelAgent(data_path=temp_literature_file)
        assert len(agent.articles) == 3
        assert agent.articles[0]["pmid"] == "12345678"
    
    def test_load_missing_file(self):
        agent = WebIntelAgent(data_path="nonexistent.json")
        assert agent.articles == []
    
    def test_summarize_for_drug_found(self, temp_literature_file):
        agent = WebIntelAgent(data_path=temp_literature_file)
        summary = agent.summarize_for_drug("TestDrug")
        
        assert summary["drug"] == "TestDrug"
        assert summary["count"] == 2  # Should find 2 articles mentioning TestDrug
        assert len(summary["matches"]) == 2
        assert "TestDrug modulates metabolic pathways" in summary["summary"]
        assert "mechanisms" in summary["combined"]
        assert "clinical outcomes" in summary["combined"]
    
    def test_summarize_for_drug_case_insensitive(self, temp_literature_file):
        agent = WebIntelAgent(data_path=temp_literature_file)
        summary = agent.summarize_for_drug("testdrug")
        
        assert summary["count"] == 2
        assert len(summary["matches"]) == 2
    
    def test_summarize_for_drug_not_found(self, temp_literature_file):
        agent = WebIntelAgent(data_path=temp_literature_file)
        summary = agent.summarize_for_drug("NonExistentDrug")
        
        assert summary["drug"] == "NonExistentDrug"
        assert summary["count"] == 0
        assert summary["matches"] == []
        assert "No literature matches found" in summary["summary"]
        assert summary["combined"] == ""
    
    def test_summarize_for_drug_empty_data(self):
        agent = WebIntelAgent(data_path="nonexistent.json")
        summary = agent.summarize_for_drug("TestDrug")
        
        assert summary["count"] == 0
        assert summary["matches"] == []
        assert "No literature matches found" in summary["summary"]