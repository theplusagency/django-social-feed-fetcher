#!/usr/bin/env python

import sys

from social_fetcher import __version__

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


install_requires = [
    'Django>=2.2,<3.2',
    'requests>=2.11.1,<3.0'
]

setup(
    name='django-social-feed-fetcher',
    version=__version__,
    description='A simple tool to fetch content from Instagram & Facebook account feeds.',
    author='The Plus',
    author_email='hello@theplus.agency',
    url='https://github.com/theplusagency/django-social-feed-fetcher',
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    long_description='django-social-feed-fetcher is a simple tool to fetch and cache the latest \
    posts from an Instagram or Facebook account feed.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Topic :: Utilities',
    ],
    install_requires=install_requires
)
