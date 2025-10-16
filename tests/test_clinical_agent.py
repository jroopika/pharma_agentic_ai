import pytest
import json
import tempfile
from pathlib import Path
from agents.clinical_agent import ClinicalAgent


@pytest.fixture
def mock_clinical_data():
    return {
        "trials": [
            {
                "id": "TEST001",
                "drug": "TestDrug",
                "indication": "Test Indication",
                "phase": "Phase 2",
                "status": "Completed",
                "summary": "Test summary",
                "results": "Test results",
                "start_date": "2020-01-01",
                "end_date": "2021-01-01"
            },
            {
                "id": "TEST002",
                "drug": "TestDrug",
                "indication": "Another Indication",
                "phase": "Phase 3",
                "status": "Active",
                "summary": "Another test summary",
                "results": "Another test results",
                "start_date": "2021-01-01",
                "end_date": None
            },
            {
                "id": "TEST003",
                "drug": "OtherDrug",
                "indication": "Other Indication",
                "phase": "Phase 1",
                "status": "Terminated",
                "summary": "Other summary",
                "results": "Other results",
                "start_date": "2019-01-01",
                "end_date": "2020-01-01"
            }
        ]
    }


@pytest.fixture
def temp_clinical_file(mock_clinical_data):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_clinical_data, f)
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink()


class TestClinicalAgent:
    
    def test_load_valid_data(self, temp_clinical_file):
        agent = ClinicalAgent(data_path=temp_clinical_file)
        assert len(agent.trials) == 3
        assert agent.trials[0]["drug"] == "TestDrug"
    
    def test_load_missing_file(self):
        agent = ClinicalAgent(data_path="nonexistent.json")
        assert agent.trials == []
    
    def test_find_trials_for_drug_exists(self, temp_clinical_file):
        agent = ClinicalAgent(data_path=temp_clinical_file)
        trials = agent.find_trials_for_drug("TestDrug")
        assert len(trials) == 2
        assert all(t["drug"] == "TestDrug" for t in trials)
    
    def test_find_trials_for_drug_case_insensitive(self, temp_clinical_file):
        agent = ClinicalAgent(data_path=temp_clinical_file)
        trials = agent.find_trials_for_drug("testdrug")
        assert len(trials) == 2
    
    def test_find_trials_for_drug_not_exists(self, temp_clinical_file):
        agent = ClinicalAgent(data_path=temp_clinical_file)
        trials = agent.find_trials_for_drug("NonExistentDrug")
        assert trials == []
    
    def test_summarize_trials(self, temp_clinical_file):
        agent = ClinicalAgent(data_path=temp_clinical_file)
        summary = agent.summarize_trials("TestDrug")
        
        assert summary["drug"] == "TestDrug"
        assert summary["count"] == 2
        assert summary["phases"]["Phase 2"] == 1
        assert summary["phases"]["Phase 3"] == 1
        assert summary["statuses"]["Completed"] == 1
        assert summary["statuses"]["Active"] == 1
        assert len(summary["examples"]) == 2
    
    def test_summarize_trials_empty(self, temp_clinical_file):
        agent = ClinicalAgent(data_path=temp_clinical_file)
        summary = agent.summarize_trials("NonExistentDrug")
        
        assert summary["drug"] == "NonExistentDrug"
        assert summary["count"] == 0
        assert summary["phases"] == {}
        assert summary["statuses"] == {}
        assert summary["examples"] == []