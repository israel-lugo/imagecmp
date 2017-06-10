
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

    quads_nw_promise = pool.apply_async(setops.group_by, (all_quadrants, tolerance), {'key': _get_nw})
    quads_ne_promise = pool.apply_async(setops.group_by, (all_quadrants, tolerance), {'key': _get_ne})
    quads_sw_promise = pool.apply_async(setops.group_by, (all_quadrants, tolerance), {'key': _get_sw})
    quads_se_promise = pool.apply_async(setops.group_by, (all_quadrants, tolerance), {'key': _get_se})

    quads_nw = quads_nw_promise.get()
    quads_ne = quads_ne_promise.get()
    quads_sw = quads_sw_promise.get()
    quads_se = quads_se_promise.get()

    return quads_nw, quads_ne, quads_sw, quads_se



def findsimilar(filenames, tolerance):
    pool = create_worker_pool()

    try:
        img_descriptors = pool.map(imagedescr.ImageDescr, filenames)

        nw, ne, sw, se = get_grouped_quadrants(img_descriptors, tolerance, pool)

    finally:
        pool.terminate()
        pool.join()

    return img_descriptors, nw, ne, sw, se


# vim: set expandtab smarttab shiftwidth=4 softtabstop=4 tw=75 :
