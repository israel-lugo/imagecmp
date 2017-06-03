
import numpy as np
from PIL import Image, ImageOps


# FINGERPRINT_SIZE can't be a class attribute of ImageDescr, because
# ImageDescr has a __slot__ attribute (for saving memory). Classes with
# __slot__ attributes cannot have default values on their class attributes.

# Both x and y MUST be multiples of 2. ImageDescr.calc_quadrants needs it.
FINGERPRINT_SIZE = (16, 16)
"""Size of the fingerprint thumbnail, in pixels."""

class ImageDescr(object):
    """Image descriptor."""

    __slots__ = ('filepath', 'fingerprint')

    def __init__(self, filepath):
        self.filepath = filepath
        self.fingerprint = self.calc_fingerprint(filepath)

    @staticmethod
    def calc_fingerprint(filepath):
        """Calculate an image's fingerprint."""

        im = Image.open(filepath)

        # TODO: Make sure we always convert to RGB. Image may be grayscale
        # or RGBA or something else, and we want fingerprints to be
        # standard in size and shape.

        im.draft(None, FINGERPRINT_SIZE)

        im = ImageOps.autocontrast(im, 5)
        im = im.resize(FINGERPRINT_SIZE, Image.NEAREST)

        array = np.fromstring(im.tobytes(), np.uint8)

        im.close()

        return array


class QuadrantAverages(object):
    """Quadrant averages for an image.

    This is a lightweight data container class.

    """
    __slots__ = ('imdesc', 'nw', 'ne', 'sw', 'se')

    def __init__(self, imdesc, nw, ne, sw, se):
        self.imdesc = imdesc
        self.nw = nw
        self.ne = ne
        self.sw = sw
        self.se = se


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


