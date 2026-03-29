# ◈ STRIKE-VECTOR

## BVR Missile Engagement Simulator with No-Escape Zone Computation, Proportional Navigation Guidance and Real-Time 3D Ops-Center Visualization

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react)
![Three.js](https://img.shields.io/badge/Three.js-r128-black?logo=three.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)

---

## 🎯 Overview

STRIKE-VECTOR is a physics-accurate BVR (Beyond Visual Range) missile engagement simulator that computes the **No-Escape Zone (NEZ)** — the 3D engagement envelope inside which a BVR missile guarantees intercept regardless of target evasive maneuver.

**Real-world application**: Used in mission planning for systems like DRDO ASTRA Mk-2, MBDA METEOR, and AIM-120 AMRAAM.

### Key Features

- **3-DOF Point Mass Dynamics** — Full missile flight dynamics with RK4 integration
- **Proportional Navigation (PNG, N=4)** + Augmented PNG with target acceleration compensation
- **Drag Polar Cd(Mach)** — Cubic spline with transonic bump and Mach-dependent lift
- **Dual-Pulse Boost-Sustain Thrust** — Altitude-compensated with ISP model
- **US Standard Atmosphere 1976** — 7-layer ISA with ρ(h), T(h), a(h), μ(h)
- **No-Escape Zone Engine** — 360° aspect sweep with full engagement sim at each point
- **F-16 Target Model** — 7g barrel roll evasive maneuver with bank-to-turn kinematics
- **Three.js 3D Scene** — Real-time engagement visualization with missile trails, explosions
- **25 Visualizations** — NEZ polar, Pk gauge, telemetry, drag polar, thrust curves, and more
- **30 Pytest Tests** — All using real physics, no mocks or `assert True`

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Installation

```bash
# Clone and enter
cd strike-vector

# Install all dependencies
pip install -r requirements.txt
npm install
```

### Run

```bash
# Terminal 1: Start physics server
uvicorn server.main:app --port 8000 --reload

# Terminal 2: Start React frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## 📐 Physics Equations

### Proportional Navigation Guidance
```
a_cmd = N × Vc × λ̇

Where:
  N = 4.0 (navigation constant)
  Vc = closing velocity = -(R⃗ · V_rel) / |R⃗|
  λ̇ = LOS rate = (R⃗ × V_rel) / |R⃗|²
```

### Augmented PNG
```
a_cmd = N × Vc × λ̇ + (N/2) × a_target
```

### 3-DOF Equations of Motion
```
dx/dt = vx
dvx/dt = (F_aero + F_thrust + F_gravity)_x / m(t)
(same for y, z)

Gravity: g(h) = g₀ × (R_earth / (R_earth + h))²
Drag: D = Cd(M) × q × S_ref
Thrust: T(h) = T_sl × (1 + k × (P₀ - P(h))/P₀)
```

### Probability of Kill
```
Pk = P_fuze × P_lethality × P_guidance
P_fuze = 1 - exp(-2.0 × (R_lethal/miss)²)
P_lethality = 1 - exp(-1.8 × (R_lethal/miss)²)
P_guidance = 1 - (miss/R_lethal)^0.7
```

---

## 🏗️ Architecture

```
strike-vector/
├── physics/           ← Pure Python physics engine
│   ├── atmosphere.py  ← US Std Atmosphere 1976
│   ├── aerodynamics.py ← Cd(Mach) drag polar
│   ├── propulsion.py  ← Dual-pulse thrust
│   ├── guidance/      ← PNG + APNG laws
│   ├── target/        ← F-16 model + evasion
│   └── engagement/    ← NEZ, Pk, engine
├── server/            ← FastAPI bridge (port 8000)
├── src/               ← React + Three.js frontend
│   ├── three-scene/   ← 3D engagement visualization
│   ├── dashboard/     ← Ops-center UI
│   └── visualizations/ ← 25 Plotly charts
└── tests/             ← 30 pytest tests
```

---

## 🧪 Testing

```bash
# Run all 30 tests
pytest tests/ -v --color=yes

# Verify physics engine
python -c "
from physics.engagement.engagement_engine import EngagementEngine
e = EngagementEngine()
r = e.run('head_on')
print(f'Intercept: {r[\"intercept_achieved\"]}, Miss: {r[\"miss_distance_m\"]:.2f}m, Pk: {r[\"pk\"]:.3f}')
"
```

---

## 📊 Scenarios

| Scenario | Geometry | Typical Pk | TOF Range |
|----------|----------|-----------|-----------|
| Head-On | M →→ ←← T | 70-98% | 8-25s |
| Tail-Chase | M →→ T →→ | 30-75% | 20-60s |
| 90° Crossing | M →→ T ↑↑ | 45-85% | 12-40s |

---

## 👨‍💻 Author

**Shivanshu** — Modelling & Simulation Project

---

## 📜 License

MIT License
