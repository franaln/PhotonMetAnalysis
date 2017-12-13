#!/usr/bin/env python

import os
import re
import sys
import json
import fnmatch
import ROOT
from collections import OrderedDict

if len(sys.argv) < 3:
    print 'usage: merge_ul.py output_file input_dir1 input_dir2 ...'
    sys.exit(1)

input_dirs = sys.argv[2:]
output_file = sys.argv[1]


all_files = []
for input_dir in input_dirs:
    for root, dirnames, filenames in os.walk(input_dir):
        for filename in fnmatch.filter(filenames, 'Output_upperlimit.root'):

            path = os.path.join(root, filename)            

            # check root file
            try:                                                                                                                                                                                                                            
                fin = ROOT.TFile.Open(path)
                if fin.IsZombie():
                    print('skipping file: %s' % path)
                    fin.Close()
                    continue
            except ReferenceError:
                print('skipping file: %s' % path)
                continue

            all_files.append(path)

# Get all available points
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

all_points = []
for path in all_files:

    infile = ROOT.TFile.Open(path)

    try:
        content = [ key.GetName() for key in infile.GetListOfKeys() ]
    except:
        continue

    for name in content:
        if not name.startswith('hypo'): ## or nor name.startswith('fitTo'):
            continue
        all_points.append(name.replace('hypo_', ''))

        infile.Close()

all_points = list(set(all_points))
all_points.sort(key=natural_keys)


# Loop over points, merge them and save upper limit
ul_dict = OrderedDict()

for point in all_points:

    print 'Merging point: %s' % point

    name = 'hypo_%s' % point

    merge_hypotest = None

    for path in all_files:
        infile = ROOT.TFile.Open(path)
        try:
            hypotest = infile.Get(name)
        except:
            hypotest = None
            
        if not hypotest or hypotest is None or hypotest.ClassName() != 'RooStats::HypoTestInverterResult':
            continue
            
        if merge_hypotest is None:
            merge_hypotest = hypotest.Clone()
        else:
            merge_hypotest.Add(hypotest.Clone())

        hypotest.Delete()
        
        infile.Close()

    # save point to output file
    ul_dict[point] = merge_hypotest.UpperLimit()

with open(output_file, 'w+') as f:
    json.dump(ul_dict, f, indent=4)


