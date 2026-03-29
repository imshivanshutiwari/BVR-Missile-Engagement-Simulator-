/** EngagementScene — Main Three.js 3D engagement canvas */
import React, { useRef, useMemo, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Stars, Line, Text, Html } from '@react-three/drei';
import * as THREE from 'three';

function EarthTerrain() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
      <planeGeometry args={[200000, 200000, 64, 64]} />
      <meshStandardMaterial color="#0a1a0a" roughness={0.9} metalness={0.1} />
    </mesh>
  );
}

function TacticalGrid() {
  const lines = useMemo(() => {
    const pts = [];
    for (let i = -100000; i <= 100000; i += 10000) {
      pts.push([new THREE.Vector3(i, 0.5, -100000), new THREE.Vector3(i, 0.5, 100000)]);
      pts.push([new THREE.Vector3(-100000, 0.5, i), new THREE.Vector3(100000, 0.5, i)]);
    }
    return pts;
  }, []);

  return (
    <group>
      {lines.map((pair, i) => (
        <Line key={i} points={pair} color="#1a3a1a" lineWidth={0.5} opacity={0.3} transparent />
      ))}
    </group>
  );
}

function RangeRings() {
  const rings = [10000, 30000, 60000];
  return (
    <group>
      {rings.map((r, i) => (
        <mesh key={i} rotation={[-Math.PI / 2, 0, 0]} position={[0, 1, 0]}>
          <ringGeometry args={[r - 50, r + 50, 128]} />
          <meshBasicMaterial color="#1a3a1a" transparent opacity={0.4} side={THREE.DoubleSide} />
        </mesh>
      ))}
    </group>
  );
}

function MissileBody({ position, velocity }) {
  const ref = useRef();
  useEffect(() => {
    if (ref.current && velocity) {
      const dir = new THREE.Vector3(velocity[0], velocity[2], velocity[1]).normalize();
      const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
      ref.current.quaternion.copy(quat);
    }
  }, [velocity]);

  return (
    <group ref={ref} position={position || [0, 8000, 0]}>
      <mesh>
        <cylinderGeometry args={[0.089, 0.089, 3.65, 12]} />
        <meshStandardMaterial color="#8899aa" metalness={0.8} roughness={0.3} />
      </mesh>
      <mesh position={[0, 2.1, 0]}>
        <coneGeometry args={[0.089, 0.5, 12]} />
        <meshStandardMaterial color="#667788" metalness={0.9} roughness={0.2} />
      </mesh>
      {[0, 90, 180, 270].map((angle, i) => (
        <mesh key={i} position={[Math.cos(angle * Math.PI / 180) * 0.12, -1.6, Math.sin(angle * Math.PI / 180) * 0.12]}>
          <boxGeometry args={[0.01, 0.3, 0.2]} />
          <meshStandardMaterial color="#556677" />
        </mesh>
      ))}
      <pointLight color="#aaddff" intensity={2} distance={50} />
    </group>
  );
}

function AircraftMesh({ position, color = '#aa3333', label = 'TGT' }) {
  return (
    <group position={position || [50000, 8000, 0]}>
      <mesh>
        <boxGeometry args={[14, 3, 10]} />
        <meshStandardMaterial color={color} metalness={0.6} roughness={0.4} />
      </mesh>
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[4, 1, 18]} />
        <meshStandardMaterial color={color} metalness={0.6} roughness={0.4} />
      </mesh>
      <Html position={[0, 10, 0]} center style={{ pointerEvents: 'none' }}>
        <div style={{
          fontFamily: "'JetBrains Mono', monospace", fontSize: 10,
          color: '#ff3333', background: 'rgba(5,8,16,0.8)',
          padding: '2px 6px', borderRadius: 3, border: '1px solid #991a1a',
          whiteSpace: 'nowrap'
        }}>
          ◆ {label}
        </div>
      </Html>
      <pointLight color="#ff6600" intensity={1} distance={30} />
    </group>
  );
}

