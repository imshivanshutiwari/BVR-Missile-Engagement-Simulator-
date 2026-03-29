/** PkGauge — Large semicircle Pk probability gauge */
import React from 'react';
import theme from '../theme';
import { pkToColor } from '../utils/colorScale';

export default function PkGauge({ pk = 0, breakdown = {} }) {
  const pct = Math.min(1, Math.max(0, pk));
  const angle = pct * 180;
  const color = pkToColor(pct);
  const r = 70;
  const cx = 80, cy = 80;

  // SVG arc path
  const endAngle = (180 - angle) * Math.PI / 180;
  const x2 = cx + r * Math.cos(endAngle);
  const y2 = cy - r * Math.sin(endAngle);
  const largeArc = angle > 180 ? 1 : 0;

  const arcPath = `M ${cx - r} ${cy} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`;

  return (
    <div className="panel">
      <div className="panel-header">Pk PROBABILITY OF KILL</div>
      <div className="panel-body" style={{ textAlign: 'center' }}>
        <svg width="160" height="100" viewBox="0 0 160 100">
          {/* Background arc */}
          <path d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
            fill="none" stroke={theme.BORDER_DIM} strokeWidth="8" strokeLinecap="round" />
          {/* Value arc */}
          {angle > 0 && (
            <path d={arcPath}
              fill="none" stroke={color} strokeWidth="8" strokeLinecap="round"
              style={{ filter: `drop-shadow(0 0 6px ${color})`, transition: 'all 0.5s ease' }} />
          )}
        </svg>
        <div style={{
          marginTop: -30,
          fontFamily: theme.FONT_MONO, fontSize: 28, fontWeight: 700,
          color: color,
          textShadow: `0 0 20px ${color}60`
        }}>
          Pk = {(pct * 100).toFixed(1)}%
        </div>
        <div style={{
          display: 'flex', justifyContent: 'center', gap: 16, marginTop: 12,
          fontFamily: theme.FONT_MONO, fontSize: 9, color: theme.TEXT_DIM,
          letterSpacing: 0.5
        }}>
          <span>FUZE: {((breakdown.p_fuze || 0) * 100).toFixed(0)}%</span>
          <span>GUIDE: {((breakdown.p_guidance || 0) * 100).toFixed(0)}%</span>
          <span>LETHAL: {((breakdown.p_lethality || 0) * 100).toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
}
