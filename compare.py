
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

# Getters for an imagedescr.QuadrantAverages quadrant. Used in findsimilar.
def _get_nw(q): return q.nw
def _get_ne(q): return q.ne
def _get_sw(q): return q.sw
def _get_se(q): return q.se
# XXX: Defining these trivial functions here is a necessary workaround, as
# multiprocessing.Pool can't copy operator.attrgetter into the child
# processes. They can't be local functions, either.


def findsimilar(filenames, tolerance):
    pool = create_worker_pool()

    try:
        img_descriptors = pool.map(imagedescr.ImageDescr, filenames)

        all_quadrants = pool.map(imagedescr.calc_quadrants, img_descriptors)

        quads_nw_promise = pool.apply_async(group_by, (all_quadrants, tolerance), {'key': _get_nw})
        quads_ne_promise = pool.apply_async(group_by, (all_quadrants, tolerance), {'key': _get_ne})
        quads_sw_promise = pool.apply_async(group_by, (all_quadrants, tolerance), {'key': _get_sw})
        quads_se_promise = pool.apply_async(group_by, (all_quadrants, tolerance), {'key': _get_se})

        quads_nw = quads_nw_promise.get()
        quads_ne = quads_ne_promise.get()
        quads_sw = quads_sw_promise.get()
        quads_se = quads_se_promise.get()

        # TODO: Finish this. Still WIP.

    finally:
        pool.terminate()
        pool.join()

    return img_descriptors, quads_nw, quads_ne, quads_sw, quads_se


def without_subranges(pairs):
    """Return a new list without intervals contained in other intervals.

    Receives an iterable of tuples (a, b), a <= b. These are interpreted as
    intervals. The returned list has only those intervals that are not
    contained within other intervals in the same iterable.

    """
    # Sort such that we're growing on a and decreasing on b:
    # [(1, 4), (1, 3), (1, 2), (1, 1), (2, 5), (2, 4), (2, 3)]
    sorted_pairs = sorted(pairs, reverse=True, key=operator.itemgetter(1))
    sorted_pairs.sort(key=operator.itemgetter(0))

    # This gives us a couple of nice invariants:
    #  - a pair contains all pairs to its right that have an equal or lower
    #    value of b
    #  - a pair to the right with a higher value of b must also have a
    #    higher value of a, which implies a new independent set (possibly
    #    overlapping the previous one)
    #
    # We just need to pick the first pair, and pairs that transition from
    # low-b to high-b. Those are the supersets.

    # Run through sorted_pairs and delete pairs that aren't low-b to high-b
    # transitions. If there are many subpairs, it will be faster to copy
    # transitions to a new list. But we're optimizing for few subpairs.
    i = 0
    while i < len(sorted_pairs)-1:
        a, b = sorted_pairs[i]

        for before_transition in range(i+1, len(sorted_pairs)):
            if sorted_pairs[before_transition][1] > b:
                before_transition -= 1
                break

        # doesn't delete anything if i+1 == before_transition+1, i.e. if
        # we're the pair before the transition
        del sorted_pairs[i+1:before_transition+1]

        # move to first non-deleted pair
        i += 1

    return sorted_pairs


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

    if key is None:
        # slower than checking with an if and not using the key, but we
        # optimize for uses with a key, as that's the case in this program
        key = lambda x: x

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
        while lo_idx < i and key(seq[lo_idx]) < minval:
            lo_idx += 1

        # find first value higher than maxval, starting from last high idx
        # (no use checking before that)
        while hi_idx < len(seq) and key(seq[hi_idx]) <= maxval:
            hi_idx += 1

        add_pair((lo_idx, hi_idx))

    if greedy:
        groups = without_subranges(groups)

    return [seq[a:b] for a, b in groups]


# vim: set expandtab smarttab shiftwidth=4 softtabstop=4 tw=75 :
