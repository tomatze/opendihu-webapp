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
`sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-gtksource-4`

## archlinux
`sudo pacman -S gtk3 python-gobject gtksourceview4`

## macOS
`brew install pygobject3 gtk+ gtksourceview4`

## windows (using mingw)
* download and install [MSYS2](https://www.msys2.org/#installation)
* run a mingw-terminal `C:\msys64\mingw64.exe` and install git and the requirements (it's important to execute mingw not msys2):

`pacman -Suy`

`pacman -S git`

`pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-gobject mingw-w64-x86_64-gtksourceview4`

# Usage
`git clone 'https://github.com/tomatze/opendihu-webapp'`

`cd opendihu-webapp/src`

`python3 gui.py`

# Docker
On Linux you can also run this project with docker. This should also work on MacOS and Windows if an X11-server is installed first

## build the container
`git clone 'https://github.com/tomatze/opendihu-webapp'`

`cd opendihu-webapp`

`./docker-build.sh`

## run the container
`./docker-run.sh`
