from .clinical_agent import ClinicalAgent
from .patent_agent import PatentAgent
from .market_agent import MarketAgent
from .webintel_agent import WebIntelAgent
from .report_agent import ReportAgent


class MasterAgent:
    """Orchestrates sub-agents to create a combined analysis and report."""

    def __init__(self):
        self.clinical = ClinicalAgent()
        self.patent = PatentAgent()
        self.market = MarketAgent()
        self.web = WebIntelAgent()
        self.reporter = ReportAgent()

    def analyze(self, drug_name: str) -> dict:
        clinical_summary = self.clinical.summarize_trials(drug_name)
        patent_assess = self.patent.assess_opportunity(drug_name)
        market_insight = self.market.get_market_insight()
        literature = self.web.summarize_for_drug(drug_name)

        conclusion = (
            f"{drug_name} shows signals from preclinical and epidemiology; clinical trials exist in oncology-related indications. "
            f"Patent coverage appears {patent_assess.get('opportunity')}. Market gap score: {market_insight.get('gap_score')}"
        )

        sections = {
            "Clinical Trials Summary": clinical_summary,
            "Patent Landscape": patent_assess,
            "Market Insight": market_insight,
            "Literature Synthesis": literature.get("summary"),
            "Conclusion": conclusion,
        }

        report_path = self.reporter.generate_pdf(f"{drug_name} — Oncology Repurposing Potential", sections)

        return {"drug": drug_name, "sections": sections, "report_path": str(report_path)}


if __name__ == "__main__":
    m = MasterAgent()
    out = m.analyze("Metformin")
    print(out)
