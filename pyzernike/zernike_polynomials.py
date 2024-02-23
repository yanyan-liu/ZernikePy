import typing as tp

import numpy as np
from scipy.special import binom
from pyzernike.plots import visualize_all, visualize_one


lookup_table = {
    'piston': 1,
    'vertical tilt': 2,
    'horizontal tilt': 3,
    'oblique astigmatism': 4,
    'defocus': 5,
    'vertical astigmatism': 6,
    'vertical trefoil': 7,
    'vertical coma': 8,
    'horizontal coma': 9,
    'oblique trefoil': 10,
    'oblique quadrafoil': 11,
    'oblique secondary astigmatism': 12,
    'primary spherical': 13,
    'vertical secondary astigmatism': 14,
    'vertical quadrafoil': 15
}


def zernike_polynomials(mode: tp.Union[int, str] = 5,
                        size: int = 128,
                        passall: bool = False,
                        show: bool = False,
                        **kwargs) -> np.ndarray:
    """ Computation of Zernike polynomials of (or up to) a given order

    Parameters
    ----------
    mode: int, str
        if int: OSA order of the Zernike polynomial; if str: find the corresponding order in the lookuptable
    size: int
        number of pixels of the length of the image
    passall: bool
        return all polynomials up to the given order. If false, only return one polynomial with the given order
    show: bool
        plot the polymonials or not
    Returns
    -------

    Notes
    -----
    Ref. https://en.wikipedia.org/wiki/Zernike_polynomials#Zernike_polynomials
    """
    # validate input variables
    if type(mode) is str:
        order = lookup_table.get(mode.lower())
        if order is None:
            raise ValueError(f'Invalid name {mode} for the mode. Try its index instead.')
    else:
        order = mode
    if type(order) is not int:
        raise TypeError(f'order should be an integer, not {type(order)}')
    elif order < 0:
        raise ValueError(f'order should be a positive integer')

    if type(size) is not int:
        raise TypeError(f'size should be an integer, not {type(size)}')

    # create mesh
    radius = size / 2
    rho, phi = create_mesh(size, radius)
    # find (n, l) pairs such that n(n+2)+l/2 < order
    n = 0
    pairs = []
    while True:
        _pairs_n = [(n, l) for l in np.arange(-n, n + 1, 2) if (n * (n + 2) + l) / 2 < order]
        if _pairs_n:
            pairs.extend(_pairs_n)
            n += 1
        else:
            break
    # compute the polynomial(s)
    if not pairs:
        raise ValueError(f'No Zernike polynomial of order {order} is found')
    elif passall:
        output = np.dstack([_zernike_nl(n, l, rho, phi, radius) for (n, l) in pairs])
        if show:
            _n, _ = pairs[-1]
            if _n == 0:
                visualize_one(output, order, **kwargs)
            else:
                visualize_all(output, order, _n + 1, **kwargs)
    else:
        _n, _l = pairs[-1]
        output = _zernike_nl(_n, _l, rho, phi, radius)
        if show:
            visualize_one(output, order, **kwargs)
    return output


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
        R = R + (-1) ** k * binom(n - k, k) * binom(n - 2 * k, (n - m) / 2 - k) * (rho / radius) ** (n - 2 * k)

    # radial part
    Z = np.where(rho <= radius, R, 0)

    # angular part
    Z *= np.cos(m * phi) if l >= 0 else np.sin(m * phi)
    return Z


def create_mesh(size: int, radius: float):
    """create polar-coordinate mesh on which the polynomial is defined

    Parameters
    ----------
    size: int
        number of pixels of the length of the image
    radius: float
        radius of the disk on which the polynomial is defined

    Returns
    -------

    """
    x = np.linspace(-radius, radius, size)
    y = np.linspace(-radius, radius, size)
    xx, yy = np.meshgrid(x, y, indexing='xy')
    rho = np.sqrt(xx ** 2 + yy ** 2)
    phi = np.angle(xx + 1j * yy)
    return rho, phi