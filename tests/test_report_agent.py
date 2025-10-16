import pytest
import tempfile
from pathlib import Path
from agents.report_agent import ReportAgent


class TestReportAgent:
    
    def test_init_default_path(self):
        agent = ReportAgent()
        # Should create default path relative to project structure
        assert agent.out_dir.name == "reports"
    
    def test_init_custom_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = Path(temp_dir) / "custom_reports"
            agent = ReportAgent(out_dir=custom_path)
            assert agent.out_dir == custom_path
            assert agent.out_dir.exists()  # Should be created
    
    def test_generate_pdf_basic(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            agent = ReportAgent(out_dir=temp_dir)
            
            title = "Test Report"
            sections = {
                "Section 1": "Content for section 1",
                "Section 2": "Content for section 2"
            }
            
            pdf_path = agent.generate_pdf(title, sections, "test_report.pdf")
            
            assert pdf_path.exists()
            assert pdf_path.name == "test_report.pdf"
            assert pdf_path.stat().st_size > 0  # File should have content
    
    def test_generate_pdf_auto_filename(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            agent = ReportAgent(out_dir=temp_dir)
            
            title = "Auto Named Report"
            sections = {"Test": "Test content"}
            
            pdf_path = agent.generate_pdf(title, sections)
            
            assert pdf_path.exists()
            assert pdf_path.name.startswith("report_")
            assert pdf_path.name.endswith(".pdf")
    
    def test_generate_pdf_complex_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            agent = ReportAgent(out_dir=temp_dir)
            
            title = "Complex Report"
            sections = {
                "Clinical Summary": {
                    "count": 5,
                    "phases": {"Phase 2": 3, "Phase 3": 2}
                },
                "Patent Analysis": "Multiple patents found with varying status",
                "Long Content": "This is a very long piece of content that should test the wrapping functionality of the PDF generator. " * 10
            }
            
            pdf_path = agent.generate_pdf(title, sections, "complex_report.pdf")
            
            assert pdf_path.exists()
            assert pdf_path.stat().st_size > 1000  # Should be substantial size