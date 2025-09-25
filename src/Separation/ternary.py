
import os
import numpy as np
import matplotlib.pyplot as plt

directory_location = r"C:\Users\Tom\Documents\Universiteit\Separations Processes\2025 Week 3\graded"

os.chdir(directory_location)

triangle_points = np.array([[0.0, 0.0],
                            [50.0, 100],
                            [100.0, 0.0],
                            [0.0, 0.0]])

inputs = np.array([[70.0, 30.0, 0.0], [0.0, 0.0, 100.0]])

solubilty_curve_file_name = r"solubility curve.txt"
# order of arrays is Water, Acid, Solvent
# with open(solubilty_curve_file_name, 'r') as f:
#     numbers_list = [float(line.strip()) for line in f]

solubility_array1d = np.loadtxt(solubilty_curve_file_name)
solubility_table2d = solubility_array1d.reshape(16, 9)
solubility_array = solubility_table2d[:, -3:]
solubility_array *= 100

tie_lines_file_name = r"tie lines.txt"
tie_lines1d = np.loadtxt(tie_lines_file_name)
tie_lines2d = tie_lines1d.reshape(6, 6)
tie_lines2d *= 100
tie_lines1 = tie_lines2d[:, :3]
tie_lines2 = tie_lines2d[:, -3:]


def convert_ternary_to_xy(array):
    """
    Input is an array with n rows and 3 columns
    :param array:
    :return:
    """
    return np.array([[0.5 * row[1] + row[2], row[1]] for row in array])


my_xy = convert_ternary_to_xy(solubility_array)
inputs = convert_ternary_to_xy(inputs)
tie1 = convert_ternary_to_xy(tie_lines1)
tie2 = convert_ternary_to_xy(tie_lines2)

fig, ax = plt.subplots(figsize=(8, 6), dpi=120)
# plt.ion()

ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

background = None
line, = ax.plot([0, 0], [0, 0], 'r-')

def draw_background():
    ax.cla()

    ax.plot(triangle_points[:,0], triangle_points[:,1], color='k')
    ax.plot(my_xy[:,0], my_xy[:,1])
    ax.plot(inputs[:,0], inputs[:,1])
    for i in range(6):
        ax.plot([tie1[i, 0], tie2[i, 0]], [tie1[i, 1], tie2[i, 1]], color='g')

    ax.text(-2, -6, "Water", ha='center', va='top', fontsize=16)
    ax.text(50, 100, "Acid", ha='center', va='bottom', fontsize=16)
    ax.text(102, -6, "Solvent", ha='center', va='top', fontsize=16)
    ax.text(101, 0, "S", ha='left', va='bottom', fontsize=16, c='r')
    ax.text(15, 30, "F", ha='right', va='bottom', fontsize=16, c='r')

    # fig.canvas.draw()

    global background
    background = fig.canvas.copy_from_bbox(ax.bbox)

    # ax.draw_artist(line)


draw_background()


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

cid1 = fig.canvas.mpl_connect('draw_event', on_reshape)
cid2 = fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)   # 'button_press_event'

# fig.savefig("fig1.png", dpi=400)
# background = fig.canvas.copy_from_bbox(fig.bbox)    # ax or fig

plt.show()


