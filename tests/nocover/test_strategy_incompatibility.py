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

import math

import hypothesis.strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule
from hypothesis.searchstrategy.strategies import BadData


def order_bounds(bounds):
    if None in bounds:
        return bounds
    else:
        return sorted(bounds)

good_floats = st.floats().filter(lambda x: not math.isnan(x))

BaseStrategies = [
    st.builds(
        lambda b1, b2: st.floats(*order_bounds((b1, b2))),
        good_floats | st.none(),
        good_floats | st.none(),
    ),
    st.builds(
        lambda b1, b2: st.integers(*order_bounds((b1, b2))),
        st.integers() | st.none(),
        st.integers() | st.none(),
    ),
]


class NearlyCompatibleStrategies(RuleBasedStateMachine):
    slightly_incompatible_strategies = Bundle(
        'slightly_incompatible_strategies')

    @rule(
        # Pick a strategy (which generates strategies) and draw a tuple of
        # strategies from that.
        source=st.sampled_from(BaseStrategies).flatmap(
            lambda ss: st.tuples(ss, ss)
        ),
        target=slightly_incompatible_strategies
    )
    def test_create_base_pair(self, source):
        return source

    @rule(
        strategies=slightly_incompatible_strategies,
        random=st.randoms()
    )
    def test_try_feeding_eachother_templates(self, strategies, random):
        s1, s2 = strategies
        template1 = s1.draw_and_produce(random)
        try:
            template2 = s2.from_basic(s1.to_basic(template1))
        except BadData:
            return

        value2 = s2.reify(template2)
        assert s2.is_valid_value(template2, value2)

TestNearlyCompatibleStrategies = NearlyCompatibleStrategies.TestCase
