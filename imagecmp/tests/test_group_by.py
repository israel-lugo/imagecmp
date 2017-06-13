
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


"""Unit tests for setops.group_by."""


import pytest

import imagecmp.setops as setops


group_by_numeric_data = [
    ([1], 0),
    ([1], 1),
    ([1, 2], 0),
    ([1, 2], 1),
    ([1, 2, 2, 2, 2, 2, 2, 2, 2, 2], 10),
    ([-3, 1, 2], 10),
    ([-50, 3, 4, 5, 6, 50, 51, 52], 4),
    (list(range(10)), 5),
    (list(range(10)), 6),
    (list(range(100)), 10),
    (list(range(-100,100,2)), 3),
]


@pytest.mark.parametrize("seq, tolerance", group_by_numeric_data)
def test_group_by_bounds(seq, tolerance):
    """group_by(seq, t) = x, for g in x, max(g) - min(g) <= t*2"""
    groups = setops.group_by(seq, tolerance)

    for group in groups:
        assert max(group) - min(group) <= tolerance*2


@pytest.mark.parametrize("seq, tolerance", group_by_numeric_data)
def test_group_by_lossless(seq, tolerance):
    """Make sure all items in seq are in the output, and vice-versa."""
    groups = setops.group_by(seq, tolerance)

    # all returned items are contained in seq
    for group in groups:
        for i in group:
            assert i in seq

    joined = sum(groups, [])

    # all of seq's items are contained in groups
    for i in seq:
        assert i in joined

