#! /usr/bin/env python

import os
import sys
import ROOT

if len(sys.argv) < 3:
    print 'usage: hist2txt.py file.root file.txt'
    sys.exit(1)


root_file_path = sys.argv[1]
text_file_path = sys.argv[2]

if not os.path.isfile(root_file_path):
    print('%s is not a file' % root_file_path)
    sys.exit(1)
    
try:
    fin = ROOT.TFile.Open(root_file_path)
            
    if fin.IsZombie():
        print('Error opening rootfile')
        fin.Close()
        sys.exit(1)
except ReferenceError:
    sys.exit(1)

    
keys = fin.GetListOfKeys()


with open(text_file_path, 'w+') as f:
    
    for key in keys:
    
        obj = fin.Get(key.GetName())

        if not obj.InheritsFrom('TH1'):
            continue

        name = obj.GetName()

        val = obj.GetBinContent(1)
        err = obj.GetBinError(1)

        lout = '{0: <80}          {1:.6f}  {2:.6f}\n'.format(name, val, err)

        f.write(lout)


fin.Close()
