/** useSimulation — manages engagement simulation state */
import { useState, useCallback } from 'react';
import { runEngagement } from '../utils/api';

export default function useSimulation() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  const simulate = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const data = await runEngagement({
        scenario: 'head_on',
        guidance_law: 'png',
        launch_range_m: 20000,
        launch_altitude_m: 8000,
        target_speed_ms: 250,
        target_altitude_m: 8000,
        target_evasion: true,
        ...params
      });
      setResult(data);
      setHistory(prev => [...prev, {
        ...data.engagement_summary,
        timestamp: new Date().toISOString(),
        id: Date.now()
      }]);
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { result, loading, error, history, simulate, reset };
}
