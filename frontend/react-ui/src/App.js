import axios from 'axios';
import { useState } from 'react';
import './index.css';

function App() {
  const [drug, setDrug] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!drug.trim()) return;

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await axios.post('/analyze', { drug: drug.trim() });
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred during analysis');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (results?.report_path) {
      const filename = results.report_path.split('/').pop();
      window.open(`/reports/${filename}`, '_blank');
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🧬 Pharma Agentic AI</h1>
        <p>Drug Repurposing & Literature Intelligence</p>
      </div>

      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-group">
          <label htmlFor="drug">Drug Name:</label>
          <input
            type="text"
            id="drug"
            value={drug}
            onChange={(e) => setDrug(e.target.value)}
            placeholder="Enter drug name (e.g., Metformin)"
            disabled={loading}
          />
        </div>
        <button type="submit" className="btn" disabled={loading || !drug.trim()}>
          {loading ? 'Analyzing...' : 'Analyze Drug'}
        </button>
      </form>

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading && (
        <div className="loading">
          <p>🔬 Running multi-agent analysis...</p>
          <p>This may take a few moments as we analyze clinical trials, patents, market data, and literature.</p>
        </div>
      )}

      {results && (
        <div className="results">
          <h2>Analysis Results for {results.drug}</h2>
          
          <div className="section">
            <h3>📊 Clinical Trials Summary</h3>
            <p><strong>Total Trials:</strong> {results.sections['Clinical Trials Summary'].count}</p>
            <p><strong>Phase Distribution:</strong> {JSON.stringify(results.sections['Clinical Trials Summary'].phases)}</p>
            <p><strong>Status Distribution:</strong> {JSON.stringify(results.sections['Clinical Trials Summary'].statuses)}</p>
            
            <div className="trials-grid">
              {results.sections['Clinical Trials Summary'].examples.map((trial, idx) => (
                <div key={idx} className="trial-card">
                  <h4>{trial.indication}</h4>
                  <p><strong>Phase:</strong> {trial.phase}</p>
                  <p><strong>Status:</strong> {trial.status}</p>
                  <p>{trial.summary}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="section">
            <h3>⚖️ Patent Landscape</h3>
            <p><strong>Opportunity Level:</strong> {results.sections['Patent Landscape'].opportunity}</p>
            <ul className="patent-list">
              {results.sections['Patent Landscape'].matches.map((patent, idx) => (
                <li key={idx} className="patent-item">
                  <strong>{patent.title}</strong> ({patent.status})<br/>
                  <em>{patent.assignee}</em><br/>
                  {patent.relevance}
                </li>
              ))}
            </ul>
          </div>

          <div className="section">
            <h3>💰 Market Insights</h3>
            <p><strong>Segment:</strong> {results.sections['Market Insight'].segment}</p>
            <p><strong>Gap Score:</strong> {results.sections['Market Insight'].gap_score}/10</p>
            <p><strong>Market Size:</strong> ${results.sections['Market Insight'].estimated_addressable_market_usd_m}M</p>
            <p><strong>Strategy:</strong> {results.sections['Market Insight'].recommended_strategy}</p>
            <p>{results.sections['Market Insight'].rationale}</p>
          </div>

          <div className="section">
            <h3>📚 Literature Synthesis</h3>
            <p>{results.sections['Literature Synthesis']}</p>
          </div>

          <div className="section">
            <h3>🎯 Conclusion</h3>
            <p>{results.sections.Conclusion}</p>
          </div>

          <div className="download-section">
            <h3>📄 Full Report</h3>
            <p>A detailed PDF report has been generated with all findings.</p>
            <button onClick={handleDownload} className="btn">
              Download PDF Report
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;