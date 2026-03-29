/** GuidanceLab — Page 4: Guidance Analysis */
import React from 'react';
import { GuidanceErrorPlot, DragPolarPlot, ThrustCurvePlot, AtmosphereProfilePlot, EnergyStatePlot } from '../../visualizations/PlotlyCharts';
import theme from '../../theme';

export default function GuidanceLab({ result }) {
  const trajectory = result?.trajectory || [];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, padding: 12, overflow: 'auto', height: 'calc(100vh - 90px)' }}>
      <DragPolarPlot />
      <ThrustCurvePlot trajectory={trajectory} />
      <AtmosphereProfilePlot />
      <GuidanceErrorPlot trajectory={trajectory} />
      <EnergyStatePlot trajectory={trajectory} />
    </div>
  );
}
