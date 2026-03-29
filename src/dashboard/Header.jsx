/** Header — STRIKE-VECTOR fixed top header bar */
import React from 'react';
import { Shield, Crosshair, Clock } from 'lucide-react';
import theme from '../theme';
import { formatTime, formatRange } from '../utils/physicsUnits';

const headerStyle = {
  position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
  height: 52,
  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
  padding: '0 20px',
  background: `linear-gradient(180deg, ${theme.BG_ELEVATED} 0%, ${theme.BG_PRIMARY} 100%)`,
  borderBottom: `1px solid ${theme.BORDER_DIM}`,
  fontFamily: theme.FONT_MONO,
  backdropFilter: 'blur(12px)',
};

const logoStyle = {
  display: 'flex', alignItems: 'center', gap: 10,
  fontSize: 15, fontWeight: 700, letterSpacing: 2,
  color: theme.CYAN_PRIMARY,
  textShadow: `0 0 20px rgba(0,212,255,0.4)`,
};

const subtitleStyle = {
  fontSize: 10, color: theme.TEXT_DIM, letterSpacing: 1,
  marginLeft: 8
};

const metaStyle = {
  display: 'flex', gap: 20, alignItems: 'center',
  fontSize: 11, color: theme.TEXT_SECONDARY
};

const statusDot = (color) => ({
  display: 'inline-block', width: 6, height: 6,
  borderRadius: '50%', backgroundColor: color,
  marginRight: 6, boxShadow: `0 0 8px ${color}`
});

export default function Header({ status = 'READY', guidance = 'PNG', scenario = 'HEAD-ON', simTime = 0, range = null }) {
  return (
    <header style={headerStyle}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <div style={logoStyle}>
          <Shield size={18} />
          ◈ STRIKE-VECTOR
        </div>
        <span style={subtitleStyle}>[BVR ENGAGEMENT SIM v1.0]</span>
      </div>
      <div style={metaStyle}>
        <span><span style={statusDot(status === 'READY' ? theme.GREEN_OK : theme.AMBER_WARN)} />STATUS: {status}</span>
        <span style={{ color: theme.CYAN_DIM }}>|</span>
        <span><Crosshair size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />GUIDANCE: {guidance}</span>
        <span style={{ color: theme.CYAN_DIM }}>|</span>
        <span>SCENARIO: {scenario}</span>
      </div>
      <div style={metaStyle}>
        <span><Clock size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />SIM TIME: {formatTime(simTime)}</span>
        <span style={{ color: theme.CYAN_DIM }}>|</span>
        <span>RANGE: {range !== null ? formatRange(range) : '-.-- km'}</span>
      </div>
    </header>
  );
}
