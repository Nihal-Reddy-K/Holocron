import { useEffect, useState } from 'react';
import { api } from '../api';

function Dashboard() {
  const [movement, setMovement] = useState(null);
  const [history, setHistory] = useState([]);
  const [insight, setInsight] = useState(null);
  const [online, setOnline] = useState(false);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const [m, h, i] = await Promise.all([api.movement(), api.history(10), api.insight()]);
        if (mounted) { setMovement(m); setHistory(h); setInsight(i); setOnline(true); }
      } catch { if (mounted) setOnline(false); }
    };
    load(); const id = setInterval(load, 1500); return () => { mounted = false; clearInterval(id); };
  }, []);

  const idx = movement?.movement_index;
  return <div className="dashboard">
    <div className="dashboard-header"><div><p className="eyebrow">OVERVIEW</p><h1>Dashboard</h1><p className="dashboard-subtitle">Live movement monitoring and AI-assisted interpretation.</p></div><div className="status-badge"><span className="status-dot"></span>{online ? 'Backend connected' : 'Backend offline'}</div></div>
    <section className="metric-grid">
      <div className="metric-card"><div className="metric-label">Movement Index</div><div className="metric-value">{idx == null ? '--' : idx.toFixed(1)}</div><div className="metric-description">Prototype movement metric</div></div>
      <div className="metric-card"><div className="metric-label">Sessions</div><div className="metric-value">{history.length}</div><div className="metric-description">Recorded sessions</div></div>
      <div className="metric-card"><div className="metric-label">Movement status</div><div className="metric-value metric-status">{movement?.pattern?.replaceAll('_',' ') || 'Ready'}</div><div className="metric-description">ML pattern output</div></div>
    </section>
    <section className="dashboard-grid">
      <div className="dashboard-panel movement-panel"><div className="panel-header"><div><h2>Current movement</h2><p>Latest backend analysis</p></div><span className="panel-tag">LIVE</span></div><div className="chart-placeholder"><div className="chart-message">{idx == null ? 'Start the demo sensor from Movement.' : `Movement Index ${idx.toFixed(1)}`}</div></div></div>
      <div className="dashboard-panel sessions-panel"><div className="panel-header"><div><h2>AI insight</h2><p>Explanation layer</p></div></div><div className="empty-state"><h3>{insight?.summary || 'No insight yet'}</h3><p>{insight?.limitations || 'Run a movement session to generate an interpretation.'}</p></div></div>
    </section>
  </div>;
}
export default Dashboard;
