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

import pytest
import hypothesis.strategies as st
from hypothesis import Settings, find, given, assume


def knapsack1(items, capacity):
    items = list(items)
    items.sort(key=lambda x: x[0] / x[1], reverse=True)
    result = []
    current_fill = 0
    for item in items:
        if item[1] + current_fill <= capacity:
            result.append(item)
            current_fill += item[1]
    return result


def knapsack2(items, capacity):
    items = list(items)
    items.sort(key=lambda x: x[1])
    items.sort(key=lambda x: x[0], reverse=True)
    result = []
    current_fill = 0
    for item in items:
        if item[1] + current_fill <= capacity:
            result.append(item)
            current_fill += item[1]
    return result


def score_solution(solution):
    """Return the total value of a solution to the knapsack problem."""
    return sum(item[0] for item in solution)


# This will be the types of data that we want to feed to our algorithm to
# test it: Our items are tuples of positive integers, and our capacities
# are integers.
Item = st.tuples(st.integers(min_value=1), st.integers(min_value=1))
ItemSet = st.lists(Item)
Capacity = st.integers(min_value=1)


def increasing_score_of_chosen_item_does_not_improve_things(
    solve_knapsack, items, capacity
):
    assume(any(item[1] <= capacity for item in items))
    result = solve_knapsack(items, capacity)
    for item in result:
        new_items = list(items)
        new_items.append((item[0] + 1, item[1]))
        new_result = solve_knapsack(new_items, capacity)
        if score_solution(new_result) <= score_solution(result):
            return True
    return False


def increasing_weight_of_chosen_item_improves_things(
    solve_knapsack, items, capacity
):
    assume(any(item[1] <= capacity for item in items))
    result = solve_knapsack(items, capacity)
    assert result
    for item in result:
        new_items = list(items)
        new_items.remove(item)
        new_items.append((item[0], item[1] + 1))
        new_result = solve_knapsack(new_items, capacity)
        if score_solution(new_result) > score_solution(result):
            return True
    return False


def removing_a_chosen_item_improves_matters(
    solve_knapsack, items, capacity
):
    result = solve_knapsack(items, capacity)
    score = score_solution(result)
    for item in result:
        new_items = list(items)
        new_items.remove(item)
        new_result = solve_knapsack(new_items, capacity)
        if score_solution(new_result) < score:
            return True
    return False


conditions = [
    increasing_score_of_chosen_item_does_not_improve_things,
    increasing_weight_of_chosen_item_improves_things,
    removing_a_chosen_item_improves_matters,
]

solvers = [
    knapsack1, knapsack2
]


params = [
    (c, s)
    for c in conditions
    for s in solvers
]


@pytest.mark.parametrize(
    ('condition', 'solve_knapsack'),
    params,
    ids=['%s, %s' % (c.__name__, s.__name__) for c, s in params])
@given(st.randoms(), settings=Settings(
    max_examples=5, max_shrinks=0
))
def test_can_find_pretty_good_knapsack_conditions(
    condition, solve_knapsack, random
):
    items, capacity = find(
        st.tuples(ItemSet, Capacity), lambda t: condition(solve_knapsack, *t),
        random=random, settings=Settings(
            database=None,
            max_examples=200,
            max_shrinks=1000,
            timeout=10,
        )
    )
    assert len(items) <= 10
