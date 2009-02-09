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
