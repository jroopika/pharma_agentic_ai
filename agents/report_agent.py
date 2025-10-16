from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import tempfile
import json


class ReportAgent:
    """Enhanced PDF report generator with tables, charts, and improved formatting."""

    def __init__(self, out_dir: str | Path | None = None):
        base = Path(__file__).parents[1] 
        self.out_dir = Path(out_dir) if out_dir else base / "outputs" / "reports"
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.darkblue,
            spaceAfter=30,
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceAfter=12,
            spaceBefore=20
        ))

    def _create_phase_distribution_chart(self, phases_data: dict) -> str:
        """Create a pie chart for clinical trial phases."""
        if not phases_data:
            return None
            
        fig, ax = plt.subplots(figsize=(6, 4))
        phases = list(phases_data.keys())
        counts = list(phases_data.values())
        
        colors_list = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        
        ax.pie(counts, labels=phases, autopct='%1.1f%%', colors=colors_list)
        ax.set_title('Clinical Trial Phase Distribution')
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        plt.savefig(temp_file.name, dpi=150, bbox_inches='tight')
        plt.close()
        
        return temp_file.name

    def _create_trials_table(self, trials_data: list) -> Table:
        """Create a formatted table of clinical trials."""
        if not trials_data:
            return None
            
        headers = [['Trial ID', 'Indication', 'Phase', 'Status']]
        rows = []
        
        for trial in trials_data[:5]:  # Limit to first 5 trials
            rows.append([
                trial.get('id', 'N/A'),
                trial.get('indication', 'N/A')[:30] + '...' if len(trial.get('indication', '')) > 30 else trial.get('indication', 'N/A'),
                trial.get('phase', 'N/A'),
                trial.get('status', 'N/A')
            ])
        
        table_data = headers + rows
        table = Table(table_data, colWidths=[1.2*inch, 2.5*inch, 1*inch, 1.3*inch])
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table

    def _create_patent_status_chart(self, patent_matches: list) -> str:
        """Create a bar chart showing patent status distribution."""
        if not patent_matches:
            return None
            
        status_counts = {}
        for patent in patent_matches:
            status = patent.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        fig, ax = plt.subplots(figsize=(6, 4))
        statuses = list(status_counts.keys())
        counts = list(status_counts.values())
        
        colors_list = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
        bars = ax.bar(statuses, counts, color=colors_list[:len(statuses)])
        
        ax.set_title('Patent Status Distribution')
        ax.set_xlabel('Patent Status')
        ax.set_ylabel('Count')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        plt.savefig(temp_file.name, dpi=150, bbox_inches='tight')
        plt.close()
        
        return temp_file.name

    def generate_pdf(self, title: str, sections: dict, filename: str | None = None) -> Path:
        """Generate an enhanced PDF report with tables and charts."""
        filename = filename or f"report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
        out_path = self.out_dir / filename
        
        doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", 
                              self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Clinical Trials Section
        if 'Clinical Trials Summary' in sections:
            clinical_data = sections['Clinical Trials Summary']
            story.append(Paragraph("📊 Clinical Trials Summary", self.styles['SectionHeader']))
            
            summary_text = f"Total Trials: {clinical_data.get('count', 0)}<br/>"
            summary_text += f"Phase Distribution: {json.dumps(clinical_data.get('phases', {}))}<br/>"
            summary_text += f"Status Distribution: {json.dumps(clinical_data.get('statuses', {}))}"
            story.append(Paragraph(summary_text, self.styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Add phase distribution chart
            if clinical_data.get('phases'):
                chart_path = self._create_phase_distribution_chart(clinical_data['phases'])
                if chart_path:
                    story.append(Image(chart_path, width=4*inch, height=2.7*inch))
                    story.append(Spacer(1, 12))
            
            # Add trials table
            if clinical_data.get('examples'):
                trials_table = self._create_trials_table(clinical_data['examples'])
                if trials_table:
                    story.append(trials_table)
                    story.append(Spacer(1, 12))
        
        # Patent Landscape Section
        if 'Patent Landscape' in sections:
            patent_data = sections['Patent Landscape']
            story.append(Paragraph("⚖️ Patent Landscape", self.styles['SectionHeader']))
            
            patent_text = f"Opportunity Level: <b>{patent_data.get('opportunity', 'Unknown')}</b><br/>"
            patent_text += f"Patent Coverage: {json.dumps(patent_data.get('patent_coverage', {}))}"
            story.append(Paragraph(patent_text, self.styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Add patent status chart
            if patent_data.get('matches'):
                chart_path = self._create_patent_status_chart(patent_data['matches'])
                if chart_path:
                    story.append(Image(chart_path, width=4*inch, height=2.7*inch))
                    story.append(Spacer(1, 12))
        
        # Market Insights Section
        if 'Market Insight' in sections:
            market_data = sections['Market Insight']
            story.append(Paragraph("💰 Market Insights", self.styles['SectionHeader']))
            
            market_text = f"Segment: {market_data.get('segment', 'N/A')}<br/>"
            market_text += f"Gap Score: <b>{market_data.get('gap_score', 'N/A')}/10</b><br/>"
            market_text += f"Market Size: ${market_data.get('estimated_addressable_market_usd_m', 'N/A')}M<br/>"
            market_text += f"Strategy: {market_data.get('recommended_strategy', 'N/A')}<br/><br/>"
            market_text += f"Rationale: {market_data.get('rationale', 'N/A')}"
            story.append(Paragraph(market_text, self.styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Literature Synthesis Section
        if 'Literature Synthesis' in sections:
            story.append(Paragraph("📚 Literature Synthesis", self.styles['SectionHeader']))
            lit_text = str(sections['Literature Synthesis'])
            story.append(Paragraph(lit_text, self.styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Conclusion Section
        if 'Conclusion' in sections:
            story.append(Paragraph("🎯 Conclusion", self.styles['SectionHeader']))
            conclusion_text = str(sections['Conclusion'])
            story.append(Paragraph(conclusion_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        # Clean up temporary chart files
        try:
            for temp_file in [f for f in Path(tempfile.gettempdir()).glob('tmp*.png')]:
                temp_file.unlink(missing_ok=True)
        except:
            pass  # Ignore cleanup errors
        
        return out_path


if __name__ == "__main__":
    ra = ReportAgent()
    sections = {
        "Clinical Trials Summary": "Example clinical summary",
        "Patent Landscape": "No active patents covering plain Metformin for oncology",
        "Market Insight": "High gap score",
        "Literature Synthesis": "Metformin acts on AMPK/mTOR and shows epidemiological signals",
        "Conclusion": "Promising repurposing opportunity"
    }
    p = ra.generate_pdf("Metformin — Oncology Repurposing Potential", sections)
    print("Wrote:", p)
