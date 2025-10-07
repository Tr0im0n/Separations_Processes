
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button

from tools import lines
from tools.CustomSlider import CustomSlider
from tools.chemistry import vapor_liquid_equilibrium


class McCabeThiele:
    DEFAULT_XF = 0.68
    DEFAULT_XD = 0.93
    DEFAULT_XB = 0.04
    DEFAULT_ALPHA = 1.85
    DEFAULT_R = 3.0
    DEFAULT_B = 10.0
    DEFAULT_Q = 1.0
    N_OF_SLIDERS = 7
    DEFAULT_MAX_EQ_ARRAY_SIZE = 127

    DEPENDENT_VARS = ['R', 'B', 'q', 'xf', 'xd', 'xb']
    DEFAULT_DEPENDENT_VAR = 'q'

    def __init__(self, xf=None, xd=None, xb=None, alpha=None, r=None, b=None, q=None, *, max_eq_array_size=None):
        # Use default if no value is passed
        self.xf = xf if xf is not None else self.DEFAULT_XF
        self.xd = xd if xd is not None else self.DEFAULT_XD
        self.xb = xb if xb is not None else self.DEFAULT_XB
        self.alpha = alpha if alpha is not None else self.DEFAULT_ALPHA
        self.r = r if r is not None else self.DEFAULT_R
        self.b = b if b is not None else self.DEFAULT_B
        self.q = q if q is not None else self.DEFAULT_Q

        self._dependent_variable = self.DEFAULT_DEPENDENT_VAR

        self.max_eq_array_size = max_eq_array_size if max_eq_array_size is not None else self.DEFAULT_MAX_EQ_ARRAY_SIZE
        self.n_eq_points = 0
        self.eq_points = np.zeros((2*self.max_eq_array_size, 1), dtype=float)

        self.rectifying_line = 0.0, 0.0
        self.stripping_line = 0.0, 0.0
        self.q_line = 0.0, 0.0
        self.q_point = 0.0, 0.0

        self.xs = np.arange(0, 1, 0.01, dtype=float)
        self.eq_curve = np.zeros_like(self.xs)

        self.ax = None

        self.diag_artist = None
        self.eqc_artist = None
        self.rect_artist = None
        self.strip_artist = None
        self.q_artist = None
        self.eqp_artist = None

        self.feed_text = None
        self.bottoms_text = None
        self.distillate_text = None

        self.sliders = None
        self.reset_button = None

    @property
    def dependent_variable(self):
        return self._dependent_variable

    @dependent_variable.setter
    def dependent_variable(self, new_value):
        if new_value not in self.DEPENDENT_VARS:
            raise ValueError(f"Invalid dependent variable '{new_value}'. ")
        self._dependent_variable = new_value

    def calculate_q(self):
        a, _ = lines.line_from_points(*self.q_point, self.xf, self.xf)
        return a/(a - 1)

    def make_all_lines(self):
        self.rectifying_line = self.r/(self.r+1), self.xd/(self.r+1)
        self.stripping_line = (self.b+1)/self.b, -self.xb/self.b
        # self.q_line = self.q/(self.q-1), -self.xf/(self.q-1)
        self.q_point = lines.intersect(*self.rectifying_line, *self.stripping_line)
        self.eq_curve = vapor_liquid_equilibrium(self.xs, self.alpha)

        self.make_equilibrium_points()

    def make_equilibrium_points(self):
        self.n_eq_points = 0
        self.eq_points = np.zeros((2*self.max_eq_array_size, 1), dtype=float)
        eqs = self.eq_points
        eqs[:3] = self.xb
        n = 3

        while eqs[n-1] < self.xd and n < 2*self.max_eq_array_size-5:
            new = vapor_liquid_equilibrium(eqs[n-1], self.alpha)

            strip = (new - self.stripping_line[1]) / self.stripping_line[0]
            rect = (new - self.rectifying_line[1]) / self.rectifying_line[0]

            eqs[n] = new
            eqs[n+1] = max(strip, rect)
            eqs[n+2] = eqs[n]
            eqs[n+3] = eqs[n+1]
            n += 4
            self.n_eq_points += 1

        self.eq_points.shape = (self.max_eq_array_size, 2)

    def init_artists(self, ax):
        self.diag_artist, = ax.plot([0, 1], [0, 1])
        self.eqc_artist, = ax.plot(self.xs, self.eq_curve)
        self.rect_artist, = ax.plot([self.xb, self.q_point[0]], [self.xb, self.q_point[1]])
        self.strip_artist, = ax.plot([self.xd, self.q_point[0]], [self.xd, self.q_point[1]])
        self.q_artist, = ax.plot([self.xf, self.q_point[0]], [self.xf, self.q_point[1]])
        self.eqp_artist, = ax.plot(self.eq_points[:self.n_eq_points*2+1, 0],
                                   self.eq_points[:self.n_eq_points*2+1, 1])
        self.feed_text = ax.text(self.xf, self.xf, "Feed", ha='left', va='top', fontsize=12)
        self.bottoms_text = ax.text(self.xb, self.xb, "Bottom", ha='left', va='top', fontsize=12)
        self.distillate_text = ax.text(self.xd, self.xd, "Distillate", ha='left', va='top', fontsize=12)

    def update_artists(self):
        self.eqc_artist.set_ydata(self.eq_curve)
        self.rect_artist.set_data([self.xb, self.q_point[0]], [self.xb, self.q_point[1]])
        self.strip_artist.set_data([self.xd, self.q_point[0]], [self.xd, self.q_point[1]])
        self.q_artist.set_data([self.xf, self.q_point[0]], [self.xf, self.q_point[1]])
        self.eqp_artist.set_data(self.eq_points[:self.n_eq_points * 2 + 1, 0],
                                 self.eq_points[:self.n_eq_points * 2 + 1, 1])
        self.feed_text.set_position((self.xf, self.xf))
        self.bottoms_text.set_position((self.xb, self.xb))
        self.distillate_text.set_position((self.xd, self.xd))

    def with_sliders(self):
        fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
        plt.subplots_adjust(left=0.4)

        ax.set_xlim(0., 1.)
        ax.set_ylim(0., 1.)
        ax.grid(True)

        self.make_all_lines()
        self.init_artists(ax)
        ax.set_title(f"Number of equilibrium stages: {self.n_eq_points}")
        self.ax = ax

        axes = [plt.axes((0.05, 0.8 - 0.1*i, 0.3, 0.05)) for i in range(self.N_OF_SLIDERS)]
        slider_xb = CustomSlider(axes[0], 'xb', 0.01, 1.0, valinit=self.xb, valstep=0.01)
        slider_xf = CustomSlider(axes[1], 'xf', 0.01, 1.0, valinit=self.xf, valstep=0.01)
        slider_xd = CustomSlider(axes[2], 'xd', 0.01, 1.0, valinit=self.xd, valstep=0.01)
        slider_alpha = CustomSlider(axes[3], 'alpha', 0.1, 10.0, valinit=self.alpha, valstep=0.01)
        slider_r = CustomSlider(axes[4], 'R', 0.1, 10.0, valinit=self.r, valstep=0.1)
        slider_b = CustomSlider(axes[5], 'B', 0.1, 20.0, valinit=self.b, valstep=0.1)
        slider_q = CustomSlider(axes[6], 'q', -1.0, 2.0, valinit=self.q, valstep=0.01)

        self.sliders = [slider_xb, slider_xf, slider_xd, slider_alpha, slider_r, slider_b, slider_q]

        # print(*dir(slider_q.canvas), sep="\n")
        # quit()
        slider_q.disable()
        # slider_q.disable()
        # slider_q.enable()

        reset_ax = plt.axes((0.02, 0.05, 0.15, 0.05))
        self.reset_button = Button(reset_ax, 'Reset', color='lightsalmon', hovercolor='tomato')
        self.reset_button.on_clicked(self.reset_sliders)

        for i in self.sliders:
            i.on_changed(self.update)

        plt.show()

    def update(self, val):
        self.xb = self.sliders[0].val
        self.xf = self.sliders[1].val
        self.xd = self.sliders[2].val
        self.alpha = self.sliders[3].val
        self.r = self.sliders[4].val
        self.b = self.sliders[5].val
        self.q = self.sliders[6].val

        if self.xb >= self.xf:
            self.xf = self.xb + 0.01
        if self.xf >= self.xd:
            self.xd = self.xf + 0.01

        self.make_all_lines()
        self.update_artists()
        self.ax.set_title(f"Number of equilibrium stages: {self.n_eq_points}")

    def reset_sliders(self, event):
        for slider in self.sliders:
            slider.reset()


def main():
    mct1 = McCabeThiele()
    mct1.with_sliders()


if __name__ == "__main__":
    main()


"""

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

"""
