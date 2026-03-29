/** App.jsx — STRIKE-VECTOR Root Layout + Navigation */
import React, { useState, useCallback } from 'react';
import Header from './dashboard/Header';
import StatusBar from './dashboard/StatusBar';
import EngagementOps from './dashboard/pages/EngagementOps';
import PhysicsLab from './dashboard/pages/PhysicsLab';
import NezAnalysis from './dashboard/pages/NezAnalysis';
import GuidanceLab from './dashboard/pages/GuidanceLab';
import EngagementHistory from './dashboard/pages/EngagementHistory';
import useSimulation from './hooks/useSimulation';
import useNez from './hooks/useNez';
import useTelemetry from './hooks/useTelemetry';
import theme from './theme';

const PAGES = [
  { id: 'ops', label: 'OPS CENTER', icon: '◈' },
  { id: 'physics', label: 'PHYSICS LAB', icon: '⚛' },
  { id: 'nez', label: 'NEZ ANALYSIS', icon: '◎' },
  { id: 'guidance', label: 'GUIDANCE LAB', icon: '⊕' },
  { id: 'history', label: 'HISTORY', icon: '☰' },
];

const navStyle = {
  position: 'fixed', top: 78, left: 0, right: 0, zIndex: 98,
  display: 'flex', gap: 2, padding: '0 20px',
  background: theme.BG_PRIMARY,
  borderBottom: `1px solid ${theme.BORDER_DIM}`,
};

const navBtnStyle = (active) => ({
  padding: '8px 16px',
  background: active ? `${theme.CYAN_PRIMARY}10` : 'transparent',
  border: 'none',
  borderBottom: active ? `2px solid ${theme.CYAN_PRIMARY}` : '2px solid transparent',
  color: active ? theme.CYAN_PRIMARY : theme.TEXT_DIM,
  fontFamily: theme.FONT_MONO,
  fontSize: 10, fontWeight: 700, letterSpacing: 1.5,
  cursor: 'pointer',
  transition: 'all 0.2s',
});

export default function App() {
  const [page, setPage] = useState('ops');
  const [config, setConfig] = useState({
    scenario: 'head_on',
    guidance_law: 'png',
    launch_range_m: 20000,
    launch_altitude_m: 8000,
    target_speed_ms: 250,
    target_altitude_m: 8000,
    target_evasion: true,
  });

  const { result, loading, error, history, simulate, reset } = useSimulation();
  const { nezData, loading: nezLoading, compute: computeNez } = useNez();
  const { current: telemetryCurrent, startStream } = useTelemetry();

  const handleLaunch = useCallback(async () => {
    await simulate(config);
  }, [config, simulate]);

  const handleComputeNez = useCallback(async () => {
    await computeNez({
      target_speed_ms: config.target_speed_ms,
      target_altitude_m: config.target_altitude_m,
      guidance_law: config.guidance_law,
      resolution: 16,
    });
  }, [config, computeNez]);

  const simTime = result?.time_of_flight_s || 0;
  const range = result?.engagement_summary?.launch_range_m || null;
  const status = loading ? 'SIMULATING' : result ? (result.intercept_achieved ? 'INTERCEPT' : 'MISS') : 'READY';

  return (
    <div style={{ minHeight: '100vh', background: theme.BG_PRIMARY }}>
      <Header
        status={status}
        guidance={config.guidance_law?.toUpperCase() || 'PNG'}
        scenario={config.scenario?.replace('_', '-')?.toUpperCase() || 'HEAD-ON'}
        simTime={simTime}
        range={range}
      />
      <StatusBar serverConnected={!error} />

      {/* Navigation */}
      <nav style={navStyle}>
        {PAGES.map(p => (
          <button
            key={p.id}
            style={navBtnStyle(page === p.id)}
            onClick={() => setPage(p.id)}
          >
            {p.icon} {p.label}
          </button>
        ))}
      </nav>

      {/* Page Content */}
      <main style={{ paddingTop: 118 }}>
        {error && (
          <div style={{
            margin: '12px 20px', padding: '10px 16px', borderRadius: 6,
            background: `${theme.RED_CRITICAL}15`,
            border: `1px solid ${theme.RED_DIM}`,
            color: theme.RED_CRITICAL,
            fontFamily: theme.FONT_MONO, fontSize: 12
          }}>
            ⚠ SERVER ERROR: {error} — Make sure FastAPI server is running on port 8000
          </div>
        )}

        {page === 'ops' && (
          <EngagementOps
            result={result}
            loading={loading}
            onLaunch={handleLaunch}
            config={config}
            setConfig={setConfig}
            telemetry={telemetryCurrent}
          />
        )}
        {page === 'physics' && <PhysicsLab result={result} />}
        {page === 'nez' && (
          <NezAnalysis
            nezData={nezData}
            loading={nezLoading}
            onCompute={handleComputeNez}
          />
        )}
        {page === 'guidance' && <GuidanceLab result={result} />}
        {page === 'history' && <EngagementHistory history={history} />}
      </main>
    </div>
  );
}
