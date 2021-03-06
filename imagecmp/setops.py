
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


"""This module implements operations on sets."""


import operator
import itertools



def has_supersets(x, seq):
    """Return True if x has at least one superset in seq."""
    for i in seq:
        if x.issubset(i):
            return True

    return False


def without_subsets(seq):
    """Return a new set without sets contained in other sets."""
    sorted_by_len = sorted(seq, key=len)

    return {x for i, x in enumerate(sorted_by_len) if not has_supersets(x, itertools.islice(sorted_by_len, i+1, None))}


def without_pair_subsets(pairs):
    """Return a new list without intervals contained in other intervals.

    Receives an iterable of tuples (a, b), a <= b. These are interpreted as
    intervals. The returned list has only those intervals that are not
    contained within other intervals in the same iterable.

    The new list may be in a different order from the input.

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


def group_by(seq, tolerance, no_singles=False, key=None):
    """Group the values of a numerical sequence by a certain tolerance.

    Returns a list of slices from the original sequence, possibly
    overlapping, where in each slice all the values are within (n -
    tolerance <= n <= n + tolerance). The ordering of the list of slices is
    arbitrary.

    If no_singles is True, groups with a single item will be discarded.

    key, if provided and not None, is a function to be applied to each
    element of the sequence, to obtain a numerical comparison key.

    """
    # we use a list of index pairs, and build the groups in the end
    groups = []

    if key is None:
        # slower than checking with an if and not using the key, but we
        # optimize for uses with a key, as that's the case in this program
        key = lambda x: x

    lo_idx = 0
    hi_idx = 0

    sorted_seq = sorted(seq, key=key)

    for i, val in enumerate(sorted_seq):
        group = []
        if key is not None:
            val = key(val)

        minval = val - tolerance
        maxval = val + tolerance

        # skip lower than minval, starting from last low idx
        # (no use going back before that)
        while lo_idx < i and key(sorted_seq[lo_idx]) < minval:
            lo_idx += 1

        # find first value higher than maxval, starting from last high idx
        # (no use checking before that)
        while hi_idx < len(sorted_seq) and key(sorted_seq[hi_idx]) <= maxval:
            hi_idx += 1

        # discard unitary pairs if requested (note hi_idx is not inclusive)
        if hi_idx > lo_idx+1 or not no_singles:
            groups.append((lo_idx, hi_idx))

    groups = without_pair_subsets(groups)

    return [sorted_seq[a:b] for a, b in groups]



