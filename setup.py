#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "img2wav",
    version = "0.1.2",
    description = "Convert images to wav audio files to view in a spectrogram",
    long_description = read("README.rst"),
    author = "Christian Sharpsten",
    author_email = "chris.sharpsten@gmail.com",
    license = "GPL-2",
    url = "https://github.com/shareef12/img2wav",
    download_url = "https://github.com/shareef12/img2wav/archive/v0.1.2.tar.gz",
    py_modules = ["img2wav"],
    install_requires = [
        "numpy",
        "Pillow",
    ],
    entry_points = {
        "console_scripts": [
            "img2wav = img2wav:main",
        ],
    })