function TrailRibbon({ points, phase = 'BOOST' }) {
  if (!points || points.length < 2) return null;
  const colors = {
    BOOST: '#ff6600', SUSTAIN: '#ff9900', COAST: '#aaffff'
  };
  const trailPts = points.slice(-500).map(p =>
    new THREE.Vector3(p[0], p[2] || 0, p[1] || 0)
  );
  return <Line points={trailPts} color={colors[phase] || '#00d4ff'} lineWidth={3} opacity={0.8} transparent />;
}

function ExplosionEffect({ position, active }) {
  const ref = useRef();
  const particles = useMemo(() => {
    const pts = [];
    for (let i = 0; i < 200; i++) {
      pts.push(new THREE.Vector3(
        (Math.random() - 0.5) * 100,
        (Math.random() - 0.5) * 100,
        (Math.random() - 0.5) * 100
      ));
    }
    return pts;
  }, []);

  if (!active || !position) return null;
  return (
    <group position={position}>
      <pointLight color="#ffffff" intensity={50} distance={500} decay={2} />
      <pointLight color="#ff6600" intensity={30} distance={300} decay={2} />
      <points>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={particles.length}
            array={new Float32Array(particles.flatMap(p => [p.x, p.y, p.z]))}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial color="#ffaa33" size={5} transparent opacity={0.8} />
      </points>
    </group>
  );
}

export default function EngagementScene({ trajectoryData, targetTrajectory, currentFrame = 0, intercept = false }) {
  const missilePos = useMemo(() => {
    if (!trajectoryData || !trajectoryData.length || currentFrame >= trajectoryData.length) return [0, 8000, 0];
    const p = trajectoryData[currentFrame];
    return [p.x || 0, -(p.z || -8000), p.y || 0];
  }, [trajectoryData, currentFrame]);

  const missileVel = useMemo(() => {
    if (!trajectoryData || !trajectoryData.length || currentFrame >= trajectoryData.length) return [1, 0, 0];
    const p = trajectoryData[currentFrame];
    return [p.vx || 1, -(p.vz || 0), p.vy || 0];
  }, [trajectoryData, currentFrame]);

  const targetPos = useMemo(() => {
    if (!targetTrajectory || !targetTrajectory.length || currentFrame >= targetTrajectory.length) return [50000, 8000, 0];
    const p = targetTrajectory[currentFrame];
    return [p.x || 50000, -(p.z || -8000), p.y || 0];
  }, [targetTrajectory, currentFrame]);

  const trailPoints = useMemo(() => {
    if (!trajectoryData) return [];
    return trajectoryData.slice(0, currentFrame + 1).map(p => [p.x || 0, p.y || 0, -(p.z || -8000)]);
  }, [trajectoryData, currentFrame]);

  const interceptPos = useMemo(() => {
    if (!intercept || !trajectoryData || !trajectoryData.length) return null;
    const last = trajectoryData[trajectoryData.length - 1];
    return [last.x || 0, -(last.z || -8000), last.y || 0];
  }, [intercept, trajectoryData]);

  return (
    <div style={{ width: '100%', height: '100%', minHeight: 400, borderRadius: 8, overflow: 'hidden' }}>
      <Canvas
        camera={{ position: [0, 15000, -30000], fov: 60, near: 1, far: 500000 }}
        gl={{ antialias: true, alpha: false }}
        style={{ background: '#000510' }}
      >
        <ambientLight intensity={0.3} />
        <directionalLight position={[50000, 50000, -50000]} intensity={0.5} />
        <Stars radius={300000} depth={100000} count={2000} factor={100} saturation={0} />
        <EarthTerrain />
        <TacticalGrid />
        <RangeRings />
        <MissileBody position={missilePos} velocity={missileVel} />
        <AircraftMesh position={targetPos} label="F-16 TGT" />
        <TrailRibbon points={trailPoints} />
        <ExplosionEffect position={interceptPos} active={intercept && currentFrame >= (trajectoryData?.length || 0) - 5} />
        {missilePos && targetPos && (
          <Line
            points={[new THREE.Vector3(...missilePos), new THREE.Vector3(...targetPos)]}
            color="#00ffff" lineWidth={1} dashed dashScale={50} dashSize={500} gapSize={500}
            transparent opacity={0.4}
          />
        )}
        <OrbitControls enableDamping dampingFactor={0.05} />
      </Canvas>
    </div>
  );
}
