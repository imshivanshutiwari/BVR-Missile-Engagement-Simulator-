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

  // Compute g-load from guidance acceleration commands
  const gLoad = currentTel.ax != null
    ? Math.sqrt(
        Math.pow(currentTel.guidance_ax || currentTel.ax || 0, 2) +
        Math.pow(currentTel.guidance_ay || currentTel.ay || 0, 2) +
        Math.pow(currentTel.guidance_az || currentTel.az || 0, 2)
      ) / 9.80665
    : 0;

  // Compute closing velocity from range change between frames
  let closingVel = 0;
  if (frame > 0 && trajectory.length > 1 && targetTraj.length > 1) {
    const prevM = trajectory[Math.max(0, frame - 1)];
    const prevT = targetTraj[Math.min(frame - 1, targetTraj.length - 1)];
    const prevRange = Math.sqrt(
      Math.pow((prevT.x || 0) - (prevM.x || 0), 2) +
      Math.pow((prevT.y || 0) - (prevM.y || 0), 2) +
      Math.pow((prevT.z || 0) - (prevM.z || 0), 2)
    );
    const dt = (currentTel.t || 0) - (prevM.t || 0);
    if (dt > 0) closingVel = (prevRange - rangeToGo) / dt;
  }

  const telData = {
    mach: currentTel.mach || 0,
    altitude_m: currentTel.altitude != null ? currentTel.altitude : (currentTel.altitude_m || 0),
    speed: currentTel.speed || 0,
    range_to_target_m: rangeToGo,
    closing_velocity_ms: closingVel,
    g_load: gLoad,
    phase: (currentTel.phase || 'STANDBY').toString().toUpperCase(),
    t: currentTel.t || 0,
  };

  const progressPct = trajectory.length > 0 ? (frame / (trajectory.length - 1)) * 100 : 0;

  return (
    <div style={{ display: 'flex', gap: 12, padding: '12px', minHeight: 'calc(100vh - 118px)' }}>
      {/* LEFT: 3D + charts */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 12, minWidth: 0 }}>
        {/* 3D Scene */}
        <div style={{
          height: 550, flexGrow: 1, borderRadius: 8,
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
          {/* INTERCEPT / MISS Result Banner */}
          {!playing && trajectory.length > 0 && frame >= trajectory.length - 2 && (
            <div style={{
              position: 'absolute', top: '50%', left: '50%',
              transform: 'translate(-50%, -50%)',
              pointerEvents: 'none', textAlign: 'center',
              animation: 'fadeIn 0.5s ease-out'
            }}>
              <div style={{
                fontFamily: theme.FONT_MONO, fontSize: 42, fontWeight: 900,
                color: result?.intercept_achieved ? '#00ff66' : '#ff3333',
                textShadow: result?.intercept_achieved
                  ? '0 0 40px #00ff66, 0 0 80px #00ff6680'
                  : '0 0 40px #ff3333, 0 0 80px #ff333380',
                letterSpacing: 4
              }}>
                {result?.intercept_achieved ? '💥 TARGET DESTROYED' : '✕ MISSILE MISS'}
              </div>
              <div style={{
                fontFamily: theme.FONT_MONO, fontSize: 14, color: '#ffffffaa',
                marginTop: 8, letterSpacing: 2
              }}>
                Pk = {((result?.pk || 0) * 100).toFixed(1)}% &nbsp;|&nbsp; Miss: {(result?.miss_distance_m || 0).toFixed(1)}m &nbsp;|&nbsp; ToF: {(result?.time_of_flight_s || 0).toFixed(2)}s
              </div>
            </div>
          )}
        </div>

        {/* Status + Pk */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <EngagementStatusBoard 
            summary={summary} 
            liveData={{...currentTel, rangeToGo}}
            isFinished={trajectory.length > 0 && !playing && frame >= trajectory.length - 2}
          />
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
