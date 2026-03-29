"""Fixed-Step RK4 Integrator for ODE systems."""

import numpy as np


def rk4_step(f, t: float, state: np.ndarray, dt: float, *args) -> np.ndarray:
    """Single RK4 integration step.

    f: callable f(t, state, *args) -> d_state/dt
    t: current time
    state: current state vector
    dt: time step
    *args: additional arguments passed to f
    """
    k1 = f(t, state, *args)
    k2 = f(t + 0.5 * dt, state + 0.5 * dt * k1, *args)
    k3 = f(t + 0.5 * dt, state + 0.5 * dt * k2, *args)
    k4 = f(t + dt, state + dt * k3, *args)
    return state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def integrate_rk4(f, state0: np.ndarray, t_span: tuple, dt: float,
                  callback=None, *args) -> dict:
    """Integrate ODE system using fixed-step RK4.

    f: callable f(t, state, *args) -> d_state/dt
    state0: initial state vector
    t_span: (t_start, t_end)
    dt: fixed time step
    callback: optional callable(t, state) returning True to stop early
    *args: additional arguments to f

    Returns dict with 't' and 'states' arrays.
    """
    t_start, t_end = t_span
    n_steps = int((t_end - t_start) / dt) + 1

    times = [t_start]
    states = [state0.copy()]
    state = state0.copy()
    t = t_start

    for _ in range(n_steps):
        if t >= t_end:
            break

        state = rk4_step(f, t, state, dt, *args)
        t += dt
        times.append(t)
        states.append(state.copy())

        if callback is not None and callback(t, state):
            break

    return {
        't': np.array(times),
        'states': np.array(states)
    }
