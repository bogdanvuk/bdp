# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
bdp (Block Diagram in Python) is a package that translates diagrams described using Python objects to TikZ and renders PDF and PNG images.
'''

requires = ['pexpect', 'sphinx-argparse']

setup(
    name='bdp',
    version='0.1',
    url='https://github.com/bogdanvuk/bdp',
    download_url = 'https://github.com/bogdanvuk/bdp/tarball/0.1',
    license='BSD',
    author='Bogdan Vukobratovic',
    author_email='bogdan.vukobratovic@gmail.com',
    description='Block Diagrams in Python',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Sphinx :: Extension',
        #'Framework :: Sphinx :: Theme',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bdp = bdp.render:main',
        ],
    },
    install_requires=requires,
)
