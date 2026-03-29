/** TelemetryPanel — Live telemetry strip with animated bars */
import React from 'react';
import { Activity } from 'lucide-react';
import theme from '../../theme';
import { formatMach, formatAlt, formatSpeed, formatRange, formatG, formatTime } from '../../utils/physicsUnits';
import { machRegimeColor, phaseColor } from '../../utils/colorScale';

function TelemetryBar({ label, value, max, color, displayValue }) {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        fontFamily: theme.FONT_MONO, fontSize: 10, fontWeight: 600,
        color: theme.TEXT_DIM, letterSpacing: 1, marginBottom: 3
      }}>
        <span>{label}</span>
        <span style={{ color: color || theme.CYAN_PRIMARY }}>{displayValue}</span>
      </div>
      <div style={{
        height: 4, background: theme.BG_ELEVATED, borderRadius: 2, overflow: 'hidden'
      }}>
        <div style={{
          width: `${pct}%`, height: '100%',
          background: color || theme.CYAN_PRIMARY,
          borderRadius: 2,
          transition: 'width 0.15s ease-out',
          boxShadow: `0 0 8px ${color || theme.CYAN_PRIMARY}60`
        }} />
      </div>
    </div>
  );
}

export default function TelemetryPanel({ data }) {
  const t = data || {};
  const mach = t.mach || 0;
  const alt = t.altitude_m || 0;
  const speed = t.speed || (mach * 340);
  const range = t.range_to_target_m || 0;
  const gLoad = t.g_load || 0;
  const phase = t.phase || 'STANDBY';
  const time = t.t || 0;
  const closing = t.closing_velocity_ms || 0;

  return (
    <div className="panel">
      <div className="panel-header"><Activity size={14} />TELEMETRY</div>
      <div className="panel-body">
        <TelemetryBar label="MACH" value={mach} max={4} color={machRegimeColor(mach)} displayValue={formatMach(mach)} />
        <TelemetryBar label="ALTITUDE" value={alt} max={20000} color={theme.CYAN_PRIMARY} displayValue={formatAlt(alt)} />
        <TelemetryBar label="SPEED" value={speed} max={1400} color={theme.CYAN_BRIGHT} displayValue={formatSpeed(speed)} />
        <TelemetryBar label="RANGE-TO-GO" value={Math.max(0, range)} max={80000} color={range < 5000 ? theme.RED_CRITICAL : theme.AMBER_WARN} displayValue={formatRange(range)} />
        <TelemetryBar label="CLOSING Vc" value={Math.abs(closing)} max={1000} color={theme.GREEN_OK} displayValue={`${closing.toFixed(0)} m/s`} />
        <TelemetryBar label="G-LOAD" value={gLoad} max={30} color={gLoad > 20 ? theme.RED_CRITICAL : theme.AMBER_WARN} displayValue={formatG(gLoad)} />
        <div style={{
          display: 'flex', justifyContent: 'space-between', marginTop: 12,
          fontFamily: theme.FONT_MONO, fontSize: 11
        }}>
          <span style={{ color: theme.TEXT_DIM }}>PHASE</span>
          <span style={{
            padding: '2px 8px', borderRadius: 3,
            background: `${phaseColor(phase)}20`,
            color: phaseColor(phase),
            fontWeight: 700, fontSize: 10, letterSpacing: 1
          }}>{phase}</span>
        </div>
        <div style={{
          display: 'flex', justifyContent: 'space-between', marginTop: 8,
          fontFamily: theme.FONT_MONO, fontSize: 11
        }}>
          <span style={{ color: theme.TEXT_DIM }}>TIME-OF-FLIGHT</span>
          <span style={{ color: theme.CYAN_PRIMARY, fontWeight: 700 }}>{formatTime(time)}</span>
        </div>
      </div>
    </div>
  );
}
