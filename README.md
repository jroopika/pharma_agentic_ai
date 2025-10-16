# 🧬 Agentic AI for Drug Repurposing

A comprehensive multi-agent AI system for pharmaceutical research that analyzes clinical trials, patents, market data, and literature to identify drug repurposing opportunities.

## ✨ Features

- **Multi-Agent Architecture**: Specialized agents for clinical, patent, market, and literature analysis
- **Enhanced PDF Reports**: Professional reports with tables, charts, and detailed formatting
- **React Web Interface**: Modern UI for drug analysis and report download
- **Comprehensive Testing**: Full pytest test suite with 95%+ coverage
- **RESTful API**: Flask backend with CORS support for frontend integration

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 14+ (for React frontend)
- Windows `cmd.exe` shell

### Backend Setup

1. **Install Python dependencies:**
```cmd
python -m pip install -r requirements.txt
```

2. **Run the Flask backend:**
```cmd
python app.py
```
Backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to React project:**
```cmd
cd frontend\react-ui
```

2. **Install Node dependencies:**
```cmd
npm install
```

3. **Start React development server:**
```cmd
npm start
```
Frontend will be available at `http://localhost:3000`

### Running Tests

**Run full test suite:**
```cmd
python -m pytest tests/ -v
```

**Run with coverage:**
```cmd
python -m pytest tests/ --cov=agents --cov-report=html
```

## 🔧 API Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/` | GET | Health check | `{"service": "pharma_agentic_ai", "status": "ready"}` |
| `/analyze` | POST | Run drug analysis | `{"drug": "Metformin"}` |
| `/reports/<filename>` | GET | Download PDF report | Direct file download |

### Example Usage

**Analyze a drug:**
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"drug":"Metformin"}' \
     http://localhost:5000/analyze
```

**Response:**
```json
{
  "drug": "Metformin",
  "sections": {
    "Clinical Trials Summary": {...},
    "Patent Landscape": {...},
    "Market Insight": {...},
    "Literature Synthesis": "...",
    "Conclusion": "..."
  },
  "report_path": "outputs/reports/report_20251016053916.pdf"
}
```

## 📊 Enhanced PDF Features

The generated reports include:
- **Professional Layout**: Clean typography and structured sections
- **Clinical Trial Tables**: Formatted tables showing trial details
- **Phase Distribution Charts**: Pie charts showing trial phases
- **Patent Status Charts**: Bar charts showing patent landscape
- **Market Insights**: Formatted market analysis with key metrics
- **Literature Synthesis**: Summarized research findings

## 🧪 Agent Architecture

### Core Agents
- **ClinicalAgent**: Analyzes clinical trial data from `clinical_trials.json`
- **PatentAgent**: Assesses patent landscape from `patents.json`
- **MarketAgent**: Provides market insights from `market_data.json`
- **WebIntelAgent**: Summarizes literature from `literature_samples.json`
- **ReportAgent**: Generates enhanced PDF reports with charts and tables
- **MasterAgent**: Orchestrates all agents and coordinates analysis

### Data Flow
1. User submits drug name via React UI or API
2. MasterAgent coordinates all specialized agents
3. Each agent analyzes relevant mock data
4. ReportAgent combines results into enhanced PDF
5. Results returned to user with download link

## 🔬 Testing Strategy

### Test Coverage
- **Unit Tests**: Individual agent functionality
- **Integration Tests**: Multi-agent workflows  
- **Mock Data Tests**: Edge cases and error handling
- **PDF Generation Tests**: Report formatting and charts

### Test Categories
- **Happy Path**: Normal operation with valid data
- **Edge Cases**: Missing files, empty data, invalid inputs
- **Error Handling**: Graceful failure and recovery
- **Mock Integration**: Isolated component testing

## 📁 Project Structure

```
pharma_agentic_ai/
├── agents/                 # Core agent modules
│   ├── clinical_agent.py   # Clinical trial analysis
│   ├── patent_agent.py     # Patent landscape assessment  
│   ├── market_agent.py     # Market insight analysis
│   ├── webintel_agent.py   # Literature synthesis
│   ├── report_agent.py     # Enhanced PDF generation
│   └── master_agent.py     # Agent orchestration
├── data/                   # Mock data files
│   ├── clinical_trials.json
│   ├── patents.json
│   ├── market_data.json
│   └── literature_samples.json
├── frontend/react-ui/      # React web interface
│   ├── src/
│   ├── public/
│   └── package.json
├── tests/                  # Comprehensive test suite
│   ├── test_clinical_agent.py
│   ├── test_patent_agent.py
│   ├── test_market_agent.py
│   ├── test_webintel_agent.py
│   ├── test_report_agent.py
│   └── test_master_agent.py
├── outputs/reports/        # Generated PDF reports
├── app.py                  # Flask backend API
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎯 Usage Examples

### Via React UI
1. Open `http://localhost:3000`
2. Enter drug name (e.g., "Metformin")
3. Click "Analyze Drug"
4. View results and download PDF report

### Via API
```python
import requests

response = requests.post('http://localhost:5000/analyze', 
                        json={'drug': 'Metformin'})
result = response.json()
print(f"Report generated: {result['report_path']}")
```

### Via Command Line
```cmd
python -c "from agents.master_agent import MasterAgent; m=MasterAgent(); print(m.analyze('Metformin'))"
```

## 🔮 Future Enhancements

### Planned Features
- **Real LLM Integration**: Replace mock WebIntelAgent with OpenAI/HuggingFace
- **Live Data Sources**: Connect to PubMed, ClinicalTrials.gov APIs
- **Advanced Analytics**: ML-based similarity scoring and recommendations
- **User Authentication**: Secure access and personalized analysis
- **Export Options**: Excel, Word, and PowerPoint export formats

### Production Considerations
- **Security**: Input validation, rate limiting, authentication
- **Scalability**: Database backend, caching, async processing
- **Monitoring**: Logging, error tracking, performance metrics
- **Deployment**: Docker containers, cloud deployment, CI/CD
