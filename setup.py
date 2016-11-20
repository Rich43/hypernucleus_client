#!/usr/bin/python3
from setuptools import setup, find_packages

install_requires = [
    'setuptools',
    'PyQt5',
    'requests'
]

setup(name='hypernucleus',
      version='1.0',
      description='Hypernucleus Client - A Python Game Database',
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.5",
          "Environment :: X11 Applications :: Qt",
          "Topic :: Games/Entertainment",
          "Topic :: Desktop Environment :: K Desktop Environment (KDE)",
          "License :: OSI Approved :: GNU General Public License (GPL)",
      ],
      package_data={
          'hypernucleus.view': ['*.ui'],
      },
      keywords='game database pygame',
      author="Richie Ward, Pynguins",
      author_email="RichieS@GMail.com",
      url="http://hypernucleus.pynguins.com",
      license="GPL",
      packages=find_packages(),
      install_requires=install_requires,
      entry_points={
          'gui_scripts': [
              'run_hypernucleus = hypernucleus:main',
          ]
      }
      )
