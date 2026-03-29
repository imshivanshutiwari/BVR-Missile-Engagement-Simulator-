/** EngagementHistory — Page 5: History & Comparison */
import React from 'react';
import { ScenarioRadarPlot } from '../../visualizations/PlotlyCharts';
import theme from '../../theme';

export default function EngagementHistory({ history = [] }) {
  return (
    <div style={{ padding: 12, overflow: 'auto', height: 'calc(100vh - 90px)' }}>
      <h2 style={{
        fontFamily: theme.FONT_MONO, fontSize: 14, fontWeight: 700,
        color: theme.CYAN_PRIMARY, letterSpacing: 2, marginBottom: 12
      }}>
        ENGAGEMENT HISTORY
      </h2>

      {/* History Table */}
      <div className="panel" style={{ marginBottom: 12 }}>
        <div className="panel-header">ENGAGEMENT LOG</div>
        <div className="panel-body" style={{ overflowX: 'auto' }}>
          <table style={{
            width: '100%', borderCollapse: 'collapse',
            fontFamily: theme.FONT_MONO, fontSize: 11
          }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${theme.BORDER_NORMAL}` }}>
                {['#', 'SCENARIO', 'GUIDANCE', 'RANGE', 'TOF(s)', 'MISS(m)', 'Pk', 'INTERCEPT'].map(h => (
                  <th key={h} style={{
                    padding: '8px 6px', textAlign: 'left',
                    color: theme.TEXT_DIM, fontSize: 9, fontWeight: 600,
                    letterSpacing: 1
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {history.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ padding: 20, textAlign: 'center', color: theme.TEXT_DIM }}>
                    No engagements run yet
                  </td>
                </tr>
              )}
              {history.map((h, i) => (
                <tr key={h.id || i} style={{
                  borderBottom: `1px solid ${theme.BORDER_DIM}`,
                  background: h.intercept_achieved ? 'rgba(0,255,136,0.03)' : 'rgba(255,51,51,0.03)'
                }}>
                  <td style={{ padding: '6px', color: theme.TEXT_DIM }}>{i + 1}</td>
                  <td style={{ padding: '6px', color: theme.TEXT_PRIMARY }}>
                    {(h.scenario || '').replace('_', '-').toUpperCase()}
                  </td>
                  <td style={{ padding: '6px', color: theme.PURPLE_INFO }}>
                    {(h.guidance_law || 'PNG').toUpperCase()}
                  </td>
                  <td style={{ padding: '6px', color: theme.CYAN_PRIMARY }}>
                    {((h.launch_range_m || 0) / 1000).toFixed(0)} km
                  </td>
                  <td style={{ padding: '6px', color: theme.TEXT_PRIMARY }}>
                    {(h.time_of_flight_s || 0).toFixed(1)}
                  </td>
                  <td style={{ padding: '6px', color: (h.miss_distance_m || 0) < 15 ? theme.GREEN_OK : theme.RED_CRITICAL }}>
                    {(h.miss_distance_m || 0).toFixed(1)}
                  </td>
                  <td style={{ padding: '6px', color: (h.pk || 0) > 0.5 ? theme.GREEN_OK : theme.RED_CRITICAL }}>
                    {((h.pk || 0) * 100).toFixed(1)}%
                  </td>
                  <td style={{ padding: '6px' }}>
                    <span style={{
                      padding: '2px 6px', borderRadius: 3, fontSize: 9,
                      background: h.intercept_achieved ? `${theme.GREEN_OK}20` : `${theme.RED_CRITICAL}20`,
                      color: h.intercept_achieved ? theme.GREEN_OK : theme.RED_CRITICAL
                    }}>
                      {h.intercept_achieved ? 'YES' : 'NO'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Radar Comparison */}
      <ScenarioRadarPlot history={history} />
    </div>
  );
}
