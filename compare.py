
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
import itertools

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


def without_subranges(pairs):
    """Iterator that yields intervals not contained in other intervals.

    Receives an iterable of tuples (a, b), a <= b. These are interpreted as
    intervals. The returned iterator yields those intervals that are not
    contained within other intervals in the same iterable.

    WARNING: The current implementation for this function takes O(N**2)
    time, so it should not be used with very large iterables.

    """
    mask = itertools.repeat(True)

    # TODO: If we move to require that the input must be sorted, we can
    # optimize this. No pair may contain a pair with a smaller a... That
    # means we can skip checking pairs with lower a's.

    for (a, b) in pairs:
        not_subpairs = (p0 < a or p1 > b or (p0 == a and p1 == b) for p0, p1 in pairs)

        # Use a list here instead of a generator, to avoid chaining an
        # arbitrarily large number of generators; bools are very small (a
        # 1M bool list takes ~8MiB in Python 3.4). As a bonus, expanding
        # our returned iterable will take O(1).
        mask = [m and ns for m, ns in zip(mask, not_subpairs)]

    return itertools.compress(pairs, mask)


def group_by(seq, tolerance, unique=True, greedy=True, key=None):
    """Group the values of a numerical sequence by a certain tolerance.

    The sequence MUST be sorted. Returns a list of slices from the original
    sequence, possibly overlapping, where in each slice all the values are
    within (n - tolerance <= n <= n + tolerance). The ordering of the list
    of slices is arbitrary.

    If unique is True, duplicate groups will be discarded. If greedy is
    True, subgroups of larger groups will be discarded.

    key, if provided and not None, is a function to be applied to each
    element of the sequence, to obtain a numerical comparison key.

    """
    # we use a set or list of index pairs, and build the groups in the end
    if unique:
        groups = set()
        add_pair = groups.add
    else:
        groups = []
        add_pair = groups.append

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

        add_pair((lo_idx, hi_idx))

    if greedy:
        groups = without_subranges(groups)

    return [seq[a:b] for a, b in groups]


# vim: set expandtab smarttab shiftwidth=4 softtabstop=4 tw=75 :
