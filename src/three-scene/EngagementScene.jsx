/** EngagementScene — Main Three.js 3D engagement canvas */
import React, { useRef, useMemo, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Stars, Line, Html } from '@react-three/drei';
import * as THREE from 'three';

/* ── helpers ── */
function toScene(p) {
  // Physics NED: x=North, y=East, z=Down → Three.js: x=East, y=Up, z=-North  
  return [p.y || 0, -(p.z || 0), -(p.x || 0)];
}
function toSceneV3(p) {
  return new THREE.Vector3(p.y || 0, -(p.z || 0), -(p.x || 0));
}

/* ── Camera auto-fit ── */
function CameraRig({ missilePos, targetPos, hasData }) {
  const { camera } = useThree();
  const initialized = useRef(false);
  
  useEffect(() => {
    if (!hasData) return;
    if (initialized.current) return;
    initialized.current = true;
    
    const mx = missilePos[0], my = missilePos[1], mz = missilePos[2];
    const tx = targetPos[0], ty = targetPos[1], tz = targetPos[2];
    const cx = (mx + tx) / 2;
    const cy = Math.max(my, ty) + 5000;
    const cz = (mz + tz) / 2 + 15000;
    
    camera.position.set(cx, cy, cz);
    camera.lookAt(cx, (my + ty) / 2, (mz + tz) / 2);
    camera.updateProjectionMatrix();
  }, [hasData, missilePos, targetPos, camera]);

  return null;
}

/* ── Terrain Grid ── */
function TacticalGrid() {
  const lines = useMemo(() => {
    const pts = [];
    const size = 50000, step = 5000;
    for (let i = -size; i <= size; i += step) {
      pts.push([new THREE.Vector3(i, 0, -size), new THREE.Vector3(i, 0, size)]);
      pts.push([new THREE.Vector3(-size, 0, i), new THREE.Vector3(size, 0, i)]);
    }
    return pts;
  }, []);
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]}>
        <planeGeometry args={[120000, 120000]} />
        <meshStandardMaterial color="#060e08" roughness={0.95} />
      </mesh>
      {lines.map((pair, i) => (
        <Line key={i} points={pair} color="#0a2a0a" lineWidth={0.5} transparent opacity={0.4} />
      ))}
    </group>
  );
}

