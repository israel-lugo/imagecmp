
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


"""Unit tests for setops module.

setops.group_by is tested in a separate unit.

"""


import pytest

import imagecmp.setops as setops


# Test data for test_has_supersets: (set, sequence, expected)
has_supersets_data = [
    (set(), [], False),
    (set(), [set()], True),
    ({1}, [{1}], True),
    (set(), [{1, 2, 3}], True),
    ({1}, [{0}, {1, 2, 3}], True),
    ({5}, [{0}, {1, 2, 3}], False),
    ({1, 2, 3}, [{5}, {1, 2, 3}, {3}], True),
    ({1, 2, 3}, [{5}, {1, 2, 4}, {3}], False),
]

without_subsets_data = [
    (set(), set()),
    ( {frozenset({1})}, {frozenset({1})}),
    (
        [frozenset({1})] * 3,
        {frozenset({1})}
    ),
    (
        {frozenset(list(range(10))), frozenset(list(range(0,10,2)))},
        {frozenset(list(range(10)))}
    ),
    (
        {frozenset(list(range(10))), frozenset(list(range(0,10,2))), frozenset({"foo", "bar"})},
        {frozenset(list(range(10))), frozenset({"foo", "bar"})}
    ),
    (
        {frozenset(list(range(10))), frozenset({"foo", "bar"}), frozenset({"foo"})},
        {frozenset(list(range(10))), frozenset({"foo", "bar"})}
    ),
]


without_pair_subsets_data = [
    ([], []),
    ( [(0, 0)], [(0, 0)]),
    ( [(0, 1)], [(0, 1)]),
    (
        [(0, 1), (0, 1), (0, 1)],
        [(0, 1)]
    ),
    (
        [(0, 1), (1, 2)],
        [(0, 1), (1, 2)]
    ),
    (
        [(-2, -1)],
        [(-2, -1)]
    ),
    (
        [(4, 50), (45, 51), (45, 50)],
        [(4, 50), (45, 51)]
    ),
    (
        [(0, 2), (0, 0), (2, 2), (0, 1), (1, 2)],
        [(0, 2)]
    ),
    (
        [(0, 1), (0, 0), (2, 2), (0, 2), (1, 2)],
        [(0, 2)]
    ),
    (
        [(0, 1), (0, 2)],
        [(0, 2)]
    ),
    (
        [(99, 101), (10, 100), (20, 21)],
        [(10, 100), (99, 101)]
    ),
    (
        [(3, 3), (2, 10), (2, 10), (-5, 10), (10, 10), (300, 304), (-5, 10)],
        [(-5, 10), (300, 304)]
    ),
]


@pytest.mark.parametrize("x, seq, expected", has_supersets_data)
def test_has_supersets(x, seq, expected):
    """has_supersets(x, seq) = expected"""
    result = setops.has_supersets(x, seq)

    assert result == expected


@pytest.mark.parametrize("seq, expected", without_subsets_data)
def test_without_subsets(seq, expected):
    """without_subsets(seq) = expected"""
    result = setops.without_subsets(seq)

    assert result == expected


@pytest.mark.parametrize("pairs, expected", without_pair_subsets_data)
def test_without_pair_subsets(pairs, expected):
    """without_pair_subsets(pairs) = expected"""
    result = setops.without_pair_subsets(pairs)

    # without_pair_subsets makes no promises about the order of its output
    assert sorted(result) == sorted(expected)

