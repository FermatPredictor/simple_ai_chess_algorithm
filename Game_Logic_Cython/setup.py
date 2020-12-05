from distutils.core import setup
from Cython.Build import cythonize
setup(ext_modules = cythonize('reversi_get_valid_move_cython.pyx'))