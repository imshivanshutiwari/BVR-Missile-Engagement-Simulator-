/** EngagementOps — Page 1: Main Ops Center (with playback animation) */
import React, { useState, useEffect, useRef } from 'react';
import EngagementScene from '../../three-scene/EngagementScene';
import TelemetryPanel from '../panels/TelemetryPanel';
import LaunchConsole from '../panels/LaunchConsole';
import ScenarioSelector from '../panels/ScenarioSelector';
import MissileConfig from '../panels/MissileConfig';
import TargetConfig from '../panels/TargetConfig';
import PkGauge from '../../visualizations/PkGauge';
import EngagementStatusBoard from '../../visualizations/EngagementStatusBoard';
import { GuidanceErrorPlot, EngagementTimelinePlot } from '../../visualizations/PlotlyCharts';
import theme from '../../theme';

export default function EngagementOps({ result, loading, onLaunch, config, setConfig, telemetry }) {
  const trajectory = result?.trajectory || [];
  const targetTraj = result?.target_trajectory || [];
  const summary = result?.engagement_summary || {};
  const pk = result?.pk || 0;
  const pkBreakdown = result?.pk_breakdown || {};

  // --- Animated playback ---
  const [frame, setFrame] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(2); // frames per tick
  const animRef = useRef(null);

  // Auto-start playback when new result arrives
  useEffect(() => {
    if (trajectory.length > 0) {
      setFrame(0);
      setPlaying(true);
    }
  }, [result]);

  // Animation loop
  useEffect(() => {
    if (!playing || trajectory.length === 0) return;
    animRef.current = setInterval(() => {
      setFrame(prev => {
        const next = prev + speed;
        if (next >= trajectory.length - 1) {
          setPlaying(false);
          return trajectory.length - 1;
        }
        return next;
      });
    }, 33); // ~30fps
    return () => clearInterval(animRef.current);
  }, [playing, speed, trajectory.length]);

  // Current telemetry from trajectory frame
  const currentTel = trajectory.length > 0 && frame < trajectory.length ? trajectory[frame] : {};
  const currentTarget = targetTraj.length > 0 && frame < targetTraj.length ? targetTraj[frame] : {};

  // Compute live range
  const rangeToGo = currentTel.x != null && currentTarget.x != null
    ? Math.sqrt(
        Math.pow((currentTarget.x || 0) - (currentTel.x || 0), 2) +
        Math.pow((currentTarget.y || 0) - (currentTel.y || 0), 2) +
        Math.pow((currentTarget.z || 0) - (currentTel.z || 0), 2)
      )
    : 0;

  const telData = {
    mach: currentTel.mach || 0,
    altitude_m: currentTel.altitude != null ? currentTel.altitude : (currentTel.altitude_m || 0),
    speed: currentTel.speed || 0,
    range_to_target_m: rangeToGo,
    closing_velocity_ms: currentTel.closing_velocity || 0,
    g_load: currentTel.g_load || 0,
    phase: currentTel.phase || 'STANDBY',
    t: currentTel.t || 0,
  };

  const progressPct = trajectory.length > 0 ? (frame / (trajectory.length - 1)) * 100 : 0;

  return (
    <div style={{ display: 'flex', gap: 12, padding: '12px', minHeight: 'calc(100vh - 118px)' }}>
      {/* LEFT: 3D + charts */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 12, minWidth: 0 }}>
        {/* 3D Scene */}
        <div style={{
          height: 420, borderRadius: 8,
          border: `1px solid ${theme.BORDER_DIM}`, overflow: 'hidden', position: 'relative'
        }}>
          <EngagementScene
            trajectoryData={trajectory}
            targetTrajectory={targetTraj}
            currentFrame={frame}
            intercept={result?.intercept_achieved}
          />
          {/* Playback controls overlay */}
          {trajectory.length > 0 && (
            <div style={{
              position: 'absolute', bottom: 8, left: 8, right: 8,
              display: 'flex', alignItems: 'center', gap: 8,
              background: 'rgba(5,8,16,0.85)', borderRadius: 6, padding: '6px 12px',
            }}>
              <button onClick={() => setPlaying(!playing)} style={{
                background: 'none', border: 'none', color: theme.CYAN_PRIMARY,
                fontFamily: theme.FONT_MONO, fontSize: 14, cursor: 'pointer', padding: '2px 6px'
              }}>
                {playing ? '⏸' : '▶'}
              </button>
              <button onClick={() => { setFrame(0); setPlaying(true); }} style={{
                background: 'none', border: 'none', color: theme.TEXT_DIM,
                fontFamily: theme.FONT_MONO, fontSize: 12, cursor: 'pointer'
              }}>⏮</button>
              <input type="range" min={0} max={Math.max(0, trajectory.length - 1)} value={frame}
                onChange={e => { setFrame(parseInt(e.target.value)); setPlaying(false); }}
                style={{ flex: 1, accentColor: theme.CYAN_PRIMARY, cursor: 'pointer' }}
              />
              <span style={{ fontFamily: theme.FONT_MONO, fontSize: 10, color: theme.TEXT_SECONDARY, minWidth: 60 }}>
                {(currentTel.t || 0).toFixed(1)}s / {(trajectory[trajectory.length - 1]?.t || 0).toFixed(1)}s
              </span>
              {[1, 2, 5, 10].map(s => (
                <button key={s} onClick={() => setSpeed(s)} style={{
                  background: speed === s ? `${theme.CYAN_PRIMARY}30` : 'none',
                  border: speed === s ? `1px solid ${theme.CYAN_PRIMARY}` : '1px solid transparent',
                  color: speed === s ? theme.CYAN_PRIMARY : theme.TEXT_DIM, borderRadius: 3,
                  fontFamily: theme.FONT_MONO, fontSize: 9, cursor: 'pointer', padding: '2px 5px'
                }}>{s}x</button>
              ))}
            </div>
          )}
        </div>

        {/* Status + Pk */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <EngagementStatusBoard summary={summary} />
          <PkGauge pk={pk} breakdown={pkBreakdown} />
        </div>

        {/* Charts */}
        <GuidanceErrorPlot trajectory={trajectory} />
        <EngagementTimelinePlot trajectory={trajectory} />
      </div>

      {/* RIGHT: Controls sidebar */}
      <div style={{ width: 300, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 12, overflowY: 'auto', maxHeight: 'calc(100vh - 118px)' }}>
        <TelemetryPanel data={telData} />
        <ScenarioSelector
          selected={config?.scenario || 'head_on'}
          onChange={(s) => setConfig && setConfig(prev => ({ ...prev, scenario: s }))}
        />
        <MissileConfig config={config} onChange={setConfig} />
        <TargetConfig config={config} onChange={setConfig} />
        <LaunchConsole onLaunch={onLaunch} loading={loading} />
      </div>
    </div>
  );
}
