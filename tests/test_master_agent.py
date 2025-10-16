import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from agents.master_agent import MasterAgent


class TestMasterAgent:
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory with mock data files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            data_dir.mkdir()
            
            # Create mock data files
            clinical_data = {
                "trials": [{
                    "id": "TEST001",
                    "drug": "TestDrug",
                    "indication": "Test Disease",
                    "phase": "Phase 2",
                    "status": "Completed"
                }]
            }
            
            patent_data = {
                "patents": [{
                    "patent_id": "US123456",
                    "title": "TestDrug methods",
                    "status": "Expired"
                }]
            }
            
            market_data = {
                "market_insights": {
                    "segment": "Test area",
                    "gap_score": 8.0
                }
            }
            
            literature_data = {
                "articles": [{
                    "pmid": "12345",
                    "title": "TestDrug mechanisms",
                    "abstract": "TestDrug shows promise"
                }]
            }
            
            # Write files
            with open(data_dir / "clinical_trials.json", "w") as f:
                json.dump(clinical_data, f)
            with open(data_dir / "patents.json", "w") as f:
                json.dump(patent_data, f)
            with open(data_dir / "market_data.json", "w") as f:
                json.dump(market_data, f)
            with open(data_dir / "literature_samples.json", "w") as f:
                json.dump(literature_data, f)
            
            yield temp_dir
    
    @patch('agents.master_agent.ClinicalAgent')
    @patch('agents.master_agent.PatentAgent')
    @patch('agents.master_agent.MarketAgent')
    @patch('agents.master_agent.WebIntelAgent')
    @patch('agents.master_agent.ReportAgent')
    def test_master_agent_init(self, mock_report, mock_web, mock_market, mock_patent, mock_clinical):
        """Test MasterAgent initialization"""
        agent = MasterAgent()
        
        # Verify all sub-agents are created
        mock_clinical.assert_called_once()
        mock_patent.assert_called_once()
        mock_market.assert_called_once()
        mock_web.assert_called_once()
        mock_report.assert_called_once()
    
    def test_analyze_integration(self, temp_data_dir):
        """Test the full analyze pipeline with real data"""
        # Mock the report generation to avoid file system dependencies
        with patch('agents.master_agent.ReportAgent') as mock_report_class:
            mock_report = MagicMock()
            mock_report.generate_pdf.return_value = Path("/fake/report.pdf")
            mock_report_class.return_value = mock_report
            
            # Patch data paths to use temp directory
            with patch('agents.clinical_agent.Path') as mock_path:
                mock_path.return_value.parents = [Path(temp_data_dir)]
                
                agent = MasterAgent()
                result = agent.analyze("TestDrug")
                
                # Verify structure
                assert "drug" in result
                assert "sections" in result
                assert "report_path" in result
                assert result["drug"] == "TestDrug"
                
                # Verify all expected sections are present
                expected_sections = [
                    "Clinical Trials Summary",
                    "Patent Landscape", 
                    "Market Insight",
                    "Literature Synthesis",
                    "Conclusion"
                ]
                
                for section in expected_sections:
                    assert section in result["sections"]
                
                # Verify report generation was called
                mock_report.generate_pdf.assert_called_once()
    
    @patch('agents.master_agent.ClinicalAgent')
    @patch('agents.master_agent.PatentAgent') 
    @patch('agents.master_agent.MarketAgent')
    @patch('agents.master_agent.WebIntelAgent')
    @patch('agents.master_agent.ReportAgent')
    def test_analyze_with_mocked_agents(self, mock_report_class, mock_web_class, mock_market_class, mock_patent_class, mock_clinical_class):
        """Test analyze method with fully mocked agents"""
        # Setup mock returns
        mock_clinical = MagicMock()
        mock_clinical.summarize_trials.return_value = {"count": 2, "drug": "TestDrug"}
        mock_clinical_class.return_value = mock_clinical
        
        mock_patent = MagicMock() 
        mock_patent.assess_opportunity.return_value = {"opportunity": "High", "drug": "TestDrug"}
        mock_patent_class.return_value = mock_patent
        
        mock_market = MagicMock()
        mock_market.get_market_insight.return_value = {"gap_score": 9.0}
        mock_market_class.return_value = mock_market
        
        mock_web = MagicMock()
        mock_web.summarize_for_drug.return_value = {"summary": "Promising signals"}
        mock_web_class.return_value = mock_web
        
        mock_report = MagicMock()
        mock_report.generate_pdf.return_value = Path("/test/report.pdf")
        mock_report_class.return_value = mock_report
        
        # Test
        agent = MasterAgent()
        result = agent.analyze("TestDrug")
        
        # Verify all agents were called
        mock_clinical.summarize_trials.assert_called_once_with("TestDrug")
        mock_patent.assess_opportunity.assert_called_once_with("TestDrug")
        mock_market.get_market_insight.assert_called_once()
        mock_web.summarize_for_drug.assert_called_once_with("TestDrug")
        mock_report.generate_pdf.assert_called_once()
        
        # Verify result structure
        assert result["drug"] == "TestDrug"
        assert result["report_path"] == "/test/report.pdf"