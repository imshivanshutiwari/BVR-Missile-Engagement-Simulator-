/** useTelemetry — SSE telemetry stream hook */
import { useState, useCallback, useRef, useEffect } from 'react';

export default function useTelemetry() {
  const [telemetry, setTelemetry] = useState([]);
  const [current, setCurrent] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [completed, setCompleted] = useState(null);
  const sourceRef = useRef(null);

  const startStream = useCallback((params = {}) => {
    if (sourceRef.current) sourceRef.current.close();
    setTelemetry([]);
    setCurrent(null);
    setCompleted(null);
    setIsStreaming(true);

    const qs = new URLSearchParams(params).toString();
    const es = new EventSource(`/api/telemetry/stream?${qs}`);
    sourceRef.current = es;

    es.addEventListener('telemetry', (e) => {
      const data = JSON.parse(e.data);
      setCurrent(data);
      setTelemetry(prev => [...prev, data]);
    });

    es.addEventListener('complete', (e) => {
      const data = JSON.parse(e.data);
      setCompleted(data);
      setIsStreaming(false);
      es.close();
    });

    es.onerror = () => {
      setIsStreaming(false);
      es.close();
    };
  }, []);

  const stopStream = useCallback(() => {
    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  useEffect(() => {
    return () => { if (sourceRef.current) sourceRef.current.close(); };
  }, []);

  return { telemetry, current, isStreaming, completed, startStream, stopStream };
}
