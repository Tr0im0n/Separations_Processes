from matplotlib.widgets import Slider
from matplotlib.text import Text
import matplotlib.pyplot as plt


class CustomSlider(Slider):
    """
    A Matplotlib Slider subclass that positions the label and value text
    above the slider bar, instead of to the left and right.
    """

    def __init__(self, ax, label, valmin, valmax, valinit=0.5, valfmt='%1.2f', **kwargs):
        super().__init__(ax, label, valmin, valmax, valinit=valinit, valfmt=valfmt, **kwargs)
        # Hide the default labels
        self.label.set_visible(False)
        self.valtext.set_visible(False)
        # Get positions
        x0, y0, width, height = ax.get_position().bounds
        fig = ax.figure
        # make new labels
        self.custom_label = fig.text(
            x0  + 0.01,
            y0 + height,
            label,
            ha='left',
            va='bottom',
            fontsize=10)
        self.custom_valtext = fig.text(
            x0 + width - 0.01,
            y0 + height,
            self.valfmt % self.val,
            ha='right',
            va='bottom',
            fontsize=10)
        # Update the text, when changed
        self.on_changed(self._update_custom_text)
        # Make it able to disable the slider
        self._event_handlers = {}
        self._is_enabled = True

        # self._store_handlers()

    def _update_custom_text(self, val):
        """Internal method to update the position and text of the custom value label."""
        self.custom_valtext.set_text(self.valfmt % val)

    def set_val_text(self, val):
        self.custom_valtext.set_text(self.valfmt % val)

    def disable(self):
        self.set_active(False)
        self.eventson = False
        self.poly.set_alpha(0.5)

    def enable(self):
        self.set_active(True)
        self.eventson = True
        self.poly.set_alpha(1.0)
