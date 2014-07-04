import os
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='retricon',
    version='1.1.0',
    packages=['retricon',],
    license="MIT License",
    description='Library to create unique images such as Github avatar',
    url='http://github.com/rphlo/py-retricon',
    download_url='https://github.com/rphlo/py-retricon/tarball/v1.1.0',
    author='Raphael Stefanini',
    author_email='rphl@rphl.net',
    keywords = ['image', 'avatar', 'icon'],
    classifiers=[],
    install_requires=[
        'pillowfight'
    ]
)
