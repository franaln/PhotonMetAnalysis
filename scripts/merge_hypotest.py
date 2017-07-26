#!/usr/bin/env python

import os
import re
import sys
import fnmatch
import ROOT

ROOT.gSystem.Load("libSusyFitter.so")

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def merge(input_files, output_file):
    
    """ merge the hypotest results and fits from all
    files in input_files into output_file """

    # Get all available points
    all_points = []
    for path in input_files:

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

    # Loop over points, merge them and save it to output file
    for point in all_points:

        print 'Merging point: %s' % point

        name = 'hypo_%s' % point

        merge_hypotest = None
        merge_fit      = None

        for path in input_files:
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

            # Corresponding fit
            if merge_fit is None:
                try:
                    merge_fit = infile.Get(name.replace('hypo', 'fitTo')).Clone()
                except:
                    print 'No fit available for point: %s' % point

            infile.Close()

        # save point to output file
        outfile = ROOT.TFile(output_file, 'update')
        outfile.cd()
        merge_hypotest.Write()
        merge_fit.Write()
        outfile.Close()

        


## Main
if len(sys.argv) < 3:
    print 'usage: merge_hypotest.py output_dir input_dir1 input_dir2 ...'
    sys.exit(1)

    
files_nominal = []
files_xsec_dn = []
files_xsec_up = []

output_dir = sys.argv[1]  
input_dirs  = sys.argv[2:] 

for input_dir in input_dirs:
    for root, dirnames, filenames in os.walk(input_dir):
        for filename in fnmatch.filter(filenames, 'Output_fixSigXSecNominal_hypotest.root'):
            files_nominal.append(os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, 'Output_hypotest.root'):
            files_nominal.append(os.path.join(root, filename))

        for filename in fnmatch.filter(filenames, 'Output_fixSigXSecDown_hypotest.root'):
            files_xsec_dn.append(os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, 'Output_fixSigXSecUp_hypotest.root'):
            files_xsec_up.append(os.path.join(root, filename))


print 'Merging %i files from %s to %s' % (len(files_nominal), ','.join(input_dirs), output_dir)


# try to guess if signal xs files exists
do_sigxs = bool(files_xsec_dn and files_xsec_up)

# create output directory
if output_dir != '.':
    os.system('mkdir -p ' + os.path.join(output_dir))

# if signal xs files exists merge the three files, else merge the only file
if do_sigxs:
    merge(files_nominal, os.path.join(output_dir, 'Output_fixSigXSecNominal_hypotest.root'))
    merge(files_xsec_dn, os.path.join(output_dir, 'Output_fixSigXSecDown_hypotest.root'))
    merge(files_xsec_up, os.path.join(output_dir, 'Output_fixSigXSecUp_hypotest.root'))

else:
    merge(files_nominal, os.path.join(output_dir, 'Output_hypotest.root'))
    

