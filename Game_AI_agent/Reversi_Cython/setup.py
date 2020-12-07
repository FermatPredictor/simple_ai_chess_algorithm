from distutils.core import setup
from Cython.Build import cythonize
setup(ext_modules = cythonize('eval_func_cython.pyx'))

"""
to complie cython, use
python setup.py build_ext --inplace
"""