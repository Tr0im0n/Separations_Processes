



def intersect(a1, b1, a2, b2):
    x = (b2-b1)/(a1-a2)
    y = a1 * x + b1
    return x, y


def closest_point_on_line(a1, b1, x, y):
    a2 = -1/a1
    b2 = y - a2 * x
    return intersect(a1, b1, a2, b2)


def through_points(x1, y1, x2, y2):
    """Returns None, if slope is Inf"""
    if x1 == x2:
        return None
    a = y2 - y1 / (x2 - x1)
    b = y1 - a * x1
    return a, b


def get_y(x, a, b):
    return a * x + b


