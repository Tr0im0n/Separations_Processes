import numpy as np


def vapor_liquid_equilibrium(x: float | np.ndarray, alpha: float):
    """Vapor Liquid Equilibrium Curve"""
    return alpha * x / ((alpha - 1) * x + 1)


def vapor_liquid_equilibrium_inverse(y: float | np.ndarray, alpha: float):
    return y / (alpha - y * (alpha - 1))
