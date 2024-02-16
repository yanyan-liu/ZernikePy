import typing as tp
from src.calculate import zernike_polynomials


def zernike(mode: tp.Union[int, str] = 4, size: int = 128, passall: bool = False, show: bool = False):
    output = zernike_polynomials(mode, size, passall, show)
    return output
