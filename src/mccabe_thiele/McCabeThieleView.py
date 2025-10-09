
from matplotlib import pyplot as plt
from matplotlib.widgets import Button, RadioButtons

from src.mccabe_thiele.McCabeThieleLogic import McCabeThieleLogic
from tools.CustomSlider import CustomSlider


class McCabeThiele:
    N_OF_SLIDERS = 7

    def __init__(self):
        self.logic = McCabeThieleLogic()

        self.ax = None
        self.artists = None
        self.sliders = None
        self.reset_button = None
        self.radio_buttons = None

    @property
    def dependent_variable(self):
        return self.logic.dependent_variable

    @dependent_variable.setter
    def dependent_variable(self, new_value):
        if new_value not in self.logic.DEPENDENT_VARS:
            raise ValueError(f"Invalid dependent variable '{new_value}'. ")
        self.sliders[self.dependent_variable].enable()
        self.logic._dependent_variable = new_value
        self.sliders[self.dependent_variable].disable()


    def init_artists(self):
        # Getting values from the logic class.
        xb = self.logic.variables['xb']
        xf = self.logic.variables['xf']
        xd = self.logic.variables['xd']
        q_point = self.logic.q_point
        eq_points = self.logic.eq_points
        n_eq_points = self.logic.n_eq_points
        xs = self.logic.xs
        vle_curve = self.logic.vle_curve

        ax = self.ax
        self.artists = {
            # Line Artists: [0] is used to unpack the single PlotLine object from ax.plot()
            'diagonal': ax.plot([0, 1], [0, 1])[0],
            'rect': ax.plot([xb, q_point[0]], [xb, q_point[1]])[0],
            'strip': ax.plot([xd, q_point[0]], [xd, q_point[1]])[0],
            'q_line': ax.plot([xf, q_point[0]], [xf, q_point[1]])[0],
            'vle': ax.plot(xs, vle_curve)[0],
            'eq_points': ax.plot(eq_points[:n_eq_points * 2 + 1, 0], eq_points[:n_eq_points * 2 + 1, 1])[0],
            # Text Artists
            'feed_text': ax.text(xf, xf, "Feed", ha='left', va='top', fontsize=12),
            'bottoms_text': ax.text(xb, xb, "Bottom", ha='left', va='top', fontsize=12),
            'distillate_text': ax.text(xd, xd, "Distillate", ha='left', va='top', fontsize=12)
        }

    def update_artists(self):
        # Getting values from the logic class.
        xb = self.logic.variables['xb']
        xf = self.logic.variables['xf']
        xd = self.logic.variables['xd']
        q_point = self.logic.q_point
        eq_points = self.logic.eq_points
        n_eq_points = self.logic.n_eq_points
        vle_curve = self.logic.vle_curve

        # Update Operating Lines
        self.artists['rect'].set_data([xb, q_point[0]], [xb, q_point[1]])
        self.artists['strip'].set_data([xd, q_point[0]], [xd, q_point[1]])
        self.artists['q_line'].set_data([xf, q_point[0]], [xf, q_point[1]])
        # Update VLE curve
        self.artists['vle'].set_ydata(vle_curve)
        # Update Equilibrium Steps
        self.artists['eq_points'].set_data(eq_points[:n_eq_points * 2 + 1, 0], eq_points[:n_eq_points * 2 + 1, 1])
        # Update Text Positions
        self.artists['feed_text'].set_position((xf, xf))
        self.artists['bottoms_text'].set_position((xb, xb))
        self.artists['distillate_text'].set_position((xd, xd))

    def init_sliders(self):
        axes = [plt.axes((0.05, 0.8 - 0.1 * i, 0.3, 0.05)) for i in range(self.N_OF_SLIDERS)]
        variables = ['xb', 'xf', 'xd', 'alpha', 'R', 'B', 'q']
        values = self.logic.variables
        maximums = [1.0, 1.0, 1.0, 10.0, 10.0, 20.0, 2.0]

        self.sliders = {variable: CustomSlider(
            ax, variable, 0.01, valmax, values[variable], valstep=0.01)
            for ax, variable, valmax in zip(axes, variables, maximums)}

        for slider in self.sliders.values():
            slider.on_changed(self.update_all)

    def init_button(self):
        reset_ax = plt.axes((0.1, 0.05, 0.15, 0.05))
        self.reset_button = Button(reset_ax, 'Reset', color='lightsalmon', hovercolor='tomato')
        self.reset_button.on_clicked(self.reset_sliders)

    def on_radio_button_press(self, label):
        weird_dict = {' ': 'R', '  ': 'B', '   ': 'q'}
        new_dependent_variable = weird_dict[label]
        self.dependent_variable = new_dependent_variable
        print(new_dependent_variable)
        self.ax.figure.canvas.draw()

    def init_radio_button(self):
        radio_ax = plt.axes((0.04, 0.16, 0.05, 0.4))
        radio_ax.set_axis_off()
        labels = (' R', ' B', ' q')
        no_labels = (' ', '  ', '   ')
        radio_props = {'s': [64, 64, 64]}
        self.radio_buttons = RadioButtons(radio_ax, no_labels, active=2, radio_props=radio_props)
        self.radio_buttons.on_clicked(self.on_radio_button_press)

    def construct_figure(self):
        fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
        fig.suptitle(f"Interactive McCabe Thiele Graph")
        plt.subplots_adjust(left=0.4)

        ax.set_xlim(0., 1.)
        ax.set_ylim(0., 1.)
        ax.grid(True)
        self.ax = ax

    def update_old(self, val):
        for key in self.variables:
            self.variables[key] = self.all_sliders[key].val

        if self.variables['xb'] >= self.variables['xf']:
            self.variables['xf'] = self.variables['xb'] + 0.01
        if self.variables['xf'] >= self.variables['xd']:
            self.variables['xd'] = self.variables['xf'] + 0.01

        self.make_all_lines()
        self.update_artists()
        dv = self.dependent_variable
        self.all_sliders[dv].set_val(self.q)
        self.all_sliders[dv].set_val_text(self.q)
        self.ax.set_title(f"Number of equilibrium stages: {self.logic.n_eq_points}")

    def update_all(self, val):
        for key, slider in self.sliders.items():
            if key in self.logic.variables:
                self.logic.variables[key] = slider.val
            else:
                raise ValueError("Slider has name that is not in variables. ")

        xb = self.logic.variables['xb']
        xf = self.logic.variables['xf']
        xd = self.logic.variables['xd']

        if xb >= xf:
            self.logic.variables['xf'] = xb + 0.01
        if xf >= xd:
            self.logic.variables['xd'] = xf + 0.01

        self.logic.make_all_lines()
        self.update_artists()

        dv = self.dependent_variable
        self.sliders[dv].set_val(self.logic.variables[dv])
        self.sliders[dv].set_val_text(self.logic.variables[dv])
        self.ax.set_title(f"Number of equilibrium stages: {self.logic.n_eq_points}")


    def reset_sliders(self, event):
        for slider in self.sliders.values():
            slider.reset()

    def main(self):
        self.construct_figure()

        self.logic.make_all_lines()
        self.ax.set_title(f"Number of equilibrium stages: {self.logic.n_eq_points}")
        self.init_artists()
        self.init_sliders()
        self.init_radio_button()

        self.sliders[self.dependent_variable].disable()
        self.init_button()

        plt.show()



def main():
    mct1 = McCabeThiele()
    mct1.main()


if __name__ == "__main__":
    main()



