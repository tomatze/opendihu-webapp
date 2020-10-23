# Overview
The opendihu-webapp is part of my Bachelor Thesis "Webapplication for multiphysics simulations with opendihu".

[Opendihu](https://github.com/maierbn/opendihu) is a software framework that solves static and dynamic multi-physics problems, spatially discretized in 1D, 2D and 3D by the finite element method.

This Project aims to simplify the creation of a new simulation in opendihu for end users by visualizing the nested solver-structures and parameters of simulations.

# Requirements
* Python3
* GTK+3
* [PyGObject](https://pygobject.readthedocs.io/en/latest/getting_started.html)
* [gtksourceview](https://gitlab.gnome.org/GNOME/gtksourceview)

## ubuntu
`sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 libgtksourceview-4-0`

## archlinux
`sudo pacman -S gtk3 python-gobject gtksourceview4`

## macOS
`brew install pygobject3 gtk+ gtksourceview4`

## windows (using MSYS2)
* download and install [MSYS2](https://www.msys2.org/#installation)
* run MSYS2 and install requirements:

`pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-gobject mingw-w64-x86_64-gtksourceview4`

# Usage
`git clone 'https://github.com/tomatze/opendihu-webapp'`

`cd opendihu-webapp`

`python3 gui.py`
