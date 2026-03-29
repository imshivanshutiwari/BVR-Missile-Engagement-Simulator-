/** NezAnalysis — Page 3: NEZ Analysis */
import React from 'react';
import { NezPolarPlot } from '../../visualizations/PlotlyCharts';
import theme from '../../theme';

export default function NezAnalysis({ nezData, loading, onCompute }) {
  const nezPoints = nezData?.nez_points || [];

  return (
    <div style={{ padding: 12, overflow: 'auto', height: 'calc(100vh - 90px)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h2 style={{
          fontFamily: theme.FONT_MONO, fontSize: 14, fontWeight: 700,
          color: theme.CYAN_PRIMARY, letterSpacing: 2
        }}>
          NO-ESCAPE ZONE ANALYSIS
        </h2>
        <button className="btn primary" onClick={onCompute} disabled={loading}>
          {loading ? 'COMPUTING...' : 'COMPUTE NEZ'}
        </button>
      </div>

      {nezPoints.length > 0 ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div style={{ gridColumn: '1 / -1' }}>
            <NezPolarPlot nezPoints={nezPoints} />
          </div>
          <div className="panel">
            <div className="panel-header">NEZ STATISTICS</div>
            <div className="panel-body" style={{ fontFamily: theme.FONT_MONO, fontSize: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ color: theme.TEXT_DIM }}>Total Simulations:</span>
                <span style={{ color: theme.CYAN_PRIMARY }}>{nezData?.total_sims_run || 0}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ color: theme.TEXT_DIM }}>Computation Time:</span>
                <span style={{ color: theme.CYAN_PRIMARY }}>{(nezData?.computation_time_s || 0).toFixed(1)}s</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ color: theme.TEXT_DIM }}>NEZ Points:</span>
                <span style={{ color: theme.GREEN_OK }}>{nezPoints.filter(p => p.is_nez).length}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: theme.TEXT_DIM }}>Coverage:</span>
                <span style={{ color: theme.GREEN_OK }}>
                  {((nezPoints.filter(p => p.is_nez).length / Math.max(1, nezPoints.length)) * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
          <div className="panel">
            <div className="panel-header">LAR DATA</div>
            <div className="panel-body" style={{ fontFamily: theme.FONT_MONO, fontSize: 12 }}>
              {nezData?.lar_data && (
                <>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                    <span style={{ color: theme.TEXT_DIM }}>Max R_max:</span>
                    <span style={{ color: theme.CYAN_PRIMARY }}>
                      {(Math.max(...(nezData.lar_data.r_max || [0])) / 1000).toFixed(1)} km
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: theme.TEXT_DIM }}>Min R_min:</span>
                    <span style={{ color: theme.AMBER_WARN }}>
                      {(Math.min(...(nezData.lar_data.r_min || [0])) / 1000).toFixed(1)} km
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          height: 300,
          fontFamily: theme.FONT_MONO, fontSize: 13, color: theme.TEXT_DIM
        }}>
          ▸ CLICK "COMPUTE NEZ" TO GENERATE ENVELOPE
        </div>
      )}
    </div>
  );
}
