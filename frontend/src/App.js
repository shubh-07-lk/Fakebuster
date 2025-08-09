import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [article, setArticle] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [matches, setMatches] = useState([]);
  const BACKEND = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  const handleCheck = async (e) => {
    e.preventDefault();
    if (!article.trim()) return alert('Please enter an article.');
    setLoading(true);
    setResult(null);
    setMatches([]);
    try {
      const resp = await axios.post(`${BACKEND}/check-fake-news`, { article });
      setResult(resp.data);
      setMatches(resp.data.matches || []);
    } catch (err) {
      console.error(err);
      alert('Error contacting backend. Make sure backend is running and API keys are configured.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>🧠 FakeBuster AI</h1>
        <p>Paste a news article (any language) and check if it's real or fake (semantic search)</p>
        <form onSubmit={handleCheck}>
          <textarea value={article} onChange={(e) => setArticle(e.target.value)} placeholder="Paste article here..." />
          <div className="actions">
            <button type="submit" disabled={loading}>{loading ? 'Analyzing...' : 'Check Fake News'}</button>
            <button type="button" onClick={() => { setArticle(''); setResult(null); setMatches([]); }}>Clear</button>
          </div>
        </form>

        {result && (
          <div className={"result " + (result.verdict === 'REAL' ? 'real' : result.verdict === 'LIKELY REAL' ? 'likely' : 'fake')}>
            <h2>Result: {result.verdict}</h2>
            <p>Detected language: {result.detected_language} | Confidence: {result.confidence}</p>
            <h3>Matches:</h3>
            {matches.length === 0 && <p>No close matches found.</p>}
            <ul>
              {matches.map((m, i) => (
                <li key={i}>
                  <strong>{m.source}:</strong> {m.headline} {m.url && (<a href={m.url} target="_blank" rel="noreferrer">Read</a>)} <em>({m.score.toFixed(2)})</em>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
