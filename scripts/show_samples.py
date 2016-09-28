#! /usr/bin/env python

import sys

from miniutils import get_sample_datasets

if len(sys.argv) < 2:
    print 'usage: show_samples.py [sample-name] [version]'
    sys.exit(1)

sample = sys.argv[1]

version = None
if len(sys.argv) > 2:
    version = sys.argv[2]


datasets = get_sample_datasets(sample, version)

for ds in datasets:
    print ds['path']

