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


def visualize_one(img: np.ndarray, order: int):
    fig = plt.figure(figsize=(_FIGSIZE, _FIGSIZE))
    cbar_min = np.round(np.min(img), 2)
    cbar_max = np.round(np.max(img), 2)
    norm = plt.Normalize(cbar_min, cbar_max)
    fig.add_subplot()
    im = plt.imshow(img, norm=norm)
    colorbar(im, cbar_min, cbar_max)
    plt.xticks([])
    plt.yticks([])
    plt.title(f'Zernike polynomial of order {order}', fontsize=_FONTSIZE)
    plt.show()


def visualize_all(imgs: np.ndarray, order: int, ncols: int):
    fig, axes = plt.subplots(ncols, ncols, figsize=(_FIGSIZE*1.5, _FIGSIZE*1))
    idx = 0
    for r, row in enumerate(axes):
        for c, ax in enumerate(row):
            ax.set_axis_off()
            if idx > order or c > r:
                continue
            else:
                img = imgs[:, :, idx]
                im = ax.imshow(img)
                ax.set_title(f'{idx}', fontsize=int(_FONTSIZE*4/ncols), y=1.0, pad=0)
                h, w = img.shape
                patch = patches.Circle((h//2, w//2), radius=h/2-1, transform=ax.transData)
                im.set_clip_path(patch)
                idx += 1
    fig.suptitle(f'All the Zernike modes up to order {order}', fontsize=_FONTSIZE)
    plt.show()
