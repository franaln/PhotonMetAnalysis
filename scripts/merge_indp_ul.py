#!/usr/bin/env python

import os
import re
import sys
import fnmatch
import ROOT

ROOT.gSystem.Load("libSusyFitter.so")

def merge(input_files, output_file):
    
    """ merge the hypotest results and fits from all
    files in input_files into output_file """

    merge_htr  = None

    for path in input_files:

        infile = ROOT.TFile.Open(path)

        try:
            htr_result = infile.Get('result_mu_SIG')
        except:
            htr_result = None

        if merge_htr is None:
            merge_htr = htr_result.Clone()
        else:
            merge_htr.Add(htr_result.Clone())

        htr_result.Delete()

        infile.Close()

    outfile = ROOT.TFile(output_file, 'update')
    outfile.cd()
    merge_htr.Write()
    outfile.Close()

        


## Main
if len(sys.argv) < 3:
    print 'usage: merge_indp_ul.py output_file input_file1 input_file2 ...'
    sys.exit(1)

output_file = sys.argv[1]  
input_files  = sys.argv[2:] 

merge(input_files, output_file)
    

