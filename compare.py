
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
import operator

import imagedescr


def create_worker_pool(worker_count=None):
    """Create a pool of worker processes.

    worker_count is the number of worker processes to create. If
    worker_count is None, the function will create as many processes as
    there are CPUs.

    """
    return multiprocessing.Pool(processes=worker_count)


def findsimilar(filenames):
    pool = create_worker_pool()

    try:
        img_descriptors = pool.map(imagedescr.ImageDescr, filenames)

        all_quadrants = pool.map(imagedescr.calc_quadrants, img_descriptors)

        quads_nw = sorted(all_quadrants, key=operator.attrgetter("nw"))
        quads_ne = sorted(all_quadrants, key=operator.attrgetter("ne"))
        quads_sw = sorted(all_quadrants, key=operator.attrgetter("sw"))
        quads_se = sorted(all_quadrants, key=operator.attrgetter("se"))

        # TODO: Finish this. Still WIP.

    finally:
        pool.terminate()
        pool.join()

    return img_descriptors, quads_nw, quads_ne, quads_sw, quads_se


def group_by(seq, tolerance, key=None):
    """Group the values of a numerical sequence by a certain tolerance.

    The sequence MUST be sorted. Returns a list of slices from the original
    sequence, possibly overlapping, where in each slice all the values are
    within (n - tolerance <= n <= n + tolerance).

    key, if provided and not None, is a function to be applied to each
    element of the sequence, to obtain a numerical comparison key.

    """
    groups = []

    lo_idx = 0
    hi_idx = 0

    for i, val in enumerate(seq):
        group = []
        if key is not None:
            val = key(val)

        minval = val - tolerance
        maxval = val + tolerance

        # skip lower than minval, starting from last low idx
        # (no use going back before that)
        while lo_idx < i and seq[lo_idx] < minval:
            lo_idx += 1

        # find first value higher than maxval, starting from last high idx
        # (no use checking before that)
        while hi_idx < len(seq) and seq[hi_idx] <= maxval:
            hi_idx += 1

        groups.append(seq[lo_idx:hi_idx])

    return groups


# vim: set expandtab smarttab shiftwidth=4 softtabstop=4 tw=75 :
