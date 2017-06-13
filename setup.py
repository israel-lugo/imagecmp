
"""Package information for imagecmp."""

import os.path
import io

from setuptools import setup

from imagecmp.version import __version__


def read(file_path_components, encoding="utf8"):
    """Read the contents of a file.

    Receives a list of path components to the file and joins them in an
    OS-agnostic way. Opens the file for reading using the specified
    encoding, and returns the file's contents.

    Works both in Python 2 and Python 3.

    """
    with io.open(
        os.path.join(os.path.dirname(__file__), *file_path_components),
        encoding=encoding
    ) as fp:
        return fp.read()


setup(
    name='imagecmp',
    description='Find similar images among many',
    author="Israel G. Lugo",
    author_email='israel.lugo@lugosys.com',
    url='https://gitlab.lugosys.com/capi/imagecmp',
    version=__version__,
    packages=['imagecmp',],
    install_requires=[ 'numpy>=1.8', 'Pillow>=2.6' ],
    license='GPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: System :: Filesystems',
    ],
    long_description=read(['README.rst']),
)
