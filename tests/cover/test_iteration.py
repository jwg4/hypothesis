# coding=utf-8

# This file is part of Hypothesis (https://github.com/DRMacIver/hypothesis)

# Most of this work is copyright (C) 2013-2015 David R. MacIver
# (david@drmaciver.com), but it contains contributions by other. See
# https://github.com/DRMacIver/hypothesis/blob/master/CONTRIBUTING.rst for a
# full list of people who may hold copyright, and consult the git log if you
# need to determine who owns an individual contribution.

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

# END HEADER

from __future__ import division, print_function, absolute_import, \
    unicode_literals

from itertools import count, islice, repeat, product

import hypothesis.strategies as st
import hypothesis.internal.iteration as ite
from hypothesis import given


@given(st.lists(st.lists(st.integers(), average_size=10), average_size=5))
def test_interleaving_gives_a_permutation_of_values(lols):
    interleaved = list(ite.interleave(map(iter, lols)))
    original = sum(lols, [])
    assert sorted(interleaved) == sorted(original)


@given(
    st.streaming(st.booleans()),
    st.streaming(st.integers(min_value=2, max_value=10))
)
def test_interleaving_mixes(integers, strings):
    interleaved = list(islice(
        ite.interleave((iter(integers), iter(strings))), 10))
    assert any(isinstance(x, bool) for x in interleaved)
    assert any(isinstance(x, int) for x in interleaved)


@given(st.lists(st.lists(st.integers(), average_size=10), average_size=5))
def test_staging_gives_a_permutation_of_values(lols):
    staged = list(ite.stage(iter(map(iter, lols))))
    original = sum(lols, [])
    assert sorted(staged) == sorted(original)


def test_staging_brings_in_values_incrementally():
    repeated_counting = (
        repeat(i) for i in count()
    )

    first_100 = list(islice(
        ite.stage(repeated_counting), 100
    ))
    assert 7 in first_100


@given(st.lists(st.lists(st.integers(), max_size=5), max_size=3))
def test_product_gives_same_values_in_different_order(lols):
    itertools_result = list(product(*map(iter, lols)))
    our_result = list(ite.product(map(iter, lols)))
    assert sorted(itertools_result) == sorted(our_result)


def test_product_yields_secondary_values_early():
    ps = list(islice(ite.product((count(), count())), 10))
    assert any(p[1] > 0 for p in ps)


def test_draw_from_empty_is_empty():
    assert list(ite.drawn_from(iter(()))) == []


def test_product_of_empty_is_empty():
    assert list(ite.product((count(), iter(())))) == []
