/** useNez — manages NEZ computation state */
import { useState, useCallback } from 'react';
import { computeNez } from '../utils/api';

export default function useNez() {
  const [nezData, setNezData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const compute = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const data = await computeNez({
        target_speed_ms: 250,
        target_altitude_m: 8000,
        guidance_law: 'png',
        resolution: 16,
        ...params
      });
      setNezData(data);
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { nezData, loading, error, compute };
}
