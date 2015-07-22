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

from itertools import count

from hypothesis.types import Stream
from hypothesis.internal.compat import hrange


def interleave(iterators):
    iterators = list(iterators)
    while any(it is not None for it in iterators):
        while iterators[-1] is None:
            iterators.pop()
        for i in hrange(len(iterators)):
            it = iterators[i]
            if it is None:
                continue
            try:
                yield next(it)
            except StopIteration:
                iterators[i] = None


def stage(iterator_of_iterators):
    iterators = []
    try:
        iterators.append(next(iterator_of_iterators))
    except StopIteration:
        return
    done = False
    while any(it is not None for it in iterators) or not done:
        while iterators[-1] is None:
            iterators.pop()
        for i in hrange(len(iterators)):
            it = iterators[i]
            if it is None:
                continue
            try:
                yield next(it)
            except StopIteration:
                if i == len(iterators) - 1:
                    iterators.pop()
                else:
                    iterators[i] = None
        if not done:
            try:
                iterators.append(next(iterator_of_iterators))
            except StopIteration:
                done = True


def product_from_streams(streams):
    for s in streams:
        try:
            s[0]
        except IndexError:
            return
    if len(streams) == 0:
        yield ()
        return
    else:
        rest = streams[1:]

        def iter_with(v):
            for p in product_from_streams(rest):
                yield (v,) + p

        for p in stage(
            iter_with(v)
            for v in streams[0]
        ):
            yield p


def product(n_iterators):
    return product_from_streams(
        tuple(map(Stream, n_iterators))
    )


def drawn_from(iterator, min_size=None, max_size=None):
    min_size = min_size or 0
    if max_size is None:
        indices = count(min_size)
    else:
        indices = hrange(min_size, max_size + 1)
    stream = Stream(iterator)
    try:
        stream[0]
    except IndexError:
        return iter(())
    return stage(
        product_from_streams((stream,) * i)
        for i in indices
    )
