from matplotlib.widgets import Slider
from matplotlib.text import Text
import matplotlib.pyplot as plt


class LabeledSlider(Slider):
    """
    A Matplotlib Slider subclass that positions the label and value text
    above the slider bar, instead of to the left and right.
    """

    def __init__(self, ax, label, valmin, valmax, valinit=0.5, valfmt='%1.2f', **kwargs):
        # 1. Initialize the parent Slider class
        super().__init__(ax, label, valmin, valmax, valinit=valinit, valfmt=valfmt, **kwargs)

        # 2. Hide the default labels
        self.label.set_visible(False)
        self.valtext.set_visible(False)

        # 3. Get normalized coordinates of the slider's Axes
        # ax.get_position() returns a Bbox (0..1 normalized figure coordinates)
        # Bbox.bounds gives (x0, y0, width, height)
        x0, y0, width, height = ax.get_position().bounds

        # Define positions for custom labels (normalized to the Figure)
        # Center of the slider
        label_x = x0 + width / 2

        # Position slightly above the slider Axes (ax.axes.figure is the parent Figure)
        label_y = y0 + height

        # 4. Create and store custom Text Artists
        fig = ax.figure

        # The main parameter label (e.g., 'xb', 'xf')
        self.custom_label = fig.text(
            x0  + 0.01,
            label_y,
            label,
            ha='left',
            va='bottom',
            fontsize=10
        )

        # The value label (dynamically updated)
        self.custom_valtext = fig.text(
            x0 + width - 0.01,
            label_y,  # Position slightly higher than the label
            self.valfmt % self.val,
            ha='right',
            va='bottom',
            fontsize=10,
        )

        # 5. Connect the update function to also update the custom value text
        # This is a critical step: whenever the slider value changes, we update the custom text.
        self.on_changed(self._update_custom_text)

    def _update_custom_text(self, val):
        """Internal method to update the position and text of the custom value label."""
        self.custom_valtext.set_text(self.valfmt % val)
        # We don't need to manually draw_idle here; the parent Slider's on_changed call
        # (which calls our attached functions) triggers the necessary canvas redraw.

class Me:
    def __init__(self, ax, label, valmin, valmax, valinit=0.5, valfmt='%1.2f', **kwargs):
        super().__init__(ax, label, valmin, valmax, valinit=valinit, valfmt=valfmt, **kwargs)

        self.label.set_visible(False)
        self.valtext.set_visible(False)

        # ax.get_position() returns a Bbox (0..1 normalized figure coordinates)
        # Bbox.bounds gives (x0, y0, width, height)
        x0, y0, width, height = ax.get_position().bounds

        label_y = y0 + height

        fig = ax.figure

        # The main parameter label (e.g., 'xb', 'xf')
        self.custom_label = fig.text(
            x0  + 0.01,
            label_y,
            label,
            ha='left',
            va='bottom',
            fontsize=10
        )

        # The value label (dynamically updated)
        self.custom_valtext = fig.text(
            x0 + width - 0.01,
            label_y,  # Position slightly higher than the label
            self.valfmt % self.val,
            ha='right',
            va='bottom',
            fontsize=10,
        )

        # 5. Connect the update function to also update the custom value text
        # This is a critical step: whenever the slider value changes, we update the custom text.
        self.on_changed(self._update_custom_text)

    def _update_custom_text(self, val):
        """Internal method to update the position and text of the custom value label."""
        self.custom_valtext.set_text(self.valfmt % val)
        # We don't need to manually draw_idle here; the parent Slider's on_changed call
        # (which calls our attached functions) triggers the necessary canvas redraw.