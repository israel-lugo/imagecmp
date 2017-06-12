
# ImageCmp - find similar images among many
# Copyright (C) 2009,2017 Israel G. Lugo
#
# This file is part of ImageCmp.
#
# ImageCmp is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# ImageCmp is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with ImageCmp. If not, see <http://www.gnu.org/licenses/>.
#
# For suggestions, feedback or bug reports: israel.lugo@lugosys.com


"""This module implements the ImageCmp public API."""


import multiprocessing
import itertools
import functools
import operator

import imagedescr
import setops


SIMILAR_QUADS_THRESHOLD = 3
"""How many quadrants must match for two images to be considered similar."""


def create_worker_pool(worker_count=None):
    """Create a pool of worker processes.

    worker_count is the number of worker processes to create. If
    worker_count is None, the function will create as many processes as
    there are CPUs.

    """
    return multiprocessing.Pool(processes=worker_count)


def group_quadrant_n(args):
    """Group slice n of image quadrants.

    Receives a tuple (all_image_quads, tolerance, n) and returns the result
    of running setops.group_by on all_image_quads, with the specified
    tolerance, using a key that gets the n-th quadrant of each image.

    Useful for multiprocessing.Pool.map, as that function can only map
    picklable or global functions.

    """
    all_image_quads, tolerance, n = args

    return setops.group_by(all_image_quads, tolerance, key=lambda q: q.quadrants[n])


def get_grouped_quadrants(img_descriptors, tolerance, nquads_x, nquads_y, pool):
    """Calculate quadrants for the images, and group them by similarity.

    Returns four lists of grouped quadrants: (NW, NE, SW, SE). Each grouped
    quadrant is a (possibly overlapping) list of sets of similar
    QuadrantAverages within that quadrant: [{a, b, c}, {f, g, c}, ...].

    tolerance should be a numerical value between 0 and 255, specifying the
    difference in average value for two images to be considered similar.
    pool should be a multiprocessing.Pool object, for doing the processing.

    """
    # specific calc_quadrants for our nquads_x and nquads_y; needs Python
    # >= 2.7, since in earlier versions partial functions weren't picklable
    # (and pool.map needs a global or picklable function)
    calc_quadrants_xy = functools.partial(imagedescr.calc_quadrants,
                                          n_x=nquads_x, n_y=nquads_y)

    all_image_quads = pool.map(calc_quadrants_xy, img_descriptors)

    # XXX: These pool operations imply memory copies. The data is pickled
    # and sent to the worker processes. The return values will contain
    # copies of the original objects, which wastes memory. We may want to
    # add a unification pass to eliminate duplicate objects: iterate the
    # quadrants, storing each object in a set, and replacing it with the
    # instance from the set.

    quads_per_image = nquads_x * nquads_y
    grouped_quads = pool.map(group_quadrant_n, [(all_image_quads, tolerance, i) for i in range(quads_per_image)])

    return grouped_quads


def count_quadrant(image_groups):
    """Count images similar to each other, within a quadrant.

    Receives a list of QuadrantAverages groups. Returns a dictionary
    mapping ImageDescr to ImageDescr counts, e.g.:

        groups = [{a, b, c}, {a, d}]
        count_quadrant(groups)
            = {a:{b:1, c:1, d:1}, b:{a:1, c:1}, c:{a:1, b:1}, d:{a:1}}

    """
    image_counts = {}
    for group in image_groups:
        for quadavg in group:
            im = quadavg.imdesc
            if im not in image_counts:
                image_counts[im] = {}

            # add the counts from this group to the current image's counts
            d = image_counts[im]
            for other_quadavg in group:
                other_im = other_quadavg.imdesc
                if other_im != im:
                    d[other_im] = d.get(other_im, 0) + 1

    return image_counts


def get_similar_counts(quadrants, pool):
    """Count the similar images within each quadrant.

    Receives a multiprocessing.Pool and a list of quadrants. Quadrants are
    lists of ImageDescr groups. Returns a dictionary mapping images to
    image counts:

        quads = [[{a, b, c}, {a, d}], [{a, c}, {a, b}], [{a, b}], [{a, b}]]
        get_similar_counts(quads, pool)
            = {a:{b:4, c:2, d:1}, b:{a:4, c:1}, c:{a:2, b:1}, d:{a:1}}

    """
    # get a list of quadrant counts
    quadrant_counts = pool.map(count_quadrant, quadrants)

    # XXX: Pool operations imply memory copies. The data is pickled
    # and sent to the worker processes. The return values will contain
    # copies of the original objects, which wastes memory. We may want to
    # add a unification pass to eliminate duplicate objects: iterate the
    # quadrants, storing each object in a set, and replacing it with the
    # instance from the set.

    # add the quadrant counts together
    similar_counts = {}
    for quadrant_count in quadrant_counts:
        for key_im in quadrant_count:
            if key_im not in similar_counts:
                similar_counts[key_im] = {}

            d = similar_counts[key_im]
            counts = quadrant_count[key_im]
            for im in counts:
                d[im] = d.get(im, 0) + counts[im]

    return similar_counts


def get_images_by_quadrants(filenames, tolerance, pool):
    """Open the images and group them by quadrant similarity.

    Receives a list of filenames, a numeric tolerance value between 0 and
    255, and a multiprocessing.Pool object. Returns a tuple of quadrants
    (NW, NE, SW, SE). Each quadrant is a list of sets of QuadrantAverages.

    """
    img_descriptors = pool.map(imagedescr.ImageDescr, filenames)

    nw, ne, sw, se = get_grouped_quadrants(img_descriptors, tolerance, 2, 2, pool)

    return nw, ne, sw, se


def get_similar_candidates(filenames, tolerance, pool):

    # TODO: Change this to receive img_descriptors, and an amount of
    # quadrants to subdivide each image. We can then be called iteratively
    # by someone else: first with 2x2 quadrants on the entire image list;
    # then with 4x4 within each candidate group, and so on. 
    #
    # We'll probably just call get_grouped_quadrants directly here, with
    # (nquads_x, nquads_y). get_images_by_quadrants gets converted into a
    # mere get_images, that returns the ImageDescr list, and is called by
    # whomever calls us (to provide us the first imdesc list, with 2x2).
    nw, ne, sw, se = get_images_by_quadrants(filenames, tolerance, pool)

    similar_counts = get_similar_counts((nw, ne, sw, se), pool)

    candidates = set()
    for im in similar_counts:
        im_counts = similar_counts[im]
        similar_to_im = {
                other_im
                for other_im in im_counts
                if im_counts[other_im] >= SIMILAR_QUADS_THRESHOLD
            }
        if similar_to_im:
            similar_to_im.add(im)
            candidates.add(frozenset(similar_to_im))

    return candidates


def findsimilar(filenames, tolerance):
    pool = create_worker_pool()

    try:
        similar_candidates = get_similar_candidates(filenames, tolerance, pool)

    finally:
        pool.terminate()
        pool.join()

    return similar_candidates


# vim: set expandtab smarttab shiftwidth=4 softtabstop=4 tw=75 :
