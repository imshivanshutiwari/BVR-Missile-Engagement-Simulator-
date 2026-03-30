from physics.engagement.engagement_engine import EngagementEngine
import math

e = EngagementEngine()
r = e.run(scenario='head_on', guidance_law='png', launch_range_m=20000, launch_altitude_m=8000, target_speed_ms=250, target_altitude_m=8000, target_evasion=True)

def check_nan(traj):
    for k, v in traj.items():
        for i, val in enumerate(v):
            if isinstance(val, (int, float)):
                if math.isnan(val) or math.isinf(val):
                    print(f"NaN/Inf found in {k} at index {i}. Value: {val}")
                    return True
            elif val is None:
                print(f"None found in {k} at index {i}")
                return True
    return False

print("Check:")
if not check_nan(r['trajectory']) and not check_nan(r['target_trajectory']):
    print("No NaNs or Infs found! Data is totally clean!")

