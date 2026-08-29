import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API = 'http://127.0.0.1:8000';

function App() {
  const [bins, setBins] = useState([]);
  const [reports, setReports] = useState([]);
  const [error, setError] = useState('');

  async function load() {
    try {
      const [b, r] = await Promise.all([
        fetch(`${API}/api/bins`),
        fetch(`${API}/api/reports`)
      ]);
      if (!b.ok || !r.ok) throw new Error('Backend not reachable');
      setBins(await b.json());
      setReports(await r.json());
      setError('');
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => { load(); }, []);

  const critical = bins.filter(b => b.fill_level >= 90).length;
  const avg = bins.length ? Math.round(bins.reduce((s, b) => s + b.fill_level, 0) / bins.length) : 0;

  return (
    <main>
      <header>
        <p className="eyebrow">CSE7102 • PRJ_628</p>
        <h1>Smart Waste Management</h1>
        <p className="sub">Predictive collection and circular-economy prototype</p>
      </header>

      {error && <div className="error">{error}. Start the FastAPI server first.</div>}

      <section className="metrics">
        <div><span>Monitored bins</span><strong>{bins.length}</strong></div>
        <div><span>Critical bins</span><strong>{critical}</strong></div>
        <div><span>Average fill</span><strong>{avg}%</strong></div>
        <div><span>Citizen reports</span><strong>{reports.length}</strong></div>
      </section>

      <section className="panel">
        <div className="panel-head"><h2>Collection priority</h2><button onClick={load}>Refresh</button></div>
        <table>
          <thead><tr><th>Bin</th><th>Ward</th><th>Fill</th><th>Status</th></tr></thead>
          <tbody>{bins.map(b => (
            <tr key={b.id}>
              <td>{b.code}</td><td>{b.ward}</td><td>{b.fill_level}%</td>
              <td><span className={`badge ${b.fill_level >= 90 ? 'critical' : b.fill_level >= 70 ? 'high' : 'normal'}`}>
                {b.fill_level >= 90 ? 'CRITICAL' : b.fill_level >= 70 ? 'HIGH' : 'NORMAL'}
              </span></td>
            </tr>
          ))}</tbody>
        </table>
      </section>

      <section className="panel">
        <div className="panel-head"><h2>Recent citizen reports</h2></div>
        <div className="reports">{reports.map(r => (
          <article key={r.id}><div><b>{r.waste_type}</b><span>{r.ward}</span></div><p>{r.description}</p><small>{r.status}</small></article>
        ))}</div>
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
