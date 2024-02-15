import numpy as np
from scipy.special import binom
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def _zernike_nl(n: int, l: int, rho: float, phi: float, radius: float):
    """ Computation of the Zernike polynomial of order n and m in the polar coordinates

    Parameters
    ----------
    n: int
        index n in the definition on wikipedia, positive integer
    l: int
        |l| = m, m is the index m in the definition on wikipedia. l can be positive or negative
    rho: float
        radial distance
    phi: float
        azimuthal angle
    radius: float
        radius of the disk on which the Zernike polynomial is defined

    Returns
    -------
    Z: np.ndarray
        Zernike polynomial given indices n and l

    """
    m = abs(l)
    R = 0
    for k in np.arange(0, (n - m) / 2 + 1):
        R = R + (-1) ** k * binom(n - k, k) * binom(n - 2 * k, (n - m) / 2 - k) * (rho/radius) ** (n - 2 * k)

    # radial part
    Z = np.where(rho <= radius, R, 0)

    # angular part
    Z *= np.cos(m * phi) if l >= 0 else np.sin(m * phi)
    return Z


def zernike_polynomials(size: int, order: int, passall: bool = 0) -> np.ndarray:
    """ Computation of Zernike polynomials

    Parameters
    ----------
    size: int
        number of pixels of the length of the image
    order: int
        OSA order of the Zernike polynomial
    passall: bool
        return all polynomials up to the given order. If false, only return one polynomial with the given order

    Returns
    -------

    Notes
    -----
    Ref. https://en.wikipedia.org/wiki/Zernike_polynomials#Zernike_polynomials
    """
    # validate input vaiables
    if type(size) is not int:
        raise TypeError(f'size should be an integer, not {type(size)}')
    if type(order) is not int:
        raise TypeError(f'order should be an integer, not {type(order)}')
    elif order < 0:
        raise ValueError(f'order should be a positive integer')

    rho, phi = create_mesh(size)

    n = 0
    zernike_stack = []
    while True:
        pairs = [(n, l) for l in np.arange(-n, n + 1, 2) if (n * (n + 2) + l) / 2 <= order]
        if pairs:
            print(pairs)
            zernike_stack.extend([_zernike_nl(n, l, rho, phi, size//2) for (n, l) in pairs])
            n += 1
        else:
            break

    if not zernike_stack:
        raise ValueError(f'The list of polynomials is empty, no Zernike polynomial of order {order} is found')
    elif passall:
        return np.dstack(zernike_stack)
    else:
        visualize_one(zernike_stack[-1], order)


def create_mesh(size):
    radius = size // 2
    x = np.linspace(-radius, radius, size)
    y = np.linspace(-radius, radius, size)
    xx, yy = np.meshgrid(x, y, indexing='xy')
    rho = np.sqrt(xx ** 2 + yy ** 2)
    phi = np.angle(xx + 1j * yy)
    return rho, phi


def colorbar(mappable):
    last_axes = plt.gca()
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = fig.colorbar(mappable, cax=cax)
    cbar.set_ticks([-np.pi, 0, np.pi])
    cbar.set_ticklabels(['-$\pi$', 0, '$\pi$'], fontsize=32)
    plt.sca(last_axes)
    return cbar


def visualize_one(img: np.ndarray, order: int):
    fig = plt.figure(figsize=(16, 16))
    norm = plt.Normalize(-np.pi, np.pi)
    fig.add_subplot()
    im = plt.imshow(img, norm=norm)
    colorbar(im)
    plt.xticks([])
    plt.yticks([])
    plt.title(f'Zernike polynomial of order {order}', fontsize=32)
    plt.show()
