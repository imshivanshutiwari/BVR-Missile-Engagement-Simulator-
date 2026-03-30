"""Guidance Law Selector — runtime selection between PNG, APNG, and AI Model."""

from physics.guidance.png_law import ProportionalNavigation
from physics.guidance.apng_law import AugmentedProportionalNavigation


def select_guidance(law_name: str = "png", N: float = 4.0):
    """Select guidance law by name.

    Args:
        law_name: "png", "apng", or "ai_model"
        N: navigation constant (default 4.0)

    Returns:
        Guidance law instance.
    """
    law_name = law_name.lower().strip()
    if law_name == "apng":
        return AugmentedProportionalNavigation(N=N)
    elif law_name == "ai_model":
        from physics.guidance.ai_law import AIGuidance
        return AIGuidance()
    else:
        return ProportionalNavigation(N=N)
