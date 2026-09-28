import { useEffect, useState } from 'react';
import { api } from '../api';
function Sessions() {
  const [sessions, setSessions] = useState([]); const [q, setQ] = useState('');
  useEffect(() => { api.history(100).then(setSessions).catch(console.error); }, []);
  const filtered = sessions.filter(s => JSON.stringify(s).toLowerCase().includes(q.toLowerCase()));
  return <div className="sessions-page"><div className="page-header"><div><p className="eyebrow">SESSIONS</p><h1>Sessions</h1><p className="page-subtitle">Recorded movement windows from the backend.</p></div></div><section className="sessions-toolbar"><div className="session-search"><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search sessions..."/></div></section><section className="sessions-table"><div className="sessions-table-header"><span>Date</span><span>Type</span><span>Source</span><span>Movement Index</span><span>Status</span></div>{filtered.length ? filtered.map(s=><div className="session-row" key={s.session_id}><span className="session-date">{new Date(s.timestamp*1000).toLocaleString()}</span><span className="session-type">Movement</span><span className="session-source">{s.context?.source || 'Backend'}</span><span className="session-score">{Number(s.movement_index).toFixed(1)}</span><span className="session-status status-complete">Complete</span></div>) : <div className="session-row"><span>No sessions yet. Start a movement stream and save a session.</span></div>}</section></div>;
}
export default Sessions;
