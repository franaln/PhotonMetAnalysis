#! /usr/bin/env python

import os
import sys
import ROOT

if len(sys.argv) < 3:
    print 'usage: txt2hist.py file.root file.txt'
    sys.exit(1)

text_file_path = sys.argv[1]
root_file_path = sys.argv[2]

if not os.path.isfile(text_file_path):
    print('%s is not a file' % text_file_path)
    sys.exit(1)
    

fin = ROOT.TFile(root_file_path, 'recreate')

with open(text_file_path) as f:
    
    lines = f.read().split('\n')

    for line in lines:

        if not line:
            continue
        
        name, val, err = line.split()

        val = float(val)
        err = float(err)

        hist = ROOT.TH1D(name, name, 1, 0.5, 1.5)

        hist.SetBinContent(1, val)
        hist.SetBinError(1, err)

        hist.Write(name)
        
    
fin.Close()
