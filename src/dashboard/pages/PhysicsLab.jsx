/** PhysicsLab — Page 2: Physics Analysis */
import React from 'react';
import {
  TrajectoryPlot3D, AltitudeTimePlot, MachTimePlot,
  SpeedComponentsPlot, ForcesPlot
} from '../../visualizations/PlotlyCharts';
import theme from '../../theme';

export default function PhysicsLab({ result }) {
  const trajectory = result?.trajectory || [];
  const targetTraj = result?.target_trajectory || [];

  if (!trajectory.length) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: 'calc(100vh - 90px)',
        fontFamily: theme.FONT_MONO, fontSize: 14, color: theme.TEXT_DIM
      }}>
        ▸ RUN AN ENGAGEMENT TO VIEW PHYSICS DATA
      </div>
    );
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, padding: 12, overflow: 'auto', height: 'calc(100vh - 90px)' }}>
      <div style={{ gridColumn: '1 / -1' }}>
        <TrajectoryPlot3D trajectory={trajectory} targetTrajectory={targetTraj} />
      </div>
      <AltitudeTimePlot trajectory={trajectory} targetTrajectory={targetTraj} />
      <MachTimePlot trajectory={trajectory} />
      <SpeedComponentsPlot trajectory={trajectory} />
      <ForcesPlot trajectory={trajectory} />
    </div>
  );
}
