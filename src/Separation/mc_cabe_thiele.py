
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.widgets import Slider


# Math tools
def intersect(a1, b1, a2, b2):
    x = (b2-b1)/(a1-a2)
    y = a1 * x + b1
    return x, y


def closest_point_on_line(a1, b1, x, y):
    a2 = -1/a1
    b2 = y - a2 * x
    return intersect(a1, b1, a2, b2)


# variables
xf = 0.68
xd = 0.93
xb = 0.04
alpha = 1.85
r = 3
b = 10

max_eq_array_size = 127
n_eq_points = 0
eq_points = np.zeros((2 * max_eq_array_size, 1), dtype=float)
rectifying_coef = (0, 0)
stripping_coef = (0, 0)
q_point = (0, 0)

xs = np.arange(0, 1, 0.01, dtype=float)

# Make lines
def make_equilibrium_curve(x):
    return alpha * x / ((alpha - 1) * x + 1)


def make_equilibrium_curve_inverse(y):
    return y / (alpha - y * (alpha - 1))


def make_equilibrium_points():
    global n_eq_points
    eq_points[:3] = xb
    n = 3

    while eq_points[n - 1] < xd and n < 2 * max_eq_array_size - 5:
        y_eq = make_equilibrium_curve(eq_points[n - 1])
        eq_points[n] = y_eq

        strip = (y_eq - stripping_coef[1]) / stripping_coef[0]
        rect = (y_eq - rectifying_coef[1]) / rectifying_coef[0]

        eq_points[n + 1] = max(strip, rect)
        eq_points[n + 2] = y_eq
        eq_points[n + 3] = eq_points[n + 1]
        n += 4
        n_eq_points += 1

    eq_points.shape = (max_eq_array_size, 2)


def make_all_lines():
    rectifying_line = r / (r + 1), xd / (r + 1)
    stripping_line = (b + 1) / b, -xb / b

    q_point = intersect(*rectifying_line, *stripping_line)

    n_eq_points = make_equilibrium_points(
        xb, xd, alpha, rectifying_line, stripping_line, eq_points, max_eq_array_size
    )

    eq_curve = make_equilibrium_curve(xs, alpha)

    return rectifying_line, stripping_line, q_point, n_eq_points, eq_curve





