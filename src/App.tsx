import { useState } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<any | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/analyze-seller', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ebay_link: url }),
      });
      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError('Failed to connect to backend. Why does this always happen to me{err}');
    }
    setIsLoading(false);
  };

  return (
    <div className="app-container" style={{ maxWidth: 600, margin: '2rem auto', padding: '2rem', background: '#fff', borderRadius: 8 }}>
      <h1 style={{ textAlign: 'center' }}>eBay Seller Analysis</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
        <input
          type="url"
          placeholder="Paste eBay product link here - I'm watching so it better not be sus🙏."
          value={url}
          onChange={e => setUrl(e.target.value)}
          style={{ width: '100%', padding: '0.75rem', fontSize: '1rem', marginBottom: '1rem' }}
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !url.trim()} style={{ width: '100%', padding: '0.75rem', fontSize: '1rem' }}>
          {isLoading ? 'Analyzing...' : 'Analyze Seller'}
        </button>
      </form>
      {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}
      {result && (
        <div style={{ background: '#f19ff9', padding: '1rem', borderRadius: 6 }}>
          <h2>Seller Info</h2>
          <p><strong>Total Feedback:</strong> {result.total_feedback}</p>
          <p><strong>Positive Feedback %:</strong> {result.positive_percent}</p>
          <h3>Recent Feedbacks</h3>
          <ul>
            {result.recent_feedbacks?.map((fb: any, idx: number) => (
              <li key={idx}>
                <strong>{fb.rating_type}:</strong> {fb.comment}
              </li>
            ))}
          </ul>
          {result.issue_sentiment_summary && result.issue_sentiment_summary.length > 0 && (
            <>
              <h3>Issue Sentiment Summary</h3>
              <table style={{ width: '100%', background: '#fff', borderCollapse: 'collapse', marginTop: 12 }}>
                <thead>
                  <tr>
                    <th style={{ border: '1px solid #ccc', padding: 4 }}>Issue</th>
                    <th style={{ border: '1px solid #ccc', padding: 4 }}>Sentiment</th>
                    <th style={{ border: '1px solid #ccc', padding: 4 }}>Count</th>
                  </tr>
                </thead>
                <tbody>
                  {result.issue_sentiment_summary.map((row: any, idx: number) => (
                    <tr key={idx}>
                      <td style={{ border: '1px solid #ccc', padding: 4 }}>{row.issues}</td>
                      <td style={{ border: '1px solid #ccc', padding: 4 }}>{row.final_sentiment}</td>
                      <td style={{ border: '1px solid #ccc', padding: 4 }}>{row.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
