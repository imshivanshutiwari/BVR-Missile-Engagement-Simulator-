"""Scenario Runner — Batch execution of all engagement scenarios."""

from physics.scenarios.head_on import HeadOnScenario
from physics.scenarios.tail_chase import TailChaseScenario
from physics.scenarios.crossing import CrossingScenario
from physics.engagement.engagement_engine import EngagementEngine


SCENARIOS = {
    'head_on': HeadOnScenario,
    'tail_chase': TailChaseScenario,
    'crossing': CrossingScenario
}


class ScenarioRunner:
    """Batch scenario executor."""

    def __init__(self):
        self.engine = EngagementEngine()

    def get_all_scenarios(self) -> list:
        """Return all scenario definitions."""
        return [s.to_dict() for s in SCENARIOS.values()]

    def get_scenario(self, scenario_id: str) -> dict:
        """Get a single scenario definition."""
        scenario_cls = SCENARIOS.get(scenario_id)
        if scenario_cls is None:
            raise ValueError(f"Unknown scenario: {scenario_id}")
        return scenario_cls.to_dict()

    def run_scenario(self, scenario_id: str,
                     override_params: dict = None) -> dict:
        """Run a single scenario with optional parameter overrides."""
        scenario = self.get_scenario(scenario_id)
        params = scenario['default_params'].copy()
        if override_params:
            params.update(override_params)

        result = self.engine.run(
            scenario=scenario_id,
            launch_range_m=params['launch_range_m'],
            launch_altitude_m=params['launch_altitude_m'],
            target_speed_ms=params['target_speed_ms'],
            target_altitude_m=params['target_altitude_m'],
            guidance_law=params['guidance_law'],
            target_evasion=params.get('target_evasion', True)
        )

        result['scenario_info'] = scenario
        return result

    def run_all(self, override_params: dict = None) -> list:
        """Run all scenarios and return results."""
        results = []
        for sid in SCENARIOS:
            result = self.run_scenario(sid, override_params)
            results.append(result)
        return results

    def compare_guidance_laws(self, scenario_id: str = "head_on") -> dict:
        """Compare PNG vs APNG for a given scenario."""
        result_png = self.run_scenario(scenario_id, {'guidance_law': 'png'})
        result_apng = self.run_scenario(scenario_id, {'guidance_law': 'apng'})

        return {
            'scenario': scenario_id,
            'png': {
                'miss_distance_m': result_png['miss_distance_m'],
                'pk': result_png['pk'],
                'tof': result_png['time_of_flight_s'],
                'intercept': result_png['intercept_achieved']
            },
            'apng': {
                'miss_distance_m': result_apng['miss_distance_m'],
                'pk': result_apng['pk'],
                'tof': result_apng['time_of_flight_s'],
                'intercept': result_apng['intercept_achieved']
            }
        }
