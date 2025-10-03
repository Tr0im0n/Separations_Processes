
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

from tools import lines


class McCabeThiele:
    def __init__(self, xf=0.68, xd=0.93, xb=0.04, alpha=1.85, r=3, b=10, *,max_eq_array_size=127) :
        self.xf = xf
        self.xd = xd
        self.xb = xb
        self.alpha = alpha
        self.r = r
        self.b = b

        self.max_eq_array_size = max_eq_array_size
        self.n_eq_points = 0
        self.eq_points = np.zeros((2*self.max_eq_array_size, 1), dtype=float)

        self.rectifying_line = 0, 0
        self.stripping_line = 0, 0
        self.q_point = 0, 0

        self.xs = np.arange(0, 1, 0.01, dtype=float)
        self.eq_curve = np.zeros_like(self.xs)

        self.diag_artist = None
        self.eqc_artist = None
        self.rect_artist = None
        self.strip_artist = None
        self.q_artist = None
        self.eqp_artist = None

        self.feed_text = None
        self.bottoms_text = None
        self.distillate_text = None


    def make_all_lines(self):
        self.rectifying_line = self.r/(self.r+1), self.xd/(self.r+1)
        self.stripping_line = (self.b+1)/self.b, -self.xb/self.b
        self.q_point = lines.intersect(*self.rectifying_line, *self.stripping_line)

        self.make_equilibrium_points()

        self.eq_curve = self.make_equilibrium_curve(self.xs)

    def make_equilibrium_curve(self, x):
        return self.alpha*x / ((self.alpha-1)*x + 1)

    def make_equilibrium_curve_inverse(self, y):
        return y / (self.alpha - y*(self.alpha-1))

    def make_equilibrium_points(self):
        self.n_eq_points = 0
        eqs = self.eq_points
        eqs[:3] = self.xb
        n = 3

        while eqs[n-1] < self.xd and n < 2*self.max_eq_array_size-5:
            new = self.make_equilibrium_curve(eqs[n-1])

            strip = (new - self.stripping_line[1]) / self.stripping_line[0]
            rect = (new - self.rectifying_line[1]) / self.rectifying_line[0]

            eqs[n] = new
            eqs[n+1] = max(strip, rect)
            eqs[n+2] = eqs[n]
            eqs[n+3] = eqs[n+1]
            n += 4
            self.n_eq_points += 1

        self.eq_points.shape = (self.max_eq_array_size, 2)

    # def make_artists(self):


    def draw_background(self, fig, ax):
        ax.cla()

        ax.plot([0, 1], [0, 1])
        ax.plot(self.xs, self.eq_curve)
        ax.plot([self.xb, self.q_point[0]], [self.xb, self.q_point[1]])
        ax.plot([self.q_point[0], self.xd], [self.q_point[1], self.xd])
        ax.plot([self.xf, self.q_point[0]], [self.xf, self.q_point[1]])

        ax.plot(self.eq_points[:self.n_eq_points*2+1, 0], self.eq_points[:self.n_eq_points*2+1, 1])

        ax.text(self.xf, self.xf, "Feed", ha='left', va='top', fontsize=12)
        ax.text(self.xb, self.xb, "Bottom", ha='left', va='top', fontsize=12)
        ax.text(self.xd, self.xd, "Distillate", ha='left', va='top', fontsize=12)
        # ax.text(*self.q_point, "Q point", ha='left', va='top', fontsize=16)
        # self.background = fig.canvas.copy_from_bbox(ax.bbox)

    def just_background(self):
        fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
        plt.subplots_adjust(left=0.3)

        ax.set_xlim(0., 1.)
        ax.set_ylim(0., 1.)

        self.draw_background(fig, ax)

        plt.show()

    def init_artists(self, ax):
        self.diag_artist = ax.plot([0, 1], [0, 1])
        self.eqc_artist, = ax.plot(self.xs, self.eq_curve)
        self.rect_artist, = ax.plot([self.xb, self.q_point[0]], [self.xb, self.q_point[1]])
        self.strip_artist, = ax.plot([self.q_point[0], self.xd], [self.q_point[1], self.xd])
        self.q_artist, = ax.plot([self.xf, self.q_point[0]], [self.xf, self.q_point[1]])
        self.eqp_artist, = ax.plot(self.eq_points[:self.n_eq_points*2+1, 0], self.eq_points[:self.n_eq_points*2+1, 1])

        self.feed_text = ax.text(self.xf, self.xf, "Feed", ha='left', va='top', fontsize=12)
        self.bottoms_text = ax.text(self.xb, self.xb, "Bottom", ha='left', va='top', fontsize=12)
        self.distillate_text = ax.text(self.xd, self.xd, "Distillate", ha='left', va='top', fontsize=12)

    def update_artists(self):
        self.eqc_artist.set_ydata(self.eq_curve)
        self.rect_artist.set_data([self.q_point[0], self.xd], [self.q_point[1], self.xd])
        self.strip_artist.set_data([self.xb, self.q_point[0]], [self.xb, self.q_point[1]])
        self.q_artist.set_data([self.xf, self.q_point[0]], [self.xf, self.q_point[1]])
        self.eqp_artist.set_data(self.eq_points[:self.n_eq_points * 2 + 1, 0],
                                 self.eq_points[:self.n_eq_points * 2 + 1, 1])
        self.feed_text.set_position(self.xf, self.xf)
        self.bottoms_text.set_position(self.xb, self.xb)
        self.distillate_text.set_position(self.xd, self.xd)


    def with_sliders(self):
        fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
        plt.subplots_adjust(left=0.3)

        ax.set_xlim(0., 1.)
        ax.set_ylim(0., 1.)
        ax.grid(True)

        self.init_artists(ax)

        axes = [plt.axes((0.01, 0.9 - 0.1*i, 0.25, 0.1)) for i in range(6)]
        slider_xb = Slider(axes[0], 'xb', 0.0, 1.0, valinit=self.xb, valstep=0.01)
        slider_xf = Slider(axes[1], 'xf', 0.0, 1.0, valinit=self.xf, valstep=0.01)
        slider_xd = Slider(axes[2], 'xd', 0.0, 1.0, valinit=self.xd, valstep=0.01)
        slider_alpha = Slider(axes[3], 'alpha', 0.0, 10.0, valinit=self.xd, valstep=0.1)
        slider_r = Slider(axes[4], 'R', 0.0, 10.0, valinit=self.r, valstep=0.1)
        slider_b = Slider(axes[5], 'B', 0.0, 10.0, valinit=self.b, valstep=0.1)

        def update(val):
            xb_val = slider_xb.val
            xf_val = slider_xf.val
            xd_val = slider_xd.val
            alpha_val = slider_alpha.val
            r_val = slider_r.val
            b_val = slider_b.val

            self.xb = xb_val
            self.xf = xf_val
            self.xd = xd_val
            self.alpha = alpha_val
            self.r = r_val
            self.b = b_val

            self.make_all_lines()
            self.update_artists()





def main():
    mct1 = McCabeThiele()
    # mct1.build_figure()
    mct1.just_background()


if __name__ == "__main__":
    main()


"""


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


"""
