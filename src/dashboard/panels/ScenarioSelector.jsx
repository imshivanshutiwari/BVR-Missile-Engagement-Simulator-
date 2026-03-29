/** ScenarioSelector — Choose engagement scenario */
import React from 'react';
import { Map } from 'lucide-react';
import theme from '../../theme';

const scenarios = [
  { id: 'head_on', name: 'HEAD-ON', desc: 'Max closing velocity', icon: '→←' },
  { id: 'tail_chase', name: 'TAIL-CHASE', desc: 'Energy-critical pursuit', icon: '→→' },
  { id: 'crossing', name: '90° CROSSING', desc: 'High LOS rate', icon: '→↑' },
];

export default function ScenarioSelector({ selected = 'head_on', onChange }) {
  return (
    <div className="panel">
      <div className="panel-header"><Map size={14} />SCENARIO</div>
      <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {scenarios.map(s => (
          <button
            key={s.id}
            onClick={() => onChange && onChange(s.id)}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '8px 12px', borderRadius: 4, cursor: 'pointer',
              background: selected === s.id ? `${theme.CYAN_PRIMARY}15` : theme.BG_ELEVATED,
              border: `1px solid ${selected === s.id ? theme.CYAN_DIM : theme.BORDER_DIM}`,
              color: selected === s.id ? theme.CYAN_PRIMARY : theme.TEXT_SECONDARY,
              fontFamily: theme.FONT_MONO, fontSize: 11, fontWeight: 600,
              letterSpacing: 1, transition: 'all 0.2s'
            }}
          >
            <span>{s.icon} {s.name}</span>
            <span style={{ fontSize: 9, color: theme.TEXT_DIM }}>{s.desc}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
