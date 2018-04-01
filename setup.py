#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name="img2wav",
      version="0.1.0",
      description="Convert images to wav audio files to view in a spectrogram",
      author="Christian Sharpsten",
      author_email="chris.sharpsten@gmail.com",
      packages=find_packages(),
      install_requires=[
          "numpy",
          "Pillow",
      ],
      entry_points={
          "console_scripts": [
              "img2wav = img2wav:main",
          ],
      })
