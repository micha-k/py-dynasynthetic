#!/usr/bin/env python

import io
import os
from setuptools import setup, find_packages
import dynasynthetic

PKG_VER = dynasynthetic.__version__


def read(*filenames, **kwargs):
    """
        Read files and join them for a long description.
    """
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        if os.path.isfile(filename):
            with io.open(filename, encoding=encoding) as filesocket:
                buf.append(filesocket.read())
    return sep.join(buf)


setup(
    name='py-dynasynthetic',
    packages=find_packages(exclude=['tests']),
    scripts=[
        'check_dynasynthetic.py',
        'dynasynthetic_cli.py'
    ],
    description='Access the Dynatrace Synthetic API',
    long_description=read('README.md'),
    version=PKG_VER,
    url='http://github.com/micha-k/py-dynasynthetic',
    download_url="http://github.com/micha-k/py-dynasynthetic/tarball/v" + PKG_VER,
    license='Apache Software License',
    author='micha-k',
    platforms='any',
    install_requires=read('requirements.txt'),
    setup_requires=read('test-requirements.txt'),
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['dynatrace', 'monitoring',
              'performance', 'metric', 'dashboarddata']
)
