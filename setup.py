#!/usr/bin/env python
from setuptools import setup, find_packages
import sphinx_explorer

requires = [
    'sphinx>=1.5',
    'pyqt5',
    'qdarkstyle',
    'qtpy',
    'toml',
    'typing',
    'pyYaml',
    'markdown',
    'py-gfm',
    'six',
    'docutils',
    'sphinx-autobuild',
    'sphinx-rtd-theme',
    'sphinx-fontawesome',
    'sphinxcontrib-blockdiag',
    'nbsphinx',
]

setup(
    name='Sphinx Explorer',
    version=sphinx_explorer.__version__,
    description='Python documentation generator',
    author='Toshiyuki Ishii.',
    author_email='pashango2@gmail.com',
    url='https://github.com/pashango2/sphinx-explorer',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=requires,
    platforms='any',
    license="MIT",
    entry_points={
        'gui_scripts': [
            'sphinx-explorer = sphinx_explorer:package_main',
        ],
    },
)
