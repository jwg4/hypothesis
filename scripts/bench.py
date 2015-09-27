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

from random import Random
import gc
import time
from hypothesis.internal.compat import hrange, hunichr
from hypothesis import find, Settings, assume
import hypothesis.strategies as st
from hypothesis.internal.reflection import arg_string
from hypothesis.database import ExampleDatabase, SQLiteBackend
import argparse
from hypothesis.errors import NoSuchExample


benchmarks = []


def benchmark(*args, **kwargs):
    def accept(f):
        benchmarks.append((f, args, kwargs))
        return f
    return accept


@benchmark(1)
@benchmark(10)
@benchmark(50)
@benchmark(100)
@benchmark(200)
def find_unique_list(random, n):
    find(
        st.lists(st.integers(), unique_by=lambda x: x, average_size=0.9 * n),
        lambda x: True
    )


class alphabet(object):
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper

    def __repr__(self):
        return "alphabet(%d, %d)" % (self.lower, self.upper)

    def __iter__(self):
        for i in hrange(self.lower, self.upper):
            yield hunichr(i)


INTERESTING_STRATEGIES = [
    st.integers(),
    st.text(),
    st.text(alphabet=alphabet(0, 10)),
    st.text(alphabet=alphabet(1, 1024)),
    st.binary(),
    st.lists(st.integers(), min_size=100),
    st.tuples(st.integers(), st.integers()),
    st.tuples(st.integers(), st.integers(), st.integers()),
    st.tuples(st.integers(), st.integers(), st.integers(), st.integers()),
    st.integers().filter(lambda x: x % 2 == 0),
    st.integers().filter(lambda x: x % 3 == 0),
    st.integers().filter(lambda x: x % 8 == 0),
    st.integers().filter(lambda x: x % 11 == 0),
]


def strategy_benchmark(f):
    for strategy in reversed(INTERESTING_STRATEGIES):
        benchmark(strategy)(f)
    return f


@strategy_benchmark
def find_minimal(random, strategy):
    find(strategy, lambda x: True, random=random)


@strategy_benchmark
def fail_to_find(random, strategy):
    try:
        find(
            strategy, lambda x: assume(False), random=random,
            settings=Settings(
                max_examples=10, max_iterations=50, min_satisfying_examples=0)
        )
    except NoSuchExample:
        pass


@strategy_benchmark
def refind_minimal(random, strategy):
    backend = SQLiteBackend(":memory:")
    with Settings(database=ExampleDatabase(backend=backend)):
        find(strategy, lambda x: True, random=random)
        find(strategy, lambda x: True, random=random)
    backend.close()


@benchmark(1)
@benchmark(10)
@benchmark(11)
@benchmark(1000)
@benchmark(2000)
@benchmark(2001)
@benchmark(2047)
@benchmark(2048)
@benchmark(2049)
@benchmark(10 ** 7)
@benchmark(10 ** 7 - 1)
def find_integer_exceeding(random, n):
    find(st.integers(), lambda x: x > n, random=random)


def main():
    parser = argparse.ArgumentParser(
        description="Hypothesis Benchmark suite"
    )
    parser.add_argument('--name', default='')
    parser.add_argument('--runs-per-example', default=2, type=int)
    parser.add_argument('--examples', default=100, type=int)
    parser.add_argument('--build', default="/dev/null", type=str)
    cli_args = parser.parse_args()
    target = open(cli_args.build, 'w')
    random = Random(1)
    for f, args, kwargs in reversed(benchmarks):
        if cli_args.name and f.__name__ != cli_args.name:
            continue
        benchmark_name = "%s(%s)" % (
            f.__name__, arg_string(
                f, ('random',) + args, kwargs)[len("random='random', "):])
        print(benchmark_name)
        runtimes = []
        target.write('%s' % (benchmark_name,))
        for i in hrange(cli_args.examples):
            seed = random.getrandbits(128)
            gc.collect()
            start = time.time()
            for _ in hrange(cli_args.runs_per_example):
                with Settings(
                    database=None
                ):
                    f(Random(seed), *args, **kwargs)
            runtime = (time.time() - start) / cli_args.runs_per_example
            runtimes.append(runtime * 1000.0)
            target.write('\t%f' % (runtime,))
            target.flush()
        target.write('\n')
        target.flush()
    target.close()

if __name__ == '__main__':
    main()
