#! /usr/bin/env python

import os
import sys
import glob

if len(sys.argv) < 2:
    print 'usage: merge_batch_output.py [batch-dir]'
    sys.exit(1)


batch_dir = sys.argv[1]

point_dirs = glob.glob(batch_dir + '/results/*')

# check region type
signal_region = os.path.basename(point_dirs[0]).split('_')[0]

hf_dir = 'PhotonMetAnalysis_excl_%s' % signal_region

# create merged dir
cmd = 'mkdir -p %s/merged' % batch_dir
os.system(cmd)

# check if signal xs
sigxs = False
test_hypo_file = '%s/%s/Output_fixSigXSecNominal_hypotest.root' % (point_dirs[0], hf_dir)
if os.path.exists(test_hypo_file):
    sigxs = True

# merge
if sigxs:

    cmd1 = 'hadd -f %s/merged/Output_fixSigXSecDown_hypotest.root' % batch_dir
    cmd2 = 'hadd -f %s/merged/Output_fixSigXSecNominal_hypotest.root' % batch_dir
    cmd3 = 'hadd -f %s/merged/Output_fixSigXSecUp_hypotest.root' % batch_dir

    for point_dir in point_dirs:

        hypo_file1 = '%s/%s/Output_fixSigXSecDown_hypotest.root' % (point_dir, hf_dir) 
        hypo_file2 = '%s/%s/Output_fixSigXSecNominal_hypotest.root' % (point_dir, hf_dir) 
        hypo_file3 = '%s/%s/Output_fixSigXSecUp_hypotest.root' % (point_dir, hf_dir) 

        if not os.path.exists(hypo_file1) or not os.path.exists(hypo_file2) or not os.path.exists(hypo_file3):
            print 'The following hypotest file does not exist: %s' % hypo_file1
            continue

        cmd1 += ' %s' % hypo_file1
        cmd2 += ' %s' % hypo_file2
        cmd3 += ' %s' % hypo_file3

    os.system(cmd1)
    os.system(cmd2)
    os.system(cmd3)

else:
    
    cmd = 'hadd -f %s/merged/Output_hypotest.root' % batch_dir

    for point_dir in point_dirs:

        hypo_file = '%s/%s/Output_hypotest.root' % (point_dir, hf_dir) 

        if not os.path.exists(hypo_file):
            print 'The following hypotest file does not exist: %s' % hypo_file
            continue

        cmd += ' %s' % hypo_file

    os.system(cmd)

#excllimit_18jul_sril/results/SRinclL_1400_1050/PhotonMetAnalysis_excl_SRinclL/Output_hypotest.root
#excllimit_18jul_sril/results/SRinclL_1800_200/results/PhotonMetAnalysis_excl_SRinclL/
#results/SRinclL_1800_450/PhotonMetAnalysis_excl_SRinclL/
