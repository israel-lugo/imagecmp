
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

# Getters for an imagedescr.QuadrantAverages quadrant. Used in findsimilar.
def _get_nw(q): return q.nw
def _get_ne(q): return q.ne
def _get_sw(q): return q.sw
def _get_se(q): return q.se
# XXX: Defining these trivial functions here is a necessary workaround, as
# multiprocessing.Pool can't copy operator.attrgetter into the child
# processes. They can't be local functions, either.



def get_grouped_quadrants(img_descriptors, tolerance, pool):
    """Calculate quadrants for the images, and group them by similarity.

    Returns four lists of grouped quadrants: (NW, NE, SW, SE). Each grouped
    quadrant is a (possibly overlapping) list of sets of similar
    QuadrantAverages within that quadrant: [{a, b, c}, {f, g, c}, ...].

    tolerance should be a numerical value between 0 and 255, specifying the
    difference in average value for two images to be considered similar.
    pool should be a multiprocessing.Pool object, for doing the processing.

    """
    all_quadrants = pool.map(imagedescr.calc_quadrants, img_descriptors)

    # XXX: These pool operations imply memory copies. The data is pickled
    # and sent to the worker processes. The return values will contain
    # copies of the original objects, which wastes memory. We may want to
    # add a unification pass to eliminate duplicate objects: iterate the
    # quadrants, storing each object in a set, and replacing it with the
    # instance from the set.

    quads_nw_promise = pool.apply_async(setops.group_by, (all_quadrants, tolerance), {'key': _get_nw})
    quads_ne_promise = pool.apply_async(setops.group_by, (all_quadrants, tolerance), {'key': _get_ne})
    quads_sw_promise = pool.apply_async(setops.group_by, (all_quadrants, tolerance), {'key': _get_sw})
    quads_se_promise = pool.apply_async(setops.group_by, (all_quadrants, tolerance), {'key': _get_se})

    quads_nw = quads_nw_promise.get()
    quads_ne = quads_ne_promise.get()
    quads_sw = quads_sw_promise.get()
    quads_se = quads_se_promise.get()

    return quads_nw, quads_ne, quads_sw, quads_se


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

    nw, ne, sw, se = get_grouped_quadrants(img_descriptors, tolerance, pool)

    return nw, ne, sw, se


def get_similar_candidates(filenames, tolerance, pool):
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
