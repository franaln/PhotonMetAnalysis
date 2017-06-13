#!/usr/bin/env python

import os
import sys
import fnmatch
import ROOT

ROOT.gSystem.Load("libSusyFitter.so")

def merge(input_files, output_file):
    
    """ merge all files in input_files into output_file """

    outfile = ROOT.TFile(output_file, 'recreate')

    hypo_dict = dict()
    fit_dict  = dict()

    for path in input_files:

        infile = ROOT.TFile.Open(path)

        content = [ key.GetName() for key in infile.GetListOfKeys() ]

        for name in content:

            if not name.startswith('hypo'): ## or nor name.startswith('fitTo'):
                continue

            point = name.replace('hypo_', '')

            hypotest = infile.Get(name)

            if not hypotest or hypotest.ClassName() != 'RooStats::HypoTestInverterResult':
                continue
            
            if not point in hypo_dict:
                hypo_dict[point] = hypotest
            else:
                hypo_dict[point].Add(hypotest)

            # Corresponding fit
            try:
                fit_dict[point] = infile.Get(name.replace('hypo', 'fitTo'))
            except:
                print 'No fit available for point: %s' % point


    # Save objects in hypo/fit dicts
    outfile.cd()
    for point in hypo_dict.itervalues():
        point.Write()
    for point in fit_dict.itervalues():
        point.Write()
    outfile.Close()


## Main
if len(sys.argv) < 4:
    print 'usage: merge_hypotest.py    output_dir input_dir1 input_dir2 ...'
    print '       merge_hypotest.py -r output_dir input_dir' 

    sys.exit(1)

    
files_nominal = []
files_xsec_dn = []
files_xsec_up = []
if sys.argv[1] == '-r':

    output_dir = sys.argv[2]
    input_dir  = sys.argv[3]

    for root, dirnames, filenames in os.walk(input_dir):
        for filename in fnmatch.filter(filenames, 'Output_fixSigXSecNominal_hypotest.root'):
            files_nominal.append(os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, 'Output_hypotest.root'):
            files_nominal.append(os.path.join(root, filename))

        for filename in fnmatch.filter(filenames, 'Output_fixSigXSecDown_hypotest.root'):
            files_xsec_dn.append(os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, 'Output_fixSigXSecUp_hypotest.root'):
            files_xsec_up.append(os.path.join(root, filename))

    print 'Merging %i files from %s to %s' % (len(files_nominal), input_dir, output_dir)

else:
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
    

