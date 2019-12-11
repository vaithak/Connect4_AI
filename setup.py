from distutils.core import *
from setuptools import setup, Extension
os.environ["CC"] = "g++" # force compiling c as c++
setup(name='Connect4AI',
    version='1',
    ext_modules=[Extension('_Connect4AI', sources=['AI_cpp_module/src/GameState.cpp', 'AI_cpp_module/src/Solver.cpp', 'Connect4AI.i'],
                    swig_opts=['-c++'],
                    extra_compile_args=['--std=c++14', '-IAI_cpp_module/includes/']
                    )],
    headers=['AI_cpp_module/includes/GameState.h','AI_cpp_module/includes/Solver.h','AI_cpp_module/includes/TranspositionTable.h']
)