import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rc
import pathlib

figure_dir = pathlib.Path("../../3140-csc-article/Software_X/content/figures/")
pwp_dir = pathlib.Path("D:/Bulk docs/University/2020/semester-2/CSC/poster-and-presentation/graphs")
# plt.style.use('dark_background')

font = {'family': 'serif'}

rc('text', usetex=True)
rc('font', **font)


aspect_ratio = 4 / 5
FULL = 5, 5 * aspect_ratio
HALF = 3, 3 * aspect_ratio

LINESTYLES = 'k--', 'b.', 'rd', 'k-'


def plot_dict(d, ts=None, interval=1, xlabel=None, ylabel=None, ax=None, lines=LINESTYLES, colours=None, labs=None,
              figsize=FULL, legend=True, loc='best', **kwargs):
    """ Simplifies the plotting of publication-ready data with latex text and different line formats for a dictionary.

    :param loc: same as plt.legend(loc=__), default='best'
    :param legend: default=True, specify whether a legend is shown
    :param figsize: same as matplotlib figsize
    :param labs: spcify line labels, if not specified, will use d.keys() as labels
    :param colours: specify line colours
    :param lines: specify the line style for all the different series
    :param ax: allows adding plots to an existing matplotlib.axis.Axes object
    :param ylabel: set the y-axis label
    :param xlabel: Set the x-axis label
    :param interval: specify the the index interval between plotted data, used to reduce the number of points plotted
    :param ts: Shared x data, requires same length for all data in d
    :param d: dictionary containing data to be plotted, if ts is not specified, the data can be of different lengths
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    if labs is None:
        labs = d.keys()
    if colours is None:
        colours = [None]*len(lines)

    for (key, val), lab, style, colour in zip(d.items(), labs, lines, colours):

        if ts is None:
            ts = np.arange(len(val))
        tsp = ts[::interval]
        valp = val[::interval]

        ax.plot(tsp, valp, style, label=lab, color=colour, **kwargs)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)

    if legend:
        ax.legend(loc=loc)
    plt.tight_layout()

    return ax


def multi_bar(bar_dat, bar_labs, group_names, colours=None, xlabel=None, ylabel=None, figsize=FULL):
    N_dats = len(bar_dat)  # number of data sets
    if colours is None:
        colours = [None]*N_dats
    N_groups = len(bar_dat[0])  # number of groups in each data set

    # calculate locations

    start_group_loc = np.arange(N_groups)
    width = 1/(N_dats+1)  # adds one width so that there is an open column between different groups

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    for i, (data, lab, colour) in enumerate(zip(bar_dat, bar_labs, colours)):
        ax.bar(start_group_loc + i*width, data, width, label=lab, color=colour)
    plt.xticks(start_group_loc + (N_dats-1)*width/2, group_names, rotation=90)
    ax.legend(loc='best')
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    plt.tight_layout()

    return ax
