import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='retricon',
    version='1.0',
    packages=['retricon',],
    license="MIT License",
    description='Library to create cool icon based',
    long_description=README,
    url='http://github.com/rphlo/django-seuranta',
    author='Raphael Stefanini',
    author_email='rphl@rphl.net',
)