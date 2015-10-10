# coding=utf-8

# This file is part of Hypothesis (https://github.com/DRMacIver/hypothesis)

# Most of this work is copyright (C) 2013-2015 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# https://github.com/DRMacIver/hypothesis/blob/master/CONTRIBUTING.rst for a
# full list of people who may hold copyright, and consult the git log if you
# need to determine who owns an individual contribution.

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

# END HEADER

from __future__ import division, print_function, absolute_import

import hashlib
import collections

import marshal
from hypothesis.internal.compat import text_type, binary_type


def object_to_tracking_key(o):
    try:
        k = marshal.dumps(o)
    except ValueError:
        raise ValueError(u'unmarshallable object %r' % (o,))

    if len(k) < 20:
        return k
    else:
        return hashlib.sha1(k).digest()


class Tracker(object):

    def __init__(self, strategy):
        self.contents = set()
        self.strategy = strategy

    def __len__(self):
        return len(self.contents)

    def track(self, x):
        k = object_to_tracking_key(self.strategy.to_basic(x))
        if k in self.contents:
            return 2
        else:
            self.contents.add(k)
            return 1
