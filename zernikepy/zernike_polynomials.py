import typing as tp

import numpy as np
from scipy.special import binom
from zernikepy.plots import visualize_all, visualize_one

ModeType = tp.Union[int, str]

lookup_table = {
    'piston': 0,
    'vertical tilt': 1,
    'horizontal tilt': 2,
    'oblique astigmatism': 3,
    'defocus': 4,
    'vertical astigmatism': 5,
    'vertical trefoil': 6,
    'vertical coma': 7,
    'horizontal coma': 8,
    'oblique trefoil': 9,
    'oblique quadrafoil': 10,
    'oblique secondary astigmatism': 11,
    'primary spherical': 12,
    'vertical secondary astigmatism': 13,
    'vertical quadrafoil': 14
}


def zernike_polynomials(mode: tp.Union[int, str] = 'defocus',
                        select: tp.Union[int, str, tp.List[ModeType]] = None,
                        size: int = 128,
                        show: bool = False,
                        **kwargs) -> np.ndarray:
    """ Computation of Zernike polynomials of (or up to) a given order

    Parameters
    ----------
    mode: int, str
        default: 'defocus'
        if int: OSA order of the Zernike polynomial; if str: find the corresponding OSA order in the lookuptable
    select: int, str, list
        default: None
        None: use the specified order in 'mode'
        'all': use all the orders up to 'mode'
        list: use orders specified in this list
    size: int
        default: 128
        number of pixels of the length of the image
    show: bool
        default: False
        plot the images or not
    Returns
    -------

    Notes
    -----
    Ref. https://en.wikipedia.org/wiki/Zernike_polynomials#Zernike_polynomials
    """
    # validate input variables
    orders = _validate_inputs(mode, select, size)
    order_max = orders[-1]
    # create mesh
    radius = size / 2
    rho, phi = create_mesh(size, radius)
    # find (n, l) pairs such that n(n+2)+l/2 in orders
    n = 0
    pairs = []
    break_loop = False
    while not break_loop:
        for l in range(-n, n + 1, 2):
            j = (n * (n + 2) + l) / 2
            if j in orders:
                pairs.append((n, l))
            if j > order_max:
                break_loop = True
        n += 1

    # compute the polynomial(s)
    n_pairs  = len(pairs)
    if n_pairs == 0:
        raise ValueError(f'No Zernike polynomial of mode(s): {orders} found')
    elif n_pairs == 1:
        n, l = pairs[0]
        output = zernike_nl(n, l, rho, phi, radius)
        if show:
            visualize_one(output, orders[0], **kwargs)
    else:
        output = np.dstack([zernike_nl(n, l, rho, phi, radius) for (n, l) in pairs])
        if show:
            _n, _ = pairs[-1]
            visualize_all(output, orders, _n + 1, **kwargs)

    return output


def zernike_nl(n: int, l: int, rho: float, phi: float, radius: float):
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

def _validate_individual_mode(mode: ModeType) -> int:
    """Validate the variable 'mode'
    - Check the type of the variable
    - check the value of the variable

    Parameters
    ----------
    mode: ModeType

    Returns
    -------

    """
    if type(mode) is int:
        if mode < 0:
            raise ValueError('please provide a nonnegative integer!')
    elif type(mode) is str:
        mode_str = mode
        mode = lookup_table.get(mode.lower())
        if mode is None:
            raise ValueError(f'Invalid name {mode_str} for the mode. Try its index instead.')
    else:
        raise TypeError(f'Unkown mode type {type(mode)}, it should be int or str')
    return mode


def _validate_inputs(
        mode: ModeType,
        select: tp.Union[int, str, tp.List[ModeType], None],
        size: int) -> tp.List[int]:
    """Validate all the input variables

    Parameters
    ----------
    mode: ModeType
    select: int, str, list
    size: int

    Returns
    -------

    """
    # check size
    if type(size) is not int or size < 0:
        raise TypeError(f'size should be a nonnegative integer, not {size} of {type(size)}')

    # check mode
    mode = _validate_individual_mode(mode)

    # check select:
    mode_list = []
    if select is None:
        mode_list.append(mode)
    elif type(select) is str:
        if select.lower() == 'all':
            mode_list = list(range(mode + 1))
    elif type(select) is list:
        if len(select) == 1:
            item = _validate_individual_mode(select[0])
            if item != mode:
                raise ValueError(f'Please select mode={select[0]} instead')
        for item in select:
            item = _validate_individual_mode(item)
            if item > mode:
                raise ValueError(f'selected mode {item} bigger than {mode}')
            mode_list.append(item)
    return sorted(mode_list)
