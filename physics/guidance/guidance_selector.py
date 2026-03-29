"""Guidance Law Selector — runtime selection between PNG and APNG."""

from physics.guidance.png_law import ProportionalNavigation
from physics.guidance.apng_law import AugmentedProportionalNavigation


def select_guidance(law_name: str = "png", N: float = 4.0):
    """Select guidance law by name.

    Args:
        law_name: "png" or "apng"
        N: navigation constant (default 4.0)

    Returns:
        Guidance law instance.
    """
    law_name = law_name.lower().strip()
    if law_name == "apng":
        return AugmentedProportionalNavigation(N=N)
    else:
        return ProportionalNavigation(N=N)
