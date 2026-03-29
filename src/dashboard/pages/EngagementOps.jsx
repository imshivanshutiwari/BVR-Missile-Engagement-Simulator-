/** EngagementOps — Page 1: Main Ops Center */
import React from 'react';
import EngagementScene from '../../three-scene/EngagementScene';
import TelemetryPanel from '../panels/TelemetryPanel';
import LaunchConsole from '../panels/LaunchConsole';
import ScenarioSelector from '../panels/ScenarioSelector';
import MissileConfig from '../panels/MissileConfig';
import TargetConfig from '../panels/TargetConfig';
import PkGauge from '../../visualizations/PkGauge';
import EngagementStatusBoard from '../../visualizations/EngagementStatusBoard';
import { GuidanceErrorPlot, EngagementTimelinePlot } from '../../visualizations/PlotlyCharts';
import theme from '../../theme';

export default function EngagementOps({ result, loading, onLaunch, config, setConfig, telemetry }) {
  const trajectory = result?.trajectory || [];
  const targetTraj = result?.target_trajectory || [];
  const summary = result?.engagement_summary || {};
  const pk = result?.pk || 0;
  const pkBreakdown = result?.pk_breakdown || {};
  const frame = trajectory.length > 0 ? trajectory.length - 1 : 0;
  const lastTelemetry = trajectory.length > 0 ? trajectory[trajectory.length - 1] : {};

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '1fr 300px',
      gridTemplateRows: 'auto auto',
      gap: 12, padding: 12, height: 'calc(100vh - 90px)'
    }}>
      {/* Left: 3D Scene + Charts */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, overflow: 'auto' }}>
        <div style={{ flex: '0 0 450px', borderRadius: 8, border: `1px solid ${theme.BORDER_DIM}`, overflow: 'hidden' }}>
          <EngagementScene
            trajectoryData={trajectory}
            targetTrajectory={targetTraj}
            currentFrame={frame}
            intercept={result?.intercept_achieved}
          />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <EngagementStatusBoard summary={summary} />
          <PkGauge pk={pk} breakdown={pkBreakdown} />
        </div>
        <GuidanceErrorPlot trajectory={trajectory} />
        <EngagementTimelinePlot trajectory={trajectory} />
      </div>

      {/* Right: Controls + Telemetry */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, overflow: 'auto' }}>
        <TelemetryPanel data={telemetry || lastTelemetry} />
        <ScenarioSelector
          selected={config?.scenario || 'head_on'}
          onChange={(s) => setConfig && setConfig(prev => ({ ...prev, scenario: s }))}
        />
        <MissileConfig config={config} onChange={setConfig} />
        <TargetConfig config={config} onChange={setConfig} />
        <LaunchConsole onLaunch={onLaunch} loading={loading} />
      </div>
    </div>
  );
}
