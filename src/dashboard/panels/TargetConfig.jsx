/** TargetConfig — Target aircraft parameter controls */
import React from 'react';
import { Plane } from 'lucide-react';
import theme from '../../theme';

export default function TargetConfig({ config = {}, onChange }) {
  const defaults = {
    target_speed_ms: 250,
    target_altitude_m: 8000,
    target_evasion: true,
    ...config
  };

  const handleChange = (key, value) => {
    if (onChange) onChange({ ...defaults, [key]: value });
  };

  const labelStyle = {
    fontFamily: theme.FONT_MONO, fontSize: 10, fontWeight: 600,
    color: theme.TEXT_DIM, letterSpacing: 1, marginBottom: 3, display: 'block'
  };

  return (
    <div className="panel">
      <div className="panel-header"><Plane size={14} />TARGET: F-16 CLASS</div>
      <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <div>
          <label style={labelStyle}>TARGET SPEED (m/s)</label>
          <input type="range" min="150" max="550" step="10"
            value={defaults.target_speed_ms}
            onChange={e => handleChange('target_speed_ms', Number(e.target.value))}
            style={{ width: '100%', accentColor: theme.AMBER_WARN }} />
          <span style={{ fontFamily: theme.FONT_MONO, fontSize: 11, color: theme.AMBER_WARN }}>
            {defaults.target_speed_ms} m/s (M{(defaults.target_speed_ms / 340).toFixed(2)})
          </span>
        </div>
        <div>
          <label style={labelStyle}>TARGET ALTITUDE (m)</label>
          <input type="range" min="1000" max="18000" step="500"
            value={defaults.target_altitude_m}
            onChange={e => handleChange('target_altitude_m', Number(e.target.value))}
            style={{ width: '100%', accentColor: theme.AMBER_WARN }} />
          <span style={{ fontFamily: theme.FONT_MONO, fontSize: 11, color: theme.AMBER_WARN }}>
            {(defaults.target_altitude_m / 1000).toFixed(1)} km
          </span>
        </div>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          fontFamily: theme.FONT_MONO, fontSize: 11
        }}>
          <input type="checkbox" checked={defaults.target_evasion}
            onChange={e => handleChange('target_evasion', e.target.checked)}
            style={{ accentColor: theme.RED_CRITICAL }} />
          <label style={{ color: defaults.target_evasion ? theme.RED_CRITICAL : theme.TEXT_DIM }}>
            7G BARREL ROLL EVASION
          </label>
        </div>
      </div>
    </div>
  );
}
