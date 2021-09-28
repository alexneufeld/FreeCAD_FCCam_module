from setuptools import setup
import os
# from freecad.FCCam.version import __version__
# name: this is the name of the distribution.
# Packages using the same name here cannot be installed together

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                            "freecad", "FCCam", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.FCCam',
      version=str(__version__),
      packages=['freecad',
                'freecad.FCCam'],
      maintainer="alexneufeld",
      maintainer_email="alex.d.neufeld@gmail.com",
      url="https://github.com/alexneufeld/FreeCAD_FCCam_module",
      description="freecad module to create cam shapes",
      install_requires=['numpy','matplolib'], # should be satisfied by FreeCAD's system dependencies already
      include_package_data=True)
