"""AI Training Data Generator — Generates training samples from APNG engagements.

Runs thousands of randomized missile engagements using the proven APNG guidance law
and records every (state → acceleration_command) pair as training data for the
Neural Network to learn from.
"""

import sys
import os
import random
import numpy as np
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from physics.engagement.engagement_engine import EngagementEngine
from physics.guidance.apng_law import AugmentedProportionalNavigation
from physics.target.target_predictor import TargetPredictor
from physics.target.f16_model import F16KinematicModel
from physics.constants import SIM_DT, SIM_MAX_TIME, NAV_CONSTANT_N


def generate_state_action_pairs(num_engagements=2000):
    """Run randomized engagements and collect (state, action) pairs.
    
    State vector (12D):
        [rel_pos_x, rel_pos_y, rel_pos_z,   # target relative position
         rel_vel_x, rel_vel_y, rel_vel_z,    # relative velocity
         missile_vx, missile_vy, missile_vz,  # missile velocity
         target_ax, target_ay, target_az]     # estimated target acceleration
    
    Action vector (3D):
        [a_cmd_x, a_cmd_y, a_cmd_z]          # APNG acceleration command
    """
    engine = EngagementEngine()
    guidance = AugmentedProportionalNavigation(N=NAV_CONSTANT_N)
    
    all_states = []
    all_actions = []
    
    scenarios = ["head_on", "tail_chase", "crossing"]
    
    print(f"🧠 Generating training data from {num_engagements} engagements...")
    start_time = time.time()
    
    successful = 0
    for i in range(num_engagements):
        scenario = random.choice(scenarios)
        launch_range = random.uniform(10000, 30000)
        launch_alt = random.uniform(4000, 12000)
        target_speed = random.uniform(180, 320)
        target_alt = random.uniform(4000, 12000)
        evasion = random.choice([True, True, True, False])  # 75% evasion
        
        try:
            setup = engine.setup_engagement(
                scenario=scenario,
                launch_range_m=launch_range,
                launch_altitude_m=launch_alt,
                target_speed_ms=target_speed,
                target_altitude_m=target_alt,
                guidance_law="apng",
                target_evasion=evasion
            )
            
            target = setup['target']
            missile_state = np.concatenate([setup['missile_pos'], setup['missile_vel']])
            predictor = TargetPredictor()
            
            def target_fn(t):
                if evasion:
                    return target.evasive_barrel_roll(t)
                return target.straight_and_level(t)
            
            # Simulate step-by-step and record every guidance decision
            t = 0.0
            dt = SIM_DT
            max_steps = int(SIM_MAX_TIME / dt)
            
            for step in range(max_steps):
                target_state = target_fn(t)
                predictor.update(t, target_state)
                target_accel = predictor.get_acceleration()
                
                # Compute the "expert" APNG command
                a_cmd = guidance.compute(missile_state, target_state, target_accel)
                
                # Build relative state vector
                rel_pos = target_state[:3] - missile_state[:3]
                rel_vel = target_state[3:6] - missile_state[3:6]
                missile_vel = missile_state[3:6]
                
                state_vec = np.concatenate([rel_pos, rel_vel, missile_vel, target_accel])
                
                # Only record if missile is still moving and range > 10m
                range_m = np.linalg.norm(rel_pos)
                speed = np.linalg.norm(missile_vel)
                if speed > 50.0 and range_m > 10.0 and step % 3 == 0:
                    all_states.append(state_vec.copy())
                    all_actions.append(a_cmd.copy())
                
                # Simple Euler step for data generation
                deriv = engine.eom.derivatives(t, missile_state, a_cmd)
                missile_state = missile_state + deriv * dt
                t += dt
                
                # Check range
                if range_m < 5.0 or range_m > 100000 or t > SIM_MAX_TIME:
                    break
            
            successful += 1
            
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i+1}/{num_engagements} | Samples grabbed so far: {len(all_states)}")
                
        except Exception as e:
            continue
    
    elapsed = time.time() - start_time
    
    states_array = np.array(all_states, dtype=np.float32)
    actions_array = np.array(all_actions, dtype=np.float32)
    
    print(f"\n✅ Data generation complete!")
    print(f"   Successful engagements: {successful}/{num_engagements}")
    print(f"   Total training samples: {len(all_states)}")
    print(f"   State shape: {states_array.shape}")
    print(f"   Action shape: {actions_array.shape}")
    print(f"   Time: {elapsed:.1f}s")
    
    return states_array, actions_array


def save_dataset(states, actions, output_dir=None):
    """Save training dataset to .npz file."""
    if output_dir is None:
        output_dir = os.path.dirname(__file__)
    
    filepath = os.path.join(output_dir, 'training_dataset.npz')
    np.savez_compressed(filepath, states=states, actions=actions)
    
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"   Saved to: {filepath} ({size_mb:.1f} MB)")
    
    return filepath


if __name__ == "__main__":
    states, actions = generate_state_action_pairs(num_engagements=400)
    save_dataset(states, actions)
