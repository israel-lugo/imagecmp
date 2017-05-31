
import numpy as np
from PIL import Image, ImageOps


# FINGERPRINT_SIZE can't be a class attribute of ImageDescr, because
# ImageDescr has a __slot__ attribute (for saving memory). Classes with
# __slot__ attributes cannot have default values on their class attributes.

FINGERPRINT_SIZE = (16, 16)
"""Size of the fingerprint thumbnail, in pixels."""

class ImageDescr(object):
    """Image descriptor."""

    __slots__ = ('filepath', 'fingerprint')

    def __init__(self, filepath, fingerprint):
        self.filepath = filepath
        self.fingerprint = fingerprint

    @classmethod
    def from_file(cls, filepath):
        """Create an ImageDescr from an image file."""
        fingerprint = cls.calc_fingerprint(filepath)

        return cls(filepath, fingerprint)

    @staticmethod
    def calc_fingerprint(filepath):
        """Calculate an image's fingerprint."""

        im = Image.open(filepath)

        im.draft(None, FINGERPRINT_SIZE)

        im = im.resize(FINGERPRINT_SIZE, Image.BICUBIC)
        im = ImageOps.autocontrast(im, 5)

        array = np.fromstring(im.tobytes(), np.uint8)

        im.close()

        return array
