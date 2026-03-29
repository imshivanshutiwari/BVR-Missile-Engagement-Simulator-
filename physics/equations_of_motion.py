"""3-DOF Point Mass Equations of Motion with RK4 Integration.

State vector: [x, y, z, vx, vy, vz] in NED frame.
x=North, y=East, z=Down (negative z = altitude above ground).
"""

import numpy as np
import math
from physics.constants import (
    G0, R_EARTH, MISSILE_REF_AREA, SIM_DT, SIM_MAX_TIME, INTERCEPT_DISTANCE
)
from physics.atmosphere import StandardAtmosphere1976
from physics.aerodynamics import MissileAerodynamics
from physics.propulsion import DualPulsePropulsion
from physics.utils.vector_math import magnitude, unit_vector, clip_vector
from physics.utils.integrator import rk4_step


class PointMassEOM:
    """3-DOF point mass equations of motion for missile flight."""

    def __init__(self, atmosphere=None, aerodynamics=None, propulsion=None):
        self.atm = atmosphere or StandardAtmosphere1976()
        self.aero = aerodynamics or MissileAerodynamics(self.atm)
        self.prop = propulsion or DualPulsePropulsion(self.atm)

    def _gravity(self, h_m: float) -> float:
        """Altitude-dependent gravity."""
        return G0 * (R_EARTH / (R_EARTH + h_m)) ** 2

    def derivatives(self, t: float, state: np.ndarray,
                    guidance_cmd: np.ndarray = None) -> np.ndarray:
        """Compute state derivatives.

        state = [x, y, z, vx, vy, vz]
        guidance_cmd = [ax_cmd, ay_cmd, az_cmd] acceleration command in m/s²

        Returns d_state/dt.
        """
        x, y, z, vx, vy, vz = state
        velocity = np.array([vx, vy, vz])
        speed = magnitude(velocity)
        h_m = max(-z, 0.0)  # altitude = -z in NED

        if guidance_cmd is None:
            guidance_cmd = np.zeros(3)

        # Current mass
        m = self.prop.mass(t)

        # ── Gravity (acts in +z direction in NED = downward) ──
        g = self._gravity(h_m)
        F_gravity = np.array([0.0, 0.0, m * g])

        # ── Aerodynamic forces ──
        if speed > 1.0:
            v_hat = velocity / speed

            # Angle of attack approximation from guidance commands
            lat_accel = guidance_cmd - np.dot(guidance_cmd, v_hat) * v_hat
            lat_mag = magnitude(lat_accel)
            alpha_rad = min(math.atan2(lat_mag, speed * 10.0), math.radians(25.0))

            mach = self.atm.mach_number(speed, h_m)
            q = self.atm.dynamic_pressure(speed, h_m)

            # Drag: opposes motion
            cd = self.aero.cd_total(mach, alpha_rad, h_m)
            F_drag = -cd * q * MISSILE_REF_AREA * v_hat

            # Lift: perpendicular to velocity, in the plane of the guidance command
            if lat_mag > 1e-6:
                lift_dir = unit_vector(lat_accel)
                cl = self.aero.cl(alpha_rad, mach)
                F_lift = cl * q * MISSILE_REF_AREA * lift_dir
            else:
                F_lift = np.zeros(3)
        else:
            F_drag = np.zeros(3)
            F_lift = np.zeros(3)

        # ── Thrust ──
        thrust_mag = self.prop.thrust(t, h_m)
        if speed > 1.0:
            # Thrust initially along velocity, then steered by guidance
            if magnitude(guidance_cmd) > 1e-6 and thrust_mag > 0:
                thrust_dir = unit_vector(velocity + guidance_cmd * 0.1)
            else:
                thrust_dir = unit_vector(velocity)
        else:
            thrust_dir = np.array([1.0, 0.0, 0.0])  # default forward
        F_thrust = thrust_mag * thrust_dir

        # ── Total acceleration ──
        F_total = F_gravity + F_drag + F_lift + F_thrust

        # Add guidance-commanded lateral acceleration (achieved via control surfaces)
        # This is the key: guidance commands are desired accelerations from PNG/APNG
        if guidance_cmd is not None and magnitude(guidance_cmd) > 0.01:
            # Remove the along-track component — only apply lateral guidance
            if speed > 1.0:
                v_hat = velocity / speed
                cmd_along = np.dot(guidance_cmd, v_hat) * v_hat
                cmd_lateral = guidance_cmd - cmd_along
                F_guidance = m * cmd_lateral
            else:
                F_guidance = m * guidance_cmd
            F_total = F_total + F_guidance

        accel = F_total / m

        return np.array([vx, vy, vz, accel[0], accel[1], accel[2]])

    def integrate_rk4(self, state0: np.ndarray, t_span: tuple,
                      dt: float, guidance_fn=None,
                      target_fn=None) -> dict:
        """Integrate missile trajectory using fixed-step RK4.

        state0: [x, y, z, vx, vy, vz]
        t_span: (t_start, t_end)
        dt: time step (default SIM_DT)
        guidance_fn: callable(t, missile_state, target_state) -> accel_cmd
        target_fn: callable(t) -> target_state [x,y,z,vx,vy,vz]

        Returns trajectory dict with all telemetry.
        """
        t_start, t_end = t_span
        state = state0.copy()
        t = t_start

        trajectory = {
            't': [], 'x': [], 'y': [], 'z': [],
            'vx': [], 'vy': [], 'vz': [],
            'mach': [], 'altitude': [], 'speed': [],
            'ax': [], 'ay': [], 'az': [],
            'mass': [], 'thrust': [], 'drag': [], 'lift': [],
            'q_dynamic': [], 'phase': [],
            'guidance_ax': [], 'guidance_ay': [], 'guidance_az': []
        }

        target_trajectory = {
            't': [], 'x': [], 'y': [], 'z': [],
            'vx': [], 'vy': [], 'vz': []
        }

        intercept_achieved = False
        miss_distance = float('inf')
        intercept_point = None

        while t <= t_end:
            x, y, z, vx, vy, vz = state
            speed = magnitude(np.array([vx, vy, vz]))
            h_m = max(-z, 0.0)

            # Target state
            if target_fn is not None:
                tgt_state = target_fn(t)
                tgt_pos = tgt_state[:3]
                target_trajectory['t'].append(t)
                target_trajectory['x'].append(tgt_state[0])
                target_trajectory['y'].append(tgt_state[1])
                target_trajectory['z'].append(tgt_state[2])
                target_trajectory['vx'].append(tgt_state[3])
                target_trajectory['vy'].append(tgt_state[4])
                target_trajectory['vz'].append(tgt_state[5])
            else:
                tgt_pos = None

            # Guidance command
            if guidance_fn is not None and target_fn is not None:
                guidance_cmd = guidance_fn(t, state, target_fn(t))
                # Add gravity bias compensation — PNG assumes zero-gravity
                # Must add upward accel to cancel gravity component normal to velocity
                h_m_cur = max(-z, 0.0)
                g_cur = self._gravity(h_m_cur)
                guidance_cmd = guidance_cmd + np.array([0.0, 0.0, -g_cur])
                guidance_cmd = clip_vector(guidance_cmd,
                                           30.0 * 9.80665)  # 30g max
            else:
                guidance_cmd = np.zeros(3)

            # Record telemetry
            mach = self.atm.mach_number(speed, h_m) if speed > 1.0 else 0.0
            q_dyn = self.atm.dynamic_pressure(speed, h_m)
            thrust_val = self.prop.thrust(t, h_m)
            phase = self.prop.phase(t)
            mass_val = self.prop.mass(t)

            # Drag magnitude
            if speed > 1.0:
                alpha = 0.0
                drag_val = self.aero.drag_force(speed, alpha, h_m)
                lift_val = self.aero.lift_force(speed, alpha, h_m)
            else:
                drag_val = 0.0
                lift_val = 0.0

            trajectory['t'].append(t)
            trajectory['x'].append(x)
            trajectory['y'].append(y)
            trajectory['z'].append(z)
            trajectory['vx'].append(vx)
            trajectory['vy'].append(vy)
            trajectory['vz'].append(vz)
            trajectory['mach'].append(mach)
            trajectory['altitude'].append(h_m)
            trajectory['speed'].append(speed)
            trajectory['ax'].append(guidance_cmd[0] if guidance_cmd is not None else 0)
            trajectory['ay'].append(guidance_cmd[1] if guidance_cmd is not None else 0)
            trajectory['az'].append(guidance_cmd[2] if guidance_cmd is not None else 0)
            trajectory['mass'].append(mass_val)
            trajectory['thrust'].append(thrust_val)
            trajectory['drag'].append(drag_val)
            trajectory['lift'].append(lift_val)
            trajectory['q_dynamic'].append(q_dyn)
            trajectory['phase'].append(phase)
            trajectory['guidance_ax'].append(guidance_cmd[0])
            trajectory['guidance_ay'].append(guidance_cmd[1])
            trajectory['guidance_az'].append(guidance_cmd[2])

            # Check intercept
            if tgt_pos is not None:
                missile_pos = np.array([x, y, z])
                dist = magnitude(missile_pos - tgt_pos)
                if dist < miss_distance:
                    miss_distance = dist
                if dist < INTERCEPT_DISTANCE:
                    intercept_achieved = True
                    intercept_point = {'x': x, 'y': y, 'z': z}
                    break

                # Check if missile has passed target (closing velocity negative)
                if len(trajectory['t']) > 50:
                    r_vec = tgt_pos - missile_pos
                    r_hat = r_vec / magnitude(r_vec) if magnitude(r_vec) > 0 else np.zeros(3)
                    v_missile = np.array([vx, vy, vz])
                    # closing = component of missile velocity toward target
                    closing = np.dot(v_missile, r_hat)
                    if closing < -100.0 and t > 5.0 and dist > INTERCEPT_DISTANCE:
                        # Missile has clearly passed target and is moving away
                        intercept_point = {'x': x, 'y': y, 'z': z}
                        break

            # Check ground impact
            if h_m <= 0 and t > 1.0:
                break

            # RK4 step
            def deriv_wrapper(t_loc, s_loc, *args):
                return self.derivatives(t_loc, s_loc, guidance_cmd)

            state = rk4_step(deriv_wrapper, t, state, dt)
            t += dt

        return {
            'trajectory': trajectory,
            'target_trajectory': target_trajectory,
            'intercept_achieved': intercept_achieved,
            'miss_distance_m': miss_distance,
            'time_of_flight_s': trajectory['t'][-1] if trajectory['t'] else 0,
            'intercept_point': intercept_point
        }

    def detect_intercept(self, missile_state: np.ndarray,
                         target_state: np.ndarray) -> bool:
        """Check if missile is within fuze radius of target."""
        m_pos = missile_state[:3]
        t_pos = target_state[:3]
        dist = magnitude(m_pos - t_pos)
        return dist < INTERCEPT_DISTANCE
