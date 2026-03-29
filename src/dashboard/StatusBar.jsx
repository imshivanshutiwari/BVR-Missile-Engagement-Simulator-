/** StatusBar — System status indicators below header */
import React from 'react';
import theme from '../theme';

const barStyle = {
  position: 'fixed', top: 52, left: 0, right: 0, zIndex: 99,
  display: 'flex', gap: 4, padding: '4px 20px',
  background: theme.BG_SECONDARY,
  borderBottom: `1px solid ${theme.BORDER_DIM}`,
  fontFamily: theme.FONT_MONO,
  fontSize: 10, fontWeight: 600, letterSpacing: 1,
  overflowX: 'auto'
};

const chipStyle = (color) => ({
  display: 'inline-flex', alignItems: 'center', gap: 4,
  padding: '3px 8px', borderRadius: 3,
  background: `${color}15`,
  border: `1px solid ${color}40`,
  color: color,
  whiteSpace: 'nowrap'
});

export default function StatusBar({ serverConnected = true }) {
  const items = [
    { label: 'PHYSICS: ONLINE', color: theme.GREEN_OK },
    { label: 'GUIDANCE: PNG-N4', color: theme.CYAN_PRIMARY },
    { label: 'ATMOSPHERE: ISA-1976', color: theme.CYAN_PRIMARY },
    { label: 'TARGET: F-16 CLASS', color: theme.AMBER_WARN },
    { label: 'NEZ: READY', color: theme.PURPLE_INFO },
    { label: `SERVER: ${serverConnected ? 'CONNECTED' : 'OFFLINE'}`,
      color: serverConnected ? theme.GREEN_OK : theme.RED_CRITICAL },
  ];

  return (
    <div style={barStyle}>
      {items.map((item, i) => (
        <span key={i} style={chipStyle(item.color)}>
          <span style={{
            width: 5, height: 5, borderRadius: '50%',
            background: item.color, boxShadow: `0 0 6px ${item.color}`
          }} />
          {item.label}
        </span>
      ))}
    </div>
  );
}
