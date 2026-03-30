/** EngagementStatusBoard — VIZ04 status cards */
import React from 'react';
import { Target, Timer, Crosshair, ShieldCheck } from 'lucide-react';
import theme from '../theme';
import { pkToColor, phaseColor } from '../utils/colorScale';

function StatusCard({ label, value, color, icon: Icon }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 10, padding: '8px 12px',
      background: theme.BG_ELEVATED, borderRadius: 4,
      border: `1px solid ${theme.BORDER_DIM}`
    }}>
      {Icon && <Icon size={14} style={{ color, flexShrink: 0 }} />}
      <div style={{ flex: 1 }}>
        <div style={{
          fontFamily: theme.FONT_MONO, fontSize: 9, fontWeight: 600,
          color: theme.TEXT_DIM, letterSpacing: 1, marginBottom: 2
        }}>{label}</div>
        <div style={{
          fontFamily: theme.FONT_MONO, fontSize: 13, fontWeight: 700,
          color: color || theme.TEXT_PRIMARY
        }}>{value}</div>
      </div>
    </div>
  );
}

export default function EngagementStatusBoard({ summary, liveData, isFinished }) {
  const s = summary || {};
  const t = liveData?.t || 0;
  
  // State: FLYING until the playback finishes, then INTERCEPT or MISS
  const phase = isFinished ? (s.intercept_achieved ? 'INTERCEPT' : 'MISS') : 'IN FLIGHT';
  const phaseClr = isFinished ? (s.intercept_achieved ? theme.GREEN_OK : theme.RED_CRITICAL) : theme.CYAN_PRIMARY;

  // Live distance: use liveData range or default to final miss distance if finished
  const currentDist = liveData?.rangeToGo !== undefined ? liveData.rangeToGo : (s.miss_distance_m || 0);

  return (
    <div className="panel">
      <div className="panel-header"><ShieldCheck size={14} />ENGAGEMENT STATUS</div>
      <div className="panel-body" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        <StatusCard label="MISSILE STATE" value={phase} color={phaseClr} icon={Target} />
        <StatusCard label={isFinished ? "FINAL MISS DIST" : "CURRENT RANGE"} value={`${currentDist.toFixed(1)} m`}
          color={isFinished ? (currentDist < 15 ? theme.GREEN_OK : theme.RED_CRITICAL) : theme.TEXT_PRIMARY} icon={Crosshair} />
        <StatusCard label="FLIGHT TIME" value={`${t.toFixed(2)} s`}
          color={theme.CYAN_PRIMARY} icon={Timer} />
        <StatusCard label="INTERCEPT" value={isFinished ? (s.intercept_achieved ? 'YES' : 'NO') : 'PENDING'}
          color={isFinished ? (s.intercept_achieved ? theme.GREEN_OK : theme.RED_CRITICAL) : theme.TEXT_DIM} icon={ShieldCheck} />
        <StatusCard label="GUIDANCE LAW" value={(s.guidance_law || 'PNG').toUpperCase()}
          color={theme.PURPLE_INFO} />
        <StatusCard label="SCENARIO" value={(s.scenario || 'head_on').replace('_', '-').toUpperCase()}
          color={theme.AMBER_WARN} />
      </div>
    </div>
  );
}
