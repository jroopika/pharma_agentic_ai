import pytest
import json
import tempfile
from pathlib import Path
from agents.patent_agent import PatentAgent


@pytest.fixture
def mock_patent_data():
    return {
        "patents": [
            {
                "patent_id": "US123456A1",
                "title": "TestDrug compositions and methods",
                "assignee": "TestCorp",
                "status": "Active",
                "claims_summary": "Compositions containing TestDrug for various conditions",
                "relevance": "Directly covers TestDrug usage"
            },
            {
                "patent_id": "US789012A1",
                "title": "Novel pharmaceutical formulations",
                "assignee": "BigPharma",
                "status": "Expired",
                "claims_summary": "General pharmaceutical formulations including TestDrug derivatives",
                "relevance": "Derivative compounds only"
            },
            {
                "patent_id": "WO2020001234A1",
                "title": "Cancer treatment methods",
                "assignee": "SmallBio",
                "status": "Abandoned",
                "claims_summary": "Methods for treating cancer with various compounds",
                "relevance": "No specific TestDrug claims"
            }
        ]
    }


@pytest.fixture
def temp_patent_file(mock_patent_data):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_patent_data, f)
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink()


class TestPatentAgent:
    
    def test_load_valid_data(self, temp_patent_file):
        agent = PatentAgent(data_path=temp_patent_file)
        assert len(agent.patents) == 3
        assert agent.patents[0]["patent_id"] == "US123456A1"
    
    def test_load_missing_file(self):
        agent = PatentAgent(data_path="nonexistent.json")
        assert agent.patents == []
    
    def test_search_patents_for_drug_found(self, temp_patent_file):
        agent = PatentAgent(data_path=temp_patent_file)
        matches = agent.search_patents_for_drug("TestDrug")
        assert len(matches) == 2  # Should find patents with TestDrug in title or claims
    
    def test_search_patents_for_drug_case_insensitive(self, temp_patent_file):
        agent = PatentAgent(data_path=temp_patent_file)
        matches = agent.search_patents_for_drug("testdrug")
        assert len(matches) == 2
    
    def test_search_patents_for_drug_not_found(self, temp_patent_file):
        agent = PatentAgent(data_path=temp_patent_file)
        matches = agent.search_patents_for_drug("NonExistentDrug")
        assert matches == []
    
    def test_assess_opportunity_no_patents(self, temp_patent_file):
        agent = PatentAgent(data_path=temp_patent_file)
        assessment = agent.assess_opportunity("NonExistentDrug")
        
        assert assessment["drug"] == "NonExistentDrug"
        assert assessment["patent_coverage"] == "none_found"
        assert assessment["opportunity"] == "High"
    
    def test_assess_opportunity_with_active_patents(self, temp_patent_file):
        agent = PatentAgent(data_path=temp_patent_file)
        assessment = agent.assess_opportunity("TestDrug")
        
        assert assessment["drug"] == "TestDrug"
        assert assessment["opportunity"] == "Low"  # Has active patents
        assert len(assessment["matches"]) == 2
    
    def test_assess_opportunity_only_expired_patents(self, temp_patent_file, mock_patent_data):
        # Modify data to have only expired/abandoned patents
        mock_patent_data["patents"][0]["status"] = "Expired"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(mock_patent_data, f)
            temp_path = Path(f.name)
        
        try:
            agent = PatentAgent(data_path=temp_path)
            assessment = agent.assess_opportunity("TestDrug")
            assert assessment["opportunity"] == "Medium"  # No active patents
        finally:
            temp_path.unlink()