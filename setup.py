#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pandocfilters',
    'blockdiag'
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pandoc_blockdiag',
    version='0.1.0',
    description="Python blockdiag filter",
    long_description=readme + '\n\n' + history,
    author="Nahuel Defossé",
    author_email='nahuel.defosse@gmail.com',
    url='https://github.com/D3f0/pandoc_blockdiag',
    packages=[
        'pandoc_blockdiag',
    ],
    package_dir={'pandoc_blockdiag':
                 'pandoc_blockdiag'},
    entry_points={
        'console_scripts': [
            'pandoc_blockdiag=pandoc_blockdiag.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pandoc_blockdiag',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
