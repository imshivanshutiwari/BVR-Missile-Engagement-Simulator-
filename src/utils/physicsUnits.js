/** Physics Unit Conversions */

export const msToKmh = (ms) => ms * 3.6;
export const msToKnots = (ms) => ms * 1.94384;
export const mToKm = (m) => m / 1000;
export const mToFt = (m) => m * 3.28084;
export const radToDeg = (rad) => rad * (180 / Math.PI);
export const degToRad = (deg) => deg * (Math.PI / 180);
export const nToKn = (n) => n / 1000;
export const paToKpa = (pa) => pa / 1000;

export const formatMach = (m) => `M ${m.toFixed(2)}`;
export const formatAlt = (m) => `${(m / 1000).toFixed(1)} km`;
export const formatRange = (m) => `${(m / 1000).toFixed(1)} km`;
export const formatSpeed = (ms) => `${ms.toFixed(0)} m/s`;
export const formatG = (g) => `${g.toFixed(1)}g`;
export const formatPk = (pk) => `${(pk * 100).toFixed(1)}%`;
export const formatTime = (s) => {
  const mins = Math.floor(s / 60);
  const secs = (s % 60).toFixed(2);
  return `${String(mins).padStart(2, '0')}:${secs.padStart(5, '0')}`;
};
