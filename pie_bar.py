import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
import numpy as np


# pie chart parameters
def pie_expand(ratios, labels, explode, colors, name):
    # make figure and assign axis objects
    fig, (ax1, ax2) = plt.subplots(1, 2, dpi=300, figsize=(10, 6))
    fig.subplots_adjust(wspace=0)


    # rotate so that first wedge is split by the x-axis
    angle = -180 * ratios[0][0] / sum(ratios[0])
    ax1_color = [colors[c] for c in labels[0]]

    ax1.pie(ratios[0], autopct='%1.1f%%', startangle=angle,
            labels=labels[0], explode=explode,  textprops={'fontsize': 10}, colors=ax1_color)

    # bar chart parameters
    xpos = 0
    bottom = 0
    width = .2

    ax2_color = [colors[c] for c in labels[1]]

    for j in range(len(ratios[1])):
        height = ratios[1][j]
        ax2.bar(xpos, height, width, bottom=bottom, color=ax2_color[j])
        ypos = bottom + ax2.patches[j].get_height() / 2
        bottom += height
        ax2.text(xpos, ypos, f"{height/sum(ratios[1])*ratios[0][0] / sum(ratios[0])* 100: .2f}%, {labels[1][j]}",
                ha='center')

    ax2.set_title('Expand')
    # ax2.legend(labels[1])
    
    ax2.axis('off')
    ax2.set_xlim(- 2.5 * width, 2.5 * width)

    # use ConnectionPatch to draw lines between the two plots
    # get the wedge data
    theta1, theta2 = ax1.patches[0].theta1, ax1.patches[0].theta2
    center, r = ax1.patches[0].center, ax1.patches[0].r
    bar_height = sum([item.get_height() for item in ax2.patches])

    # draw top connecting line
    x = r * np.cos(np.pi / 180 * theta2) + center[0]
    y = r * np.sin(np.pi / 180 * theta2) + center[1]
    con = ConnectionPatch(xyA=(-width / 2, bar_height), coordsA=ax2.transData,
                        xyB=(x, y), coordsB=ax1.transData)
    con.set_color([0, 0, 0])
    con.set_linewidth(4)
    ax2.add_artist(con)

    # draw bottom connecting line
    x = r * np.cos(np.pi / 180 * theta1) + center[0]
    y = r * np.sin(np.pi / 180 * theta1) + center[1]
    con = ConnectionPatch(xyA=(-width / 2, 0), coordsA=ax2.transData,
                        xyB=(x, y), coordsB=ax1.transData)
    con.set_color([0, 0, 0])
    con.set_linewidth(4)
    ax2.add_artist(con)

    plt.savefig(name, dpi=300)

    