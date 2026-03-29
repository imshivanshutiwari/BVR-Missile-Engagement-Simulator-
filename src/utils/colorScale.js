/** Threat Color Maps and Scales */
import theme from '../theme';

export function pkToColor(pk) {
  if (pk >= 0.8) return theme.GREEN_OK;
  if (pk >= 0.5) return theme.AMBER_WARN;
  if (pk >= 0.3) return theme.AMBER_DIM;
  return theme.RED_CRITICAL;
}

export function machRegimeColor(mach) {
  if (mach < 0.8) return '#4488ff';       // subsonic
  if (mach < 1.2) return theme.AMBER_WARN; // transonic
  if (mach < 3.0) return theme.RED_CRITICAL; // supersonic
  return theme.PURPLE_INFO;                 // hypersonic
}

export function phaseColor(phase) {
  switch (phase) {
    case 'BOOST': return '#ff6600';
    case 'SUSTAIN': return '#ff9900';
    case 'COAST': return '#aaffff';
    default: return theme.TEXT_DIM;
  }
}

export function threatLevel(range_m, closing_vel) {
  if (range_m < 5000) return { level: 'CRITICAL', color: theme.RED_CRITICAL };
  if (range_m < 15000) return { level: 'HIGH', color: theme.AMBER_WARN };
  if (range_m < 30000) return { level: 'MEDIUM', color: theme.CYAN_PRIMARY };
  return { level: 'LOW', color: theme.GREEN_OK };
}

export const plotlyDarkLayout = {
  paper_bgcolor: 'rgba(9, 14, 28, 0.95)',
  plot_bgcolor: 'rgba(5, 8, 16, 0.95)',
  font: { family: "'JetBrains Mono', monospace", color: '#c8e8ff', size: 11 },
  xaxis: {
    gridcolor: '#1a2840', zerolinecolor: '#204060',
    tickfont: { color: '#7a9ab8' }
  },
  yaxis: {
    gridcolor: '#1a2840', zerolinecolor: '#204060',
    tickfont: { color: '#7a9ab8' }
  },
  margin: { t: 40, r: 20, b: 40, l: 50 },
  showlegend: true,
  legend: { font: { color: '#7a9ab8', size: 10 }, bgcolor: 'transparent' }
};
