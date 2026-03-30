/** Plotly-based visualization components for all chart types */
import React from 'react';
import Plot from 'react-plotly.js';
import { plotlyDarkLayout } from '../utils/colorScale';
import theme from '../theme';

const baseLayout = {
  ...plotlyDarkLayout,
  autosize: true,
  height: 300,
};

/** VIZ06: Trajectory 3D Plot */
export function TrajectoryPlot3D({ trajectory, targetTrajectory }) {
  const t = trajectory || [];
  const tgt = targetTrajectory || [];
  return (
    <div className="panel">
      <div className="panel-header">3D TRAJECTORY</div>
      <Plot
        data={[
          {
            type: 'scatter3d', mode: 'lines', name: 'Missile',
            x: t.map(p => (p.x || 0) / 1000),
            y: t.map(p => (p.y || 0) / 1000),
            z: t.map(p => (p.altitude || 0) / 1000),
            line: { color: theme.CYAN_PRIMARY, width: 3 }
          },
          {
            type: 'scatter3d', mode: 'lines', name: 'Target',
            x: tgt.map(p => (p.x || 0) / 1000),
            y: tgt.map(p => (p.y || 0) / 1000),
            z: tgt.map(p => (-(p.z || 0)) / 1000),
            line: { color: theme.RED_CRITICAL, width: 2, dash: 'dash' }
          }
        ]}
        layout={{
          ...baseLayout, height: 400,
          scene: {
            xaxis: { title: 'North (km)', gridcolor: '#1a2840', color: '#7a9ab8' },
            yaxis: { title: 'East (km)', gridcolor: '#1a2840', color: '#7a9ab8' },
            zaxis: { title: 'Alt (km)', gridcolor: '#1a2840', color: '#7a9ab8' },
            bgcolor: 'rgba(5,8,16,0.95)'
          },
          title: { text: 'Engagement Trajectory', font: { color: theme.CYAN_PRIMARY, size: 12 } }
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
}

/** VIZ07: Altitude vs Time */
export function AltitudeTimePlot({ trajectory, targetTrajectory }) {
  const t = trajectory || [];
  const tgt = targetTrajectory || [];
  return (
    <div className="panel">
      <div className="panel-header">ALTITUDE vs TIME</div>
      <Plot
        data={[
          { type: 'scatter', mode: 'lines', name: 'Missile Alt',
            x: t.map(p => p.t), y: t.map(p => (p.altitude || 0) / 1000),
            line: { color: theme.CYAN_PRIMARY, width: 2 } },
          { type: 'scatter', mode: 'lines', name: 'Target Alt',
            x: tgt.map(p => p.t), y: tgt.map(p => -(p.z || -8000) / 1000),
            line: { color: theme.RED_CRITICAL, width: 2, dash: 'dash' } }
        ]}
        layout={{ ...baseLayout,
          xaxis: { ...baseLayout.xaxis, title: 'Time (s)' },
          yaxis: { ...baseLayout.yaxis, title: 'Altitude (km)' },
          title: { text: 'Altitude Profile', font: { color: theme.CYAN_PRIMARY, size: 12 } }
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
}

/** VIZ08: Mach Number vs Time */
export function MachTimePlot({ trajectory }) {
  const t = trajectory || [];
  return (
    <div className="panel">
      <div className="panel-header">MACH NUMBER vs TIME</div>
      <Plot
        data={[
          { type: 'scatter', mode: 'lines', name: 'Mach',
            x: t.map(p => p.t), y: t.map(p => p.mach || 0),
            fill: 'tozeroy', fillcolor: 'rgba(0,212,255,0.1)',
            line: { color: theme.CYAN_PRIMARY, width: 2 } },
          { type: 'scatter', mode: 'lines', name: 'M=1 (Sonic)',
            x: t.length ? [t[0].t, t[t.length - 1].t] : [0, 1], y: [1, 1],
            line: { color: '#ffffff', width: 1, dash: 'dash' } }
        ]}
        layout={{ ...baseLayout,
          xaxis: { ...baseLayout.xaxis, title: 'Time (s)' },
          yaxis: { ...baseLayout.yaxis, title: 'Mach Number', range: [0, 4.5] },
          title: { text: 'Mach Number Profile', font: { color: theme.CYAN_PRIMARY, size: 12 } },
          shapes: [
            { type: 'rect', x0: 0, x1: 1e6, y0: 0, y1: 0.8, fillcolor: '#4488ff10', line: { width: 0 } },
            { type: 'rect', x0: 0, x1: 1e6, y0: 0.8, y1: 1.2, fillcolor: '#ffb30010', line: { width: 0 } },
            { type: 'rect', x0: 0, x1: 1e6, y0: 1.2, y1: 3.0, fillcolor: '#ff333310', line: { width: 0 } },
            { type: 'rect', x0: 0, x1: 1e6, y0: 3.0, y1: 5.0, fillcolor: '#9966ff10', line: { width: 0 } },
          ]
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
}

/** VIZ10: Forces Breakdown */
export function ForcesPlot({ trajectory }) {
  const t = trajectory || [];
  return (
    <div className="panel">
      <div className="panel-header">FORCES vs TIME</div>
      <Plot
        data={[
          { type: 'scatter', mode: 'lines', name: 'Thrust',
            x: t.map(p => p.t), y: t.map(p => (p.thrust || 0) / 1000),
            fill: 'tozeroy', fillcolor: 'rgba(255,102,0,0.15)',
            line: { color: '#ff6600', width: 2 } },
          { type: 'scatter', mode: 'lines', name: 'Drag',
            x: t.map(p => p.t), y: t.map(p => -(p.drag || 0) / 1000),
            fill: 'tozeroy', fillcolor: 'rgba(255,51,51,0.1)',
            line: { color: theme.RED_CRITICAL, width: 2 } },
          { type: 'scatter', mode: 'lines', name: 'Lift',
            x: t.map(p => p.t), y: t.map(p => (p.lift || 0) / 1000),
            line: { color: theme.GREEN_OK, width: 1 } }
        ]}
        layout={{ ...baseLayout,
          xaxis: { ...baseLayout.xaxis, title: 'Time (s)' },
          yaxis: { ...baseLayout.yaxis, title: 'Force (kN)' },
          title: { text: 'Forces Breakdown', font: { color: theme.CYAN_PRIMARY, size: 12 } }
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
}

/** VIZ09: Speed Components */
export function SpeedComponentsPlot({ trajectory }) {
  const t = trajectory || [];
  return (
    <div className="panel">
      <div className="panel-header">SPEED COMPONENTS vs TIME</div>
      <Plot
        data={[
          { type: 'scatter', mode: 'lines', name: 'Vx (North)',
            x: t.map(p => p.t), y: t.map(p => p.vx || 0),
            line: { color: theme.CYAN_PRIMARY, width: 2 } },
          { type: 'scatter', mode: 'lines', name: 'Vy (East)',
            x: t.map(p => p.t), y: t.map(p => p.vy || 0),
            line: { color: theme.AMBER_WARN, width: 2, dash: 'dot' } },
          { type: 'scatter', mode: 'lines', name: 'Vz (Down)',
            x: t.map(p => p.t), y: t.map(p => p.vz || 0),
            line: { color: theme.GREEN_OK, width: 2, dash: 'dash' } }
        ]}
        layout={{ ...baseLayout,
          xaxis: { ...baseLayout.xaxis, title: 'Time (s)' },
          yaxis: { ...baseLayout.yaxis, title: 'Velocity (m/s)' },
          title: { text: 'Velocity Components', font: { color: theme.CYAN_PRIMARY, size: 12 } }
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
}

/** VIZ11: NEZ Polar Plot */
export function NezPolarPlot({ nezPoints }) {
  const pts = nezPoints || [];
  const nezInside = pts.filter(p => p.is_nez);
  const nezOutside = pts.filter(p => !p.is_nez);

  return (
    <div className="panel">
      <div className="panel-header">NO-ESCAPE ZONE (POLAR)</div>
      <Plot
        data={[
          { type: 'scatterpolar', mode: 'markers', name: 'NEZ (Kill Zone)',
            r: nezInside.map(p => p.range_m / 1000),
            theta: nezInside.map(p => p.aspect_deg),
            marker: { color: theme.GREEN_OK, size: 6, opacity: 0.6 } },
          { type: 'scatterpolar', mode: 'markers', name: 'Outside NEZ',
            r: nezOutside.map(p => p.range_m / 1000),
            theta: nezOutside.map(p => p.aspect_deg),
            marker: { color: theme.RED_DIM, size: 4, opacity: 0.3 } }
        ]}
        layout={{
          ...baseLayout, height: 400,
          polar: {
            bgcolor: 'rgba(5,8,16,0.95)',
            angularaxis: { gridcolor: '#1a2840', linecolor: '#204060', tickfont: { color: '#7a9ab8', size: 9 } },
            radialaxis: { gridcolor: '#1a2840', linecolor: '#204060', tickfont: { color: '#7a9ab8', size: 9 },
              title: { text: 'Range (km)', font: { color: '#7a9ab8', size: 10 } } }
          },
          title: { text: 'NEZ Envelope', font: { color: theme.GREEN_OK, size: 12 } }
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
}

/** VIZ17: Thrust Curve */
export function ThrustCurvePlot({ trajectory }) {
  const t = trajectory || [];
  return (
    <div className="panel">
      <div className="panel-header">THRUST CURVE</div>
      <Plot
        data={[
          { type: 'scatter', mode: 'lines', name: 'Thrust', yaxis: 'y1',
            x: t.map(p => p.t), y: t.map(p => (p.thrust || 0) / 1000),
            fill: 'tozeroy',
            fillcolor: t.map(p => (p.phase === 'BOOST' ? 'rgba(255,102,0,0.2)' : 'rgba(255,153,0,0.15)'))[0],
            line: { color: '#ff6600', width: 2 } },
          { type: 'scatter', mode: 'lines', name: 'Mass', yaxis: 'y2',
            x: t.map(p => p.t), y: t.map(p => p.mass || 185),
            line: { color: theme.CYAN_PRIMARY, width: 1, dash: 'dot' } }
        ]}
        layout={{ ...baseLayout,
          xaxis: { ...baseLayout.xaxis, title: 'Time (s)' },
          yaxis: { ...baseLayout.yaxis, title: 'Thrust (kN)', side: 'left' },
          yaxis2: { title: 'Mass (kg)', side: 'right', overlaying: 'y',
            gridcolor: 'transparent', tickfont: { color: theme.CYAN_DIM } },
          title: { text: 'Thrust & Mass Profile', font: { color: '#ff6600', size: 12 } }
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
}

/** VIZ16: Drag Polar */
export function DragPolarPlot() {
  const machs = [];
  const cd0s = [];
  const cd0_table = [0.016, 0.018, 0.021, 0.026, 0.038, 0.042, 0.040, 0.036, 0.028, 0.022, 0.019, 0.018, 0.017, 0.017];
  const mach_table = [0.5, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0];
  for (let i = 0; i < mach_table.length; i++) {
    machs.push(mach_table[i]);
    cd0s.push(cd0_table[i]);
  }

  return (
    <div className="panel">
      <div className="panel-header">DRAG POLAR Cd vs MACH</div>
      <Plot
        data={[
          { type: 'scatter', mode: 'lines+markers', name: 'Cd0 (zero-lift)',
            x: machs, y: cd0s,
            line: { color: theme.CYAN_PRIMARY, width: 2 },
            marker: { color: theme.CYAN_PRIMARY, size: 4 } }
        ]}
        layout={{ ...baseLayout,
          xaxis: { ...baseLayout.xaxis, title: 'Mach Number' },
          yaxis: { ...baseLayout.yaxis, title: 'Cd0' },
          title: { text: 'Zero-Lift Drag Coefficient', font: { color: theme.CYAN_PRIMARY, size: 12 } },
          shapes: [{ type: 'line', x0: 1, x1: 1, y0: 0, y1: 0.05, line: { color: theme.RED_CRITICAL, width: 1, dash: 'dash' } }],
          annotations: [{ x: 1.0, y: 0.04, text: 'M=1', showarrow: false, font: { color: theme.RED_CRITICAL, size: 10 } },
            { x: 1.0, y: 0.038, text: 'Transonic bump', showarrow: true, arrowcolor: theme.AMBER_WARN,
              font: { color: theme.AMBER_WARN, size: 9 }, ax: 40, ay: -30 }]
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
}

/** VIZ18: Atmosphere Profile */
export function AtmosphereProfilePlot() {
  const alts = [];
  const temps = [], pressures = [], densities = [], sounds = [];
  for (let h = 0; h <= 20000; h += 500) {
    alts.push(h / 1000);
    const T = 288.15 - 6.5 * (h / 1000);
    temps.push(Math.max(216.65, T));
    pressures.push(101325 * Math.exp(-h / 8500) / 1000);
    densities.push(1.225 * Math.exp(-h / 8500));
    sounds.push(Math.sqrt(1.4 * 287 * Math.max(216.65, T)));
  }

  return (
    <div className="panel">
      <div className="panel-header">US STD ATMOSPHERE 1976</div>
      <Plot
        data={[
          { type: 'scatter', mode: 'lines', name: 'Temperature (K)',
            x: temps, y: alts, line: { color: theme.CYAN_PRIMARY, width: 2 } },
        ]}
        layout={{ ...baseLayout,
          xaxis: { ...baseLayout.xaxis, title: 'Temperature (K)' },
          yaxis: { ...baseLayout.yaxis, title: 'Altitude (km)' },
          title: { text: 'Temperature vs Altitude', font: { color: theme.CYAN_PRIMARY, size: 12 } }
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
}

/** VIZ05/VIZ19: Guidance Error Plot */
export function GuidanceErrorPlot({ trajectory }) {
  const t = trajectory || [];
  return (
    <div className="panel">
      <div className="panel-header">GUIDANCE COMMANDS</div>
      <Plot
        data={[
          { type: 'scatter', mode: 'lines', name: 'Lateral Cmd',
            x: t.map(p => p.t), y: t.map(p => (p.guidance_ay || 0) / 9.81),
            line: { color: theme.CYAN_PRIMARY, width: 1.5 } },
          { type: 'scatter', mode: 'lines', name: 'Vertical Cmd',
            x: t.map(p => p.t), y: t.map(p => (p.guidance_az || 0) / 9.81),
            line: { color: theme.AMBER_WARN, width: 1.5 } },
          { type: 'scatter', mode: 'lines', name: 'Zero',
            x: t.length ? [t[0].t, t[t.length - 1].t] : [0, 1], y: [0, 0],
            line: { color: '#ffffff', width: 0.5, dash: 'dash' } }
        ]}
        layout={{ ...baseLayout,
          xaxis: { ...baseLayout.xaxis, title: 'Time (s)' },
          yaxis: { ...baseLayout.yaxis, title: 'Accel Command (g)', range: [-55, 55] },
          title: { text: 'Guidance Acceleration Commands', font: { color: theme.CYAN_PRIMARY, size: 12 } }
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
}

/** VIZ22: Scenario Comparison Radar */
export function ScenarioRadarPlot({ history }) {
  const h = history || [];
  if (h.length === 0) return (
    <div className="panel">
      <div className="panel-header">SCENARIO COMPARISON</div>
      <div className="panel-body" style={{ color: theme.TEXT_DIM, textAlign: 'center', padding: 40 }}>
        Run multiple scenarios to compare
      </div>
    </div>
  );

  return (
    <div className="panel">
      <div className="panel-header">SCENARIO COMPARISON</div>
      <Plot
        data={h.slice(-3).map((item, i) => ({
          type: 'scatterpolar', fill: 'toself', name: item.scenario || `Run ${i + 1}`,
          r: [item.pk || 0, 1 - Math.min(1, (item.miss_distance_m || 100) / 100),
              Math.min(1, 30 / (item.time_of_flight_s || 30)), 0.7, 0.8, item.pk || 0],
          theta: ['Pk', 'Miss Inv', 'TOF Eff', 'NEZ Cov', 'Energy', 'Pk'],
          line: { color: [theme.CYAN_PRIMARY, theme.AMBER_WARN, theme.GREEN_OK][i] },
          fillcolor: [`${theme.CYAN_PRIMARY}20`, `${theme.AMBER_WARN}20`, `${theme.GREEN_OK}20`][i]
        }))}
        layout={{
          ...baseLayout, height: 350,
          polar: {
            bgcolor: 'rgba(5,8,16,0.95)',
            radialaxis: { range: [0, 1], gridcolor: '#1a2840', tickfont: { color: '#7a9ab8', size: 9 } },
            angularaxis: { gridcolor: '#1a2840', tickfont: { color: '#7a9ab8', size: 9 } }
          }
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
}

/** VIZ23: Engagement Timeline */
export function EngagementTimelinePlot({ trajectory }) {
  const t = trajectory || [];
  const events = [];
  let maxT = 0;
  t.forEach(p => {
    if (p.t > maxT) maxT = p.t;
  });

  const boostEnd = t.find(p => p.phase === 'SUSTAIN')?.t || 3.2;
  const sustainEnd = t.find(p => p.phase === 'COAST')?.t || 20;

  return (
    <div className="panel">
      <div className="panel-header">ENGAGEMENT TIMELINE</div>
      <Plot
        data={[
          { type: 'bar', name: 'BOOST', orientation: 'h',
            y: ['Missile Phase'], x: [boostEnd],
            marker: { color: 'rgba(255,102,0,0.6)' } },
          { type: 'bar', name: 'SUSTAIN', orientation: 'h',
            y: ['Missile Phase'], x: [sustainEnd - boostEnd], base: [boostEnd],
            marker: { color: 'rgba(255,153,0,0.6)' } },
          { type: 'bar', name: 'COAST', orientation: 'h',
            y: ['Missile Phase'], x: [maxT - sustainEnd], base: [sustainEnd],
            marker: { color: 'rgba(170,255,255,0.3)' } }
        ]}
        layout={{ ...baseLayout, height: 120, barmode: 'stack',
          xaxis: { ...baseLayout.xaxis, title: 'Time (s)' },
          yaxis: { ...baseLayout.yaxis },
          title: { text: 'Phase Timeline', font: { color: theme.CYAN_PRIMARY, size: 12 } }
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
}

/** VIZ25: Energy State */
export function EnergyStatePlot({ trajectory }) {
  const t = trajectory || [];
  return (
    <div className="panel">
      <div className="panel-header">ENERGY STATE DIAGRAM</div>
      <Plot
        data={[
          { type: 'scatter', mode: 'lines', name: 'Missile',
            x: t.map(p => p.speed || 0), y: t.map(p => (p.altitude || 0) / 1000),
            line: { color: theme.CYAN_PRIMARY, width: 2 },
            marker: { color: theme.CYAN_PRIMARY } }
        ]}
        layout={{ ...baseLayout,
          xaxis: { ...baseLayout.xaxis, title: 'Speed (m/s)' },
          yaxis: { ...baseLayout.yaxis, title: 'Altitude (km)' },
          title: { text: 'Speed vs Altitude (Energy State)', font: { color: theme.CYAN_PRIMARY, size: 12 } }
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
}
