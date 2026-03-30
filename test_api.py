import time
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from physics.engagement.engagement_engine import EngagementEngine

engine = EngagementEngine()
data = engine.run(
    scenario="head_on",
    guidance_law="apng",
    launch_range_m=20000,
    launch_altitude_m=8000,
    target_speed_ms=250,
    target_altitude_m=8000,
    target_evasion=True
)
print(f"Trajectory points: {len(data['trajectory']['x'])}")
print(f"Intercept: {data['intercept_achieved']}")
print(f"Miss distance: {data['miss_distance_m']:.2f}m")
print(f"Pk: {data['pk']*100:.1f}%")
print(f"ToF: {data['time_of_flight_s']:.2f}s")
if data['intercept_point']:
    print(f"Intercept Point: X={data['intercept_point']['x']:.1f}, Y={data['intercept_point']['y']:.1f}, Z={data['intercept_point']['z']:.1f}")
t_end_z = data['target_trajectory']['z'][-1]
t_end_x = data['target_trajectory']['x'][-1]
t_end_y = data['target_trajectory']['y'][-1]
print(f"Target End: X={t_end_x:.1f}, Y={t_end_y:.1f}, Z={t_end_z:.1f}")
