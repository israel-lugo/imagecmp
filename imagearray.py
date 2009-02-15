
# $Id$

import Image
import numpy


def array_from_image(input_file, resample_size=None, data_type=numpy.int16):
    """Return a NumPy array of an image's RGB values.

    input_file may be a string containing the path to the image, or a file
    object (opened for reading in binary mode).

    The image is converted to RGB first if necessary. Then it is converted
    to a flat (unidimensional) array in the form (R1, G1, B1, R2, G2, B2,
    ... , Rn, Gn, Bn). If resample_size is given, it should be a tuple (x,
    y). In this case, the image will be resized to the specified dimensions
    before converting it to an array. The array will therefore be of length
    x*y.

    The array is converted to the specified data_type, which can be any
    numpy data type or one of the python data type objects int, float or
    complex. By default the array is converted to numpy.int16, so that you
    can do math on it without overflowing (e.g. subtracting two arrays).

    """
    im = Image.open(input_file, 'r')

    # convert the image to RGB (instead of e.g. palette)
    if im.mode != 'RGB':
        im = im.convert('RGB')

    if resample_size is not None:
        im = im.resize(resample_size, Image.ANTIALIAS)

    array = numpy.fromstring(im.tostring(), numpy.uint8)

    if data_type != numpy.uint8:
        array = array.astype(data_type)

    return array



def mean_distance(array1, array2):
    """Calculate the average distance between elements of 2 NumPy arrays.

    Both arrays must be of the same size and shape (dimensions). The
    function calculates the absolute difference between the corresponding
    elements of each array, and then returns the average value.

    """
    difference_list = abs(array1 - array2)

    return difference_list.mean()
