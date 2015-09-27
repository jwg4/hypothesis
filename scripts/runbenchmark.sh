#!/bin/bash

set -x -e

RELEASED=$(mktemp)
LOCAL=$(mktemp)

pip install virtualenv
rm -rf released-hypothesis
python -m virtualenv released-hypothesis
. released-hypothesis/bin/activate
pip install hypothesis --upgrade
python scripts/bench.py --build=$RELEASED
deactivate

PYTHONPATH=src python scripts/bench.py --build=$LOCAL

python scripts/benchcompare.py $RELEASED $LOCAL
