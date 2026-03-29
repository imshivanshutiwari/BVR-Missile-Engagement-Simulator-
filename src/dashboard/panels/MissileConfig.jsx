/** MissileConfig — Missile parameter controls */
import React from 'react';
import { Rocket } from 'lucide-react';
import theme from '../../theme';

export default function MissileConfig({ config = {}, onChange }) {
  const defaults = {
    guidance_law: 'png',
    nav_constant: 4.0,
    launch_range_m: 20000,
    launch_altitude_m: 8000,
    ...config
  };

  const handleChange = (key, value) => {
    if (onChange) onChange({ ...defaults, [key]: value });
  };

  const inputStyle = {
    width: '100%', padding: '6px 8px', borderRadius: 3,
    background: theme.BG_ELEVATED, border: `1px solid ${theme.BORDER_DIM}`,
    color: theme.TEXT_PRIMARY, fontFamily: theme.FONT_MONO, fontSize: 11,
    outline: 'none'
  };
  const labelStyle = {
    fontFamily: theme.FONT_MONO, fontSize: 10, fontWeight: 600,
    color: theme.TEXT_DIM, letterSpacing: 1, marginBottom: 3, display: 'block'
  };

  return (
    <div className="panel">
      <div className="panel-header"><Rocket size={14} />MISSILE CONFIG</div>
      <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <div>
          <label style={labelStyle}>GUIDANCE LAW</label>
          <select style={inputStyle} value={defaults.guidance_law}
            onChange={e => handleChange('guidance_law', e.target.value)}>
            <option value="png">PNG (N=4)</option>
            <option value="apng">APNG (Augmented)</option>
          </select>
        </div>
        <div>
          <label style={labelStyle}>LAUNCH RANGE (m)</label>
          <input type="range" min="2000" max="60000" step="1000"
            value={defaults.launch_range_m}
            onChange={e => handleChange('launch_range_m', Number(e.target.value))}
            style={{ width: '100%', accentColor: theme.CYAN_PRIMARY }} />
          <span style={{ fontFamily: theme.FONT_MONO, fontSize: 11, color: theme.CYAN_PRIMARY }}>
            {(defaults.launch_range_m / 1000).toFixed(0)} km
          </span>
        </div>
        <div>
          <label style={labelStyle}>LAUNCH ALTITUDE (m)</label>
          <input type="range" min="1000" max="18000" step="500"
            value={defaults.launch_altitude_m}
            onChange={e => handleChange('launch_altitude_m', Number(e.target.value))}
            style={{ width: '100%', accentColor: theme.CYAN_PRIMARY }} />
          <span style={{ fontFamily: theme.FONT_MONO, fontSize: 11, color: theme.CYAN_PRIMARY }}>
            {(defaults.launch_altitude_m / 1000).toFixed(1)} km
          </span>
        </div>
      </div>
    </div>
  );
}
