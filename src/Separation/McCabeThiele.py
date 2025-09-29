
from matplotlib import pyplot as plt
import numpy as np


def equilibrium_curve(x, alpha):
    return alpha*x / ((alpha-1)*x + 1)


def equilibrium_curve_inverse(y, alpha):
    return y / (alpha - y*(alpha-1))


alpha1 = 2.4
x1 = np.arange(0, 1.01, 0.01)
y1 = equilibrium_curve(x1, alpha1)

fig, ax = plt.subplots(figsize=(8, 6), dpi=120)

ax.set_xlim(0., 1.)
ax.set_ylim(0., 1.)

background = None
line, = ax.plot([0, 0], [0, 0], 'r-')


def draw_background():
    ax.cla()

    ax.plot([0, 1], [0, 1])
    ax.plot(x1, y1)

    global background
    background = fig.canvas.copy_from_bbox(ax.bbox)
    ax.draw_artist(line)


def on_reshape(event):
    # draw_background()
    global background
    background = fig.canvas.copy_from_bbox(ax.bbox)


def on_mouse_move(event):
    if not event.inaxes:
        return 0

    if background is None:
        return 1

    fig.canvas.restore_region(background)

    x, y = event.xdata, event.ydata
    line.set_data([0, x], [0, y])
    ax.draw_artist(line)

    fig.canvas.blit(ax.bbox)   # ax or fig
    return 2


draw_background()

cid1 = fig.canvas.mpl_connect('draw_event', on_reshape)
cid2 = fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)   # 'button_press_event'



plt.show()


