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

"""
Script for comparing output from who bench.py runs.

Basic concept:

    Each benchmark has been run on the same number of examples in each version.
    We compare those examples using a one sided simulated permutation test.
    We then run the Benjamini Hochberg procedure to compare all the benchmarks
    with a false discovery rate of 0.01

Is this statistically sound? ¯\_(ツ)_/¯

It seems to work though.
"""

import sys
from random import Random
from fractions import Fraction
from collections import OrderedDict


def mean(ls):
    return float(sum(Fraction(*l.as_integer_ratio()) for l in ls) / len(ls))


def parse_file(f):
    results = OrderedDict()
    for line in open(f):
        bits = line.strip().split("\t")
        results[bits[0]] = list(map(float, bits[1:]))
    return results


def main():
    _, established, new = sys.argv
    established = parse_file(established)
    new = parse_file(new)

    if set(established.keys()) != set(new.keys()):
        print("Benchmarks differ")
        new_keys = set(new.keys()) - set(established.keys())
        if new_keys:
            print("Additional benchmarks in new:", ', '.join(new_keys))
        missing_keys = set(established.keys()) - set(new.keys())
        if missing_keys:
            print("Missing benchmarks in new:", ', '.join(missing_keys))
        sys.exit(1)
    benchmarks = list(established)
    for benchmark in benchmarks:
        if len(new[benchmark]) != len(established[benchmark]):
            print(
                "Number of examples for benchmark %s differ: %d vs %d" % (
                    benchmark,
                    len(established[benchmark]), len(new[benchmark])))
            sys.exit(1)

    results = []
    random = Random(1)
    for k in benchmarks:
        established_values = established[k]
        new_values = new[k]
        n = len(established_values)
        assert len(new_values) == n
        threshold = mean(established_values) - mean(
            new_values
        )
        counter = 0
        runs = 2000
        for _ in range(runs):
            values = established_values + new_values
            random.shuffle(values)
            if (
                mean(values[:n]) - mean(values[n:]) <=
                threshold
            ):
                counter += 1
        p = (1.0 + counter) / (1.0 + runs)
        results.append((p, k))
        print("%s: p=%.4f" % (k, p))
    results.sort()
    desired_fdr = 0.01
    k = 0
    for i, (p, _) in enumerate(results, 1):
        if p <= i / len(results) * desired_fdr:
            k = i
    if k > 0:
        print("The following benchmarks exhibit regressions:")
        print()
        for p, b in results[:k]:
            print("    %s: %f vs %f (p=%f)" % (
                b,
                mean(established[b]), mean(new[b]), p))
        sys.exit(1)
    else:
        print(
            "No detectable performance regressions at desired FDR of %f" % (
                desired_fdr,))
        sys.exit(0)

if __name__ == '__main__':
    main()
