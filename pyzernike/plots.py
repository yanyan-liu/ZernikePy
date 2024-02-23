import typing as tp

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.axes_grid1 import make_axes_locatable

_FONTSIZE = 15
_FIGSIZE = _FONTSIZE // 2


def colorbar(mappable, cbar_min, cbar_max):
    last_axes = plt.gca()
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = fig.colorbar(mappable, cax=cax)
    cbar.set_ticks([cbar_min, 0, cbar_max])
    cbar.set_ticklabels([cbar_min, 0, cbar_max], fontsize=_FONTSIZE)
    plt.sca(last_axes)
    return cbar


def visualize_one(img: np.ndarray, order: int, **kwargs):
    """visualize one mode

    Parameters
    ----------
    img: np.ndarray
        Zernike mode to be shown
    order: int
        order of the mode
    kwargs:
        'cmap': colormap of the plot, choose one valid for plt

    Returns
    -------

    """
    cmap = kwargs.get('cmap')
    cbar_min = -1
    cbar_max = 1

    fig = plt.figure(figsize=(_FIGSIZE, _FIGSIZE))
    norm = plt.Normalize(cbar_min, cbar_max)
    fig.add_subplot()
    im = plt.imshow(img, norm=norm, cmap=cmap)
    colorbar(im, cbar_min, cbar_max)
    plt.xticks([])
    plt.yticks([])
    plt.title(f'Zernike polynomial of order {order}', fontsize=_FONTSIZE)
    plt.show()


def visualize_all(imgs: np.ndarray, orders: tp.List, ncols: int, **kwargs):
    """visualize all the modes up to a given order in a pyramid (bottom left of a square grid)

    Parameters
    ----------
    imgs: np.ndarray
        all the images in the list of orders
    orders: list
        list of all the modes
    ncols: int
        number of columns in the figure
    kwargs:
        'cmap': colormap of the plot, choose one valid for plt

    Returns
    -------

    """
    cmap = kwargs.get('cmap')
    order_max = orders[-1]
    fig, axes = plt.subplots(ncols, ncols, figsize=(_FIGSIZE*1.5, _FIGSIZE*1))
    idx = 0
    order_idx = 0
    for r, row in enumerate(axes):
        for c, ax in enumerate(row):
            ax.set_axis_off()
            if c > r:
                continue
            if order_idx in orders:
                img = imgs[:, :, idx]
                im = ax.imshow(img, cmap=cmap)
                # dymanic fontsize for the title, adjust title position
                ax.set_title(f'{order_idx}', fontsize=int(_FONTSIZE*4/ncols), y=1.01, pad=0)
                # only show the disk on which the polynomial is defined
                h, w = img.shape
                patch = patches.Circle((h//2, w//2), radius=h/2-1, transform=ax.transData)
                im.set_clip_path(patch)
                idx += 1
            order_idx += 1
    fig.suptitle(f'Zernike modes up to order {order_max}', fontsize=_FONTSIZE)
    plt.show()
