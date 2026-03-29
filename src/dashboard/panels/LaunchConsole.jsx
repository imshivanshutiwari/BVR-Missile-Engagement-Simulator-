/** LaunchConsole — Simplified FIRE button (no arm step needed) */
import React, { useState } from 'react';
import { Flame, RotateCcw } from 'lucide-react';
import theme from '../../theme';

export default function LaunchConsole({ onLaunch, loading = false, disabled = false }) {
  const handleFire = () => {
    if (onLaunch) onLaunch();
  };

  return (
    <div style={{
      background: theme.BG_CARD,
      border: `1px solid ${loading ? theme.AMBER_WARN : theme.RED_CRITICAL}40`,
      borderRadius: 8, padding: 12,
    }}>
      <button
        onClick={handleFire}
        disabled={loading || disabled}
        style={{
          width: '100%',
          padding: '16px 20px',
          fontSize: 16,
          fontWeight: 800,
          fontFamily: theme.FONT_MONO,
          letterSpacing: 2,
          border: 'none',
          borderRadius: 6,
          cursor: loading ? 'wait' : 'pointer',
          color: '#ffffff',
          background: loading
            ? 'linear-gradient(135deg, #665500, #443300)'
            : 'linear-gradient(135deg, #cc0000, #990000)',
          boxShadow: loading
            ? '0 0 20px rgba(255,179,0,0.3)'
            : '0 0 30px rgba(255,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1)',
          transition: 'all 0.3s',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 10,
          animation: loading ? 'pulse-red 1.5s infinite' : 'none',
        }}
      >
        {loading ? (
          <>
            <RotateCcw size={18} style={{ animation: 'spin 1s linear infinite' }} />
            SIMULATING...
          </>
        ) : (
          <>
            <Flame size={20} />
            🔥 FIRE MISSILE
          </>
        )}
      </button>
      <div style={{
        marginTop: 8, textAlign: 'center',
        fontFamily: theme.FONT_MONO, fontSize: 9,
        color: theme.TEXT_DIM, letterSpacing: 1
      }}>
        {loading ? 'COMPUTING TRAJECTORY...' : 'CLICK TO LAUNCH • HEAD-ON ENGAGEMENT'}
      </div>
    </div>
  );
}
