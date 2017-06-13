ImageCmp
========

|license|

Quickly find similar images among many.

ImageCmp processes multiple image files and identifies similar images. Similar
images are images with a similar graphical content, regardless of their name,
size, resolution or timestamp.

ImageCmp fully supports both Python 2 and Python 3.

The imagecmp package is a library that implements the functionality and exports
an API. A future, separate, imagecmp-cli package is planned, to provide a
command-line utility.


Dependencies
------------

- Python Imaging Library (PIL), specifically the Pillow_ fork. Tested with
  versions 2.6.1 and 3.4.2, but should work with anything beyond version
  2.0.

- NumPy_ array processing module. Tested with versions 1.8.2 and 1.10.4, but
  should work with anything beyond version 1.8.

To install Pillow on Gentoo, install ``dev-python/pillow``. On Debian or Ubuntu,
install ``python-pil`` or ``python3-pil``.

To install NumPy on Gentoo, install ``dev-python/numpy``. On Debian or Ubuntu,
install ``python-numpy`` or ``python3-numpy``.


License
-------

Copyright (C) 2009,2017 Israel G. Lugo <israel.lugo@lugosys.com>

ImageCmp is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

ImageCmp is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License along
with ImageCmp. If not, see <http://www.gnu.org/licenses/>.


.. |license| image:: https://img.shields.io/badge/license-GPLv3+-blue.svg?maxAge=2592000
   :target: LICENSE
.. _Pillow: https://python-pillow.org
.. _NumPy: http://www.numpy.org
