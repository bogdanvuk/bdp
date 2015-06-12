# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

requires = ['pexpect', 'sphinx-argparse']

setup(
    name='bdp',
    version='0.2',
    url='https://github.com/bogdanvuk/bdp',
    download_url = 'https://github.com/bogdanvuk/bdp/tarball/0.2',
    license='BSD',
    author='Bogdan Vukobratovic',
    author_email='bogdan.vukobratovic@gmail.com',
    description='Block Diagrams in Python',
    long_description=long_description,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
	'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Sphinx :: Extension',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    keywords= ['Python', 'TikZ', 'Block diagram', 'PDF', 'PNG', 'Sphinx'],
    entry_points={
        'console_scripts': [
            'bdp = bdp.render:main',
        ],
    },
    install_requires=requires,
)
