
import numpy as np
from PIL import Image, ImageOps


# FINGERPRINT_SIZE can't be a class attribute of ImageDescr, because
# ImageDescr has a __slot__ attribute (for saving memory). Classes with
# __slot__ attributes cannot have default values on their class attributes.

# Both x and y MUST be multiples of 2. ImageDescr.calc_quadrants needs it.
FINGERPRINT_SIZE = (16, 16)
"""Size of the fingerprint thumbnail, in pixels."""

class ImageDescr(object):
    """Image descriptor.

    This is a lightweight read-only data container class.

    """

    __slots__ = ('_filepath', '_fingerprint')

    def __init__(self, filepath):
        self._filepath = filepath
        self._fingerprint = self._calc_fingerprint(filepath)

    @property
    def filepath(self):
        """Get the image's file path."""
        return self._filepath

    @property
    def fingerprint(self):
        """Get the image's fingerprint."""
        return self._fingerprint

    def __eq__(self, other):
        """Compare with another ImageDescr.

        Two ImageDescr are considered the same iif their filepath is the
        same.

        """
        return self._filepath == other._filepath

    def __hash__(self):
        """Return hash(self.filepath)."""
        return hash(self._filepath)

    @staticmethod
    def _calc_fingerprint(filepath):
        """Calculate an image's fingerprint."""

        im = Image.open(filepath)

        # TODO: Make sure we always convert to RGB. Image may be grayscale
        # or RGBA or something else, and we want fingerprints to be
        # standard in size and shape.

        im.draft(None, FINGERPRINT_SIZE)

        im = ImageOps.autocontrast(im, 5)
        im = im.resize(FINGERPRINT_SIZE, Image.NEAREST)

        array = np.fromstring(im.tobytes(), np.uint8)
        array.setflags(write=False)

        im.close()

        return array


class QuadrantAverages(object):
    """Quadrant averages for an image.

    This is a lightweight read-only data container class.

    """
    __slots__ = ('_imdesc', '_quadrants')

    def __init__(self, imdesc, quadrants):
        self._imdesc = imdesc
        self._quadrants = quadrants

    @property
    def imdesc(self): return self._imdesc

    @property
    def quadrants(self): return self._quadrants

    def __eq__(self, other):
        """Compare with another QuadrantAverages."""
        return (self._imdesc == other._imdesc
                and self._quadrants == self._quadrants)

    def __hash__(self):
        """Return hash(self)."""
        return hash((self._imdesc, self._quadrants))


def calc_quadrants(imdesc, n_x, n_y):
    """Calculate quadrant averages, for an arbitrary number of quadrants.

    Receives the ImageDescr, the number of quadrants along the x axis, and
    the number of quadrants along the y axis. Reshapes the image's
    fingerprint into a thumbnail of the image, and divides it into
    quadrants as specified.
    
    Returns a QuadrantAverages object.

    The number of quadrants must be an even divisor of the ImageDescr's
    fingerprint size along its respective axis.

    """
    x = FINGERPRINT_SIZE[0]
    pixel_cols = FINGERPRINT_SIZE[1]

    y = pixel_cols*3

    assert imdesc.fingerprint.size == x * y

    quad_x, rem_x = divmod(x, n_x)
    quad_y, rem_y = divmod(y, n_y)

    if (rem_x != 0):
        raise ValueError("thumbnail x (%d) does not evenly divide by n_x (%d)"
                         % (x, n_x))
    if (rem_y != 0):
        raise ValueError("thumbnail y (%d) does not evenly divide by n_y (%d)"
                         % (y, n_y))

    # reshape into a 2D rectangle of pixel values
    rect = imdesc.fingerprint.reshape(x, y)

    quadrants = tuple(rect[i:i+quad_x, j:j+quad_y].mean()
                        for i in range(0, x, quad_x)
                        for j in range(0, y, quad_y))

    return QuadrantAverages(imdesc, quadrants)