/* ── Range rings ── */
function RangeRings() {
  return (
    <group>
      {[5000, 10000, 20000, 40000].map((r, i) => (
        <group key={i}>
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 2, 0]}>
            <ringGeometry args={[r - 30, r + 30, 128]} />
            <meshBasicMaterial color="#1a3a1a" transparent opacity={0.3} side={THREE.DoubleSide} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

/* ── Missile body ── */
function MissileBody({ position, velocity }) {
  const ref = useRef();
  useEffect(() => {
    if (!ref.current || !velocity) return;
    const dir = new THREE.Vector3(...velocity).normalize();
    if (dir.length() > 0.01) {
      const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
      ref.current.quaternion.copy(quat);
    }
  }, [velocity]);

  const scale = 200; // Scale up for visibility
  return (
    <group ref={ref} position={position}>
      <mesh>
        <cylinderGeometry args={[18 * 1, 18 * 1, 730, 12]} />
        <meshStandardMaterial color="#8899aa" metalness={0.8} roughness={0.3} emissive="#334455" emissiveIntensity={0.3} />
      </mesh>
      <mesh position={[0, 420, 0]}>
        <coneGeometry args={[18, 100, 12]} />
        <meshStandardMaterial color="#667788" metalness={0.9} roughness={0.2} />
      </mesh>
      <pointLight color="#66bbff" intensity={3} distance={2000} />
      <pointLight color="#ff6600" intensity={2} distance={1500} position={[0, -400, 0]} />
    </group>
  );
}

/* ── Target aircraft ── */
function TargetAircraft({ position, label = 'F-16 TGT' }) {
  const scale = 300;
  return (
    <group position={position}>
      {/* fuselage */}
      <mesh>
        <boxGeometry args={[200, 100, 600]} />
        <meshStandardMaterial color="#aa2222" metalness={0.5} roughness={0.5} emissive="#660000" emissiveIntensity={0.4} />
      </mesh>
      {/* wings */}
      <mesh>
        <boxGeometry args={[800, 20, 300]} />
        <meshStandardMaterial color="#992222" metalness={0.5} roughness={0.5} />
      </mesh>
      {/* tail */}
      <mesh position={[0, 80, -250]}>
        <boxGeometry args={[20, 200, 100]} />
        <meshStandardMaterial color="#882222" />
      </mesh>
      <Html position={[0, 300, 0]} center style={{ pointerEvents: 'none' }}>
        <div style={{
          fontFamily: "'JetBrains Mono', monospace", fontSize: 11, fontWeight: 700,
          color: '#ff3333', background: 'rgba(5,8,16,0.85)',
          padding: '3px 8px', borderRadius: 3, border: '1px solid #ff333360',
          whiteSpace: 'nowrap', textShadow: '0 0 10px #ff3333'
        }}>
          ◆ {label}
        </div>
      </Html>
      <pointLight color="#ff4400" intensity={2} distance={1000} />
    </group>
  );
}

/* ── Trail ribbon ── */
function TrailRibbon({ points }) {
  if (!points || points.length < 2) return null;
  const maxPts = 800;
  const trail = points.slice(-maxPts);
  
  // Color each segment by phase
  const trailV3 = trail.map(p => new THREE.Vector3(p[0], p[1], p[2]));
  
  return (
    <group>
      <Line points={trailV3} color="#ff8800" lineWidth={3} transparent opacity={0.9} />
      <Line points={trailV3} color="#ffcc44" lineWidth={1.5} transparent opacity={0.5} />
    </group>
  );
}

/* ── Target trail ── */
function TargetTrail({ points }) {
  if (!points || points.length < 2) return null;
  const trail = points.slice(-800).map(p => new THREE.Vector3(p[0], p[1], p[2]));
  return <Line points={trail} color="#ff3333" lineWidth={1.5} transparent opacity={0.5} dashed dashScale={100} dashSize={200} gapSize={200} />;
}

/* ── Explosion ── */
function ExplosionEffect({ position, active }) {
  const particles = useMemo(() => {
    const pts = [];
    for (let i = 0; i < 400; i++) {
      pts.push(
        (Math.random() - 0.5) * 600,
        (Math.random() - 0.5) * 600,
        (Math.random() - 0.5) * 600
      );
    }
    return new Float32Array(pts);
  }, []);

  if (!active || !position) return null;
  return (
    <group position={position}>
      <pointLight color="#ffffff" intensity={80} distance={5000} decay={2} />
      <pointLight color="#ff6600" intensity={40} distance={3000} decay={2} />
      <points>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" count={400} array={particles} itemSize={3} />
        </bufferGeometry>
        <pointsMaterial color="#ffaa33" size={30} transparent opacity={0.9} sizeAttenuation />
      </points>
    </group>
  );
}

/* ── Main Scene ── */
export default function EngagementScene({ trajectoryData, targetTrajectory, currentFrame = 0, intercept = false }) {
  const hasData = trajectoryData && trajectoryData.length > 0;
  const safeFrame = hasData ? Math.min(currentFrame, trajectoryData.length - 1) : 0;

  const missilePos = useMemo(() => {
    if (!hasData) return [0, 8000, 0];
    return toScene(trajectoryData[safeFrame]);
  }, [trajectoryData, safeFrame, hasData]);

  const missileVel = useMemo(() => {
    if (!hasData) return [0, 0, -1];
    const p = trajectoryData[safeFrame];
    return [p.vy || 0, -(p.vz || 0), -(p.vx || 0)];
  }, [trajectoryData, safeFrame, hasData]);

  const targetPos = useMemo(() => {
    if (!targetTrajectory || !targetTrajectory.length) return [0, 8000, 20000];
    const sf = Math.min(safeFrame, targetTrajectory.length - 1);
    return toScene(targetTrajectory[sf]);
  }, [targetTrajectory, safeFrame]);

  const trailPoints = useMemo(() => {
    if (!hasData) return [];
    return trajectoryData.slice(0, safeFrame + 1).map(p => toScene(p));
  }, [trajectoryData, safeFrame, hasData]);

  const targetTrailPts = useMemo(() => {
    if (!targetTrajectory || !targetTrajectory.length) return [];
    const end = Math.min(safeFrame + 1, targetTrajectory.length);
    return targetTrajectory.slice(0, end).map(p => toScene(p));
  }, [targetTrajectory, safeFrame]);

  const interceptPos = useMemo(() => {
    if (!intercept || !hasData) return null;
    const last = trajectoryData[trajectoryData.length - 1];
    return toScene(last);
  }, [intercept, trajectoryData, hasData]);

  const showExplosion = intercept && safeFrame >= trajectoryData.length - 10;

  return (
    <div style={{ width: '100%', height: '100%', minHeight: 400 }}>
      <Canvas
        camera={{ position: [0, 15000, 25000], fov: 55, near: 1, far: 500000 }}
        gl={{ antialias: true, alpha: false }}
        style={{ background: '#000510' }}
      >
        <ambientLight intensity={0.4} />
        <directionalLight position={[30000, 50000, -30000]} intensity={0.6} />
        <Stars radius={200000} depth={80000} count={1500} factor={200} saturation={0} />

        <TacticalGrid />
        <RangeRings />

        <MissileBody position={missilePos} velocity={missileVel} />
        <TargetAircraft position={targetPos} />
        <TrailRibbon points={trailPoints} />
        <TargetTrail points={targetTrailPts} />
        <ExplosionEffect position={interceptPos} active={showExplosion} />

        {/* LOS line */}
        {hasData && (
          <Line
            points={[new THREE.Vector3(...missilePos), new THREE.Vector3(...targetPos)]}
            color="#00ffff" lineWidth={1} dashed dashScale={80} dashSize={300} gapSize={300}
            transparent opacity={0.3}
          />
        )}

        <CameraRig missilePos={missilePos} targetPos={targetPos} hasData={hasData} />
        <OrbitControls enableDamping dampingFactor={0.08} />
      </Canvas>
    </div>
  );
}
