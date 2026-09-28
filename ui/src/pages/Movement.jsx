import { useEffect, useRef, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../api';

function Movement() {
  const [points, setPoints] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [running, setRunning] = useState(false);
  const [source, setSource] = useState('demo');
  const timer = useRef(null);
  const start = useRef(Date.now());

  useEffect(() => () => clearInterval(timer.current), []);

  const sendDemoSample = async () => {
    const t = (Date.now() - start.current) / 1000;
    const tremor = Math.sin(t * 2 * Math.PI * 4.2) * 0.12;
    const irregular = Math.sin(t * 2 * Math.PI * 1.3) * 0.05 + Math.sin(t * 2 * Math.PI * 2.7) * 0.03;
    const sample = { timestamp: Date.now() / 1000, x: tremor + irregular, y: Math.sin(t * 2 * Math.PI * 3.1) * 0.04, z: 0.98 + Math.sin(t * 2 * Math.PI * 0.4) * 0.015 };
    try {
      const result = await api.sensor(sample);
      setAnalysis(result);
      setPoints((p) => [...p.slice(-59), { time: t.toFixed(1), value: result.movement_index }]);
    } catch (e) {
      console.error(e);
    }
  };

  const toggle = () => {
    if (running) {
      clearInterval(timer.current);
      setRunning(false);
      return;
    }
    start.current = Date.now();
    setRunning(true);
    sendDemoSample();
    timer.current = setInterval(sendDemoSample, 100);
  };

  const saveSession = async () => {
    if (!analysis) return;
    await api.session({ duration: 5, context: { source: source === 'demo' ? 'demo_sensor' : source } });
    alert('Movement window saved as a session.');
  };

  const usePhone = async () => {
    if (!window.DeviceMotionEvent) return alert('DeviceMotion is not available in this browser. Use the demo sensor or open this page on a phone over HTTPS.');
    if (typeof DeviceMotionEvent.requestPermission === 'function') {
      const permission = await DeviceMotionEvent.requestPermission();
      if (permission !== 'granted') return;
    }
    setSource('phone');
    const handler = (e) => {
      const a = e.accelerationIncludingGravity || e.acceleration;
      if (!a) return;
      api.sensor({ timestamp: Date.now() / 1000, x: a.x || 0, y: a.y || 0, z: a.z || 0 }).then((result) => {
        setAnalysis(result);
        setPoints((p) => [...p.slice(-59), { time: new Date().toLocaleTimeString(), value: result.movement_index }]);
      }).catch(console.error);
    };
    window.addEventListener('devicemotion', handler);
    setRunning(true);
    timer.current = { handler };
  };

  const stopPhone = () => {
    if (timer.current?.handler) window.removeEventListener('devicemotion', timer.current.handler);
    clearInterval(timer.current);
    timer.current = null;
    setRunning(false);
  };

  const baseline = analysis?.baseline || {};
  const features = analysis?.features || {};

  return (
    <div className="movement-page">
      <div className="page-header">
        <div><p className="eyebrow">MOVEMENT</p><h1>Movement</h1><p className="page-subtitle">Live movement analysis from the Holocron backend.</p></div>
        <div className="movement-controls">
          <div className="sensor-status"><span className="status-dot"></span>{running ? 'Sensor stream active' : 'Sensor idle'}</div>
          <select className="signal-select" value={source} onChange={(e) => setSource(e.target.value)}>
            <option value="demo">Demo sensor</option><option value="phone">Phone IMU</option>
          </select>
          {source === 'demo' ? <button className="report-button" onClick={toggle}>{running ? 'Stop stream' : 'Start demo'}</button> : <button className="report-button" onClick={running ? stopPhone : usePhone}>{running ? 'Stop phone' : 'Use phone IMU'}</button>}
          <button className="report-button" onClick={saveSession} disabled={!analysis}>Save session</button>
        </div>
      </div>

      <section className="movement-metrics">
        <div className="movement-metric"><span>Movement Index</span><strong>{analysis ? analysis.movement_index.toFixed(1) : '--'}</strong></div>
        <div className="movement-metric"><span>Personal baseline</span><strong>{baseline.baseline_ready ? baseline.baseline.toFixed(1) : 'Provisional'}</strong></div>
        <div className="movement-metric"><span>Pattern</span><strong>{analysis?.pattern?.pattern?.replaceAll('_', ' ') || '--'}</strong></div>
        <div className="movement-metric"><span>Signal RMS</span><strong>{features.rms?.toFixed(3) || '--'}</strong></div>
      </section>

      <section className="movement-panel">
        <div className="panel-header"><div><h2>Movement signal</h2><p>Backend Movement Index over incoming windows</p></div><span className="panel-tag">LIVE</span></div>
        <div className="movement-chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={points} margin={{ top: 20, right: 20, left: 0, bottom: 10 }}><CartesianGrid stroke="#edf0ee" vertical={false}/><XAxis dataKey="time" tick={{fontSize:10,fill:'#8a918c'}} axisLine={false} tickLine={false}/><YAxis domain={[0,100]} tick={{fontSize:10,fill:'#8a918c'}} axisLine={false} tickLine={false}/><Tooltip/><Line type="monotone" dataKey="value" stroke="#2f7655" strokeWidth={2} dot={false}/></LineChart></ResponsiveContainer></div>
      </section>
      {analysis && <section className="dashboard-panel" style={{marginTop:16}}><div className="panel-header"><div><h2>Latest analysis</h2><p>Structured output from the backend</p></div></div><p><strong>Baseline change:</strong> {baseline.difference?.toFixed(1)} ({baseline.relative_change?.toFixed(1)}%)</p><p><strong>Dominant frequency:</strong> {features.dominant_frequency?.toFixed(2)} Hz</p><p><strong>Model confidence:</strong> {analysis.pattern?.confidence == null ? 'not calibrated' : `${(analysis.pattern.confidence * 100).toFixed(0)}%`}</p></section>}
    </div>
  );
}
export default Movement;
