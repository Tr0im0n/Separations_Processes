
from matplotlib import pyplot as plt
import numpy as np

from tools import lines


class McCabeThiele:
    def __init__(self, xf=0.68, xd=0.93, xb=0.04, alpha=1.85, r=3, b=10):
        self.xf = xf
        self.xd = xd
        self.xb = xb

        self.alpha = alpha
        self.r = r
        self.b = b

        self.rectifying_line = r/(r+1), xd/(r+1)
        self.stripping_line = (b+1)/b, -xb/b
        self.q_point = lines.intersect(*self.rectifying_line, *self.stripping_line)

        self.xs = np.arange(0, 1.01, 0.01)
        self.eq_curve = self.make_equilibrium_curve(self.xs)

        self.background = None

    def make_equilibrium_curve(self, x):
        return self.alpha*x / ((self.alpha-1)*x + 1)

    def make_equilibrium_curve_inverse(self, y):
        return y / (self.alpha - y*(self.alpha-1))

    def build_figure(self):
        fig, ax = plt.subplots(figsize=(8, 6), dpi=120)

        ax.set_xlim(0., 1.)
        ax.set_ylim(0., 1.)

        line, = ax.plot([0, 0], [0, 0], 'r-')

        self.draw_background(fig, ax)

        ax.draw_artist(line)

        def on_reshape(event):
            self.background = fig.canvas.copy_from_bbox(ax.bbox)

        def on_mouse_move(event):
            if (not event.inaxes) or self.background is None:
                return 0

            fig.canvas.restore_region(self.background)

            line.set_data([0, event.xdata], [0, event.ydata])
            ax.draw_artist(line)

            fig.canvas.blit(ax.bbox)  # ax or fig
            return 1

        cid1 = fig.canvas.mpl_connect('draw_event', on_reshape)
        cid2 = fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)

        plt.show()

    def draw_background(self, fig, ax):
        ax.cla()

        ax.plot([0, 1], [0, 1])
        ax.plot(self.xs, self.eq_curve)
        ax.plot([self.xb, self.q_point[0]], [self.xb, self.q_point[1]])
        ax.plot([self.q_point[0], self.xd], [self.q_point[1], self.xd])
        ax.plot([self.xf, self.q_point[0]], [self.xf, self.q_point[1]])

        ax.text(self.xf, self.xf, "Feed", ha='left', va='top', fontsize=12)
        ax.text(self.xb, self.xb, "Bottom", ha='left', va='top', fontsize=12)
        ax.text(self.xd, self.xd, "Distillate", ha='left', va='top', fontsize=12)
        # ax.text(*self.q_point, "Q point", ha='left', va='top', fontsize=16)

        self.background = fig.canvas.copy_from_bbox(ax.bbox)




mct1 = McCabeThiele()
mct1.build_figure()


