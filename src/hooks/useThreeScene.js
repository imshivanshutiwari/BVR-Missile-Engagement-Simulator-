/** useThreeScene — Three.js scene lifecycle management */
import { useState, useCallback } from 'react';

export default function useThreeScene() {
  const [cameraMode, setCameraMode] = useState('free');
  const [playbackState, setPlaybackState] = useState('stopped');
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  const [currentFrame, setCurrentFrame] = useState(0);

  const setCameraModeWrapped = useCallback((mode) => {
    setCameraMode(mode);
  }, []);

  const togglePlayback = useCallback(() => {
    setPlaybackState(prev => prev === 'playing' ? 'paused' : 'playing');
  }, []);

  const stopPlayback = useCallback(() => {
    setPlaybackState('stopped');
    setCurrentFrame(0);
  }, []);

  const setSpeed = useCallback((speed) => {
    setPlaybackSpeed(speed);
  }, []);

  return {
    cameraMode, setCameraMode: setCameraModeWrapped,
    playbackState, togglePlayback, stopPlayback,
    playbackSpeed, setSpeed,
    currentFrame, setCurrentFrame
  };
}
