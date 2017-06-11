
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
    __slots__ = ('_imdesc', '_nw', '_ne', '_sw', '_se')

    def __init__(self, imdesc, nw, ne, sw, se):
        self._imdesc = imdesc
        self._nw = nw
        self._ne = ne
        self._sw = sw
        self._se = se

    @property
    def imdesc(self): return self._imdesc

    @property
    def nw(self): return self._nw

    @property
    def ne(self): return self._ne

    @property
    def sw(self): return self._sw

    @property
    def se(self): return self._se

    def __eq__(self, other):
        """Compare with another QuadrantAverages."""
        return (self._imdesc == other._imdesc
                and self._nw == other._nw
                and self._ne == other._ne
                and self._sw == other._sw
                and self._se == other._se)

    def __hash__(self):
        """Return hash(self)."""
        return hash((self._imdesc, self._nw, self._ne, self._sw, self._se))



def calc_quadrants(imdesc):
    """Calculate quadrant averages.

    Reshapes the fingerprint back into the original shape of the image,
    and divides it into quadrants. Calculates the average value of each
    quadrant, and returns them as a tuple, left-right, top-down:
    (nw_avg, ne_avg, se_avg, sw_avg).

    """
    x = FINGERPRINT_SIZE[0]
    pixel_cols = FINGERPRINT_SIZE[1]

    # each pixel in a line is actually 3 values: (R, G, B)
    y = pixel_cols*3

    assert imdesc.fingerprint.size == x * y

    # reshape into a 2D rectangle of pixel values
    rect = imdesc.fingerprint.reshape(x, y)

    assert x % 2 == 0 and y % 2 == 0
    half_x = x/2
    half_y = y/2

    north_west = rect[0:half_x, 0:half_y]
    north_east = rect[0:half_x, half_y:y]
    south_west = rect[half_x:x, 0:half_y]
    south_east = rect[half_x:x, half_y:y]

    nw_avg = north_west.mean()
    ne_avg = north_east.mean()
    sw_avg = south_west.mean()
    se_avg = south_east.mean()

    return QuadrantAverages(imdesc, nw_avg, ne_avg, sw_avg, se_avg)


