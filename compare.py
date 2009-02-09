#!/usr/bin/env python

import imagearray

def compare_images(filename1, filename2, resolution=(4,4)):
    """Compare two images and return the difference between them.

    The images are compared by quadrants, using the specified resolution.
    The returned value is the average difference in color values between
    corresponding quadrants in each image. It is expressed in a percentage
    over 255 (which is the highest possible difference, e.g. from black to
    white). A value of 0 means both images are equal (at the given
    resolution). A value of 100 means both images are completely different
    (one's black, the other's white).

    """
    array1 = imagearray.array_from_image(filename1, resolution)
    array2 = imagearray.array_from_image(filename2, resolution)

    difference = imagearray.mean_distance(array1, array2)

    assert 0 <= difference <= 255

    return (difference * 100) / 255


if __name__ == '__main__':
    import sys

    resolution = (4, 4)

    if len(sys.argv) < 3:
        print >>sys.stderr, 'Usage: %s <filename1> <filename2> [<resolution_x> <resolution_y>]' % sys.argv[0]
        sys.exit(1)

    filename1, filename2 = sys.argv[1:3]

    if len(sys.argv) >= 5:
        resolution = (int(sys.argv[3]), int(sys.argv[4]))

    print '%f %%' % (100 - compare_images(filename1, filename2, resolution))
