/** LaunchConsole — ARM + FIRE controls with pre-launch checklist */
import React, { useState } from 'react';
import { ShieldAlert, Flame, CheckCircle } from 'lucide-react';
import theme from '../../theme';

export default function LaunchConsole({ onLaunch, loading = false, disabled = false }) {
  const [armed, setArmed] = useState(false);

  const checklist = [
    { label: 'Target Lock', ok: true },
    { label: 'Guidance Initialized', ok: true },
    { label: 'Motor Armed', ok: armed },
    { label: 'NEZ Confirmed', ok: true },
  ];

  const handleArm = () => setArmed(!armed);
  const handleFire = () => {
    if (armed && onLaunch) onLaunch();
  };

  return (
    <div className="panel" style={{ borderColor: armed ? theme.RED_DIM : theme.BORDER_DIM }}>
      <div className="panel-header">
        <ShieldAlert size={14} />
        LAUNCH CONSOLE
      </div>
      <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {/* Checklist */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {checklist.map((item, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: 8,
              fontFamily: theme.FONT_MONO, fontSize: 11,
              color: item.ok ? theme.GREEN_OK : theme.TEXT_DIM
            }}>
              <CheckCircle size={12} style={{ opacity: item.ok ? 1 : 0.3 }} />
              {item.ok ? '✓' : '○'} {item.label}
            </div>
          ))}
        </div>

        {/* Buttons */}
        <button
          className={`btn ${armed ? 'danger' : ''}`}
          onClick={handleArm}
          style={{
            width: '100%',
            animation: armed ? 'pulse-red 1.5s infinite' : 'none',
            background: armed
              ? 'linear-gradient(135deg, rgba(255,51,51,0.2), rgba(255,51,51,0.05))'
              : undefined
          }}
        >
          <ShieldAlert size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
          {armed ? 'ARMED — CLICK TO SAFE' : 'ARM MISSILE'}
        </button>

        <button
          className="btn danger"
          onClick={handleFire}
          disabled={!armed || loading || disabled}
          style={{
            width: '100%', fontSize: 14, padding: '12px 16px',
            opacity: (!armed || loading) ? 0.4 : 1,
            cursor: (!armed || loading) ? 'not-allowed' : 'pointer',
            boxShadow: armed ? '0 0 30px rgba(255, 51, 51, 0.3)' : 'none'
          }}
        >
          <Flame size={16} style={{ marginRight: 6, verticalAlign: 'middle' }} />
          {loading ? 'SIMULATING...' : 'FIRE'}
        </button>
      </div>
    </div>
  );
}
