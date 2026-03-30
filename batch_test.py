import sys
import os
import random
import time
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from physics.engagement.engagement_engine import EngagementEngine

def run_batch_test(num_tests=200):
    engine = EngagementEngine()
    
    print(f"==================================================")
    print(f"🚀 STRIKE-VECTOR BATCH EVALUATION MODEL")
    print(f"==================================================")
    print(f"Running {num_tests} random engagements...\n")
    
    results = {
        'total': num_tests,
        'hits': 0,
        'misses': 0,
        'avg_miss_distance': 0.0,
        'avg_pk': 0.0,
        'scenarios': {'head_on': 0, 'tail_chase': 0, 'crossing': 0},
        'laws': {'png': 0, 'apng': 0}
    }
    
    total_miss_dist = 0.0
    total_pk = 0.0
    start_time = time.time()
    
    scenarios = ["tail_chase"]
    laws = ["png"]
    
    for i in range(num_tests):
        scenario = random.choice(scenarios)
        law = random.choice(laws)
        
        # Randomize launch parameters slightly
        launch_range = random.uniform(15000, 25000)
        launch_alt = random.uniform(5000, 10000)
        target_speed = random.uniform(200, 300)
        target_alt = random.uniform(5000, 10000)
        evasion = random.choice([True, False])
        
        try:
            data = engine.run(
                scenario=scenario,
                guidance_law=law,
                launch_range_m=launch_range,
                launch_altitude_m=launch_alt,
                target_speed_ms=target_speed,
                target_altitude_m=target_alt,
                target_evasion=evasion
            )
            
            miss_dist = data['miss_distance_m']
            pk = data['pk']
            intercept = data['intercept_achieved']
            
            total_miss_dist += miss_dist
            total_pk += pk
            
            if intercept:
                results['hits'] += 1
            else:
                results['misses'] += 1
                
            results['scenarios'][scenario] += 1
            results['laws'][law] += 1
            
            if (i+1) % 20 == 0:
                print(f"Progress: {i+1}/{num_tests} | Hits: {results['hits']} | Avg Miss: {total_miss_dist/(i+1):.1f}m")
                
        except Exception as e:
            print(f"Test {i+1} failed with exception: {str(e)}")
            results['misses'] += 1
    
    elapsed = time.time() - start_time
    
    results['avg_miss_distance'] = total_miss_dist / num_tests
    results['avg_pk'] = total_pk / num_tests
    
    print(f"\n==================================================")
    print(f"📊 BATCH TEST RESULTS")
    print(f"==================================================")
    print(f"Time Taken: {elapsed:.2f}s")
    print(f"Total Tests: {num_tests}")
    print(f"Intercepts: {results['hits']} ({(results['hits']/num_tests)*100:.1f}%)")
    print(f"Misses: {results['misses']} ({(results['misses']/num_tests)*100:.1f}%)")
    print(f"Average Pk: {results['avg_pk']*100:.1f}%")
    print(f"Average Miss Distance: {results['avg_miss_distance']:.1f}m")
    print(f"==================================================")
    
if __name__ == "__main__":
    # Test just 10 first to see if script runs properly without crashing, 
    # then if OK, I'll run full 200.
    run_batch_test(200)
