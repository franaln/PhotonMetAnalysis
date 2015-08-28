#! /usr/bin/env python2.7

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True # fix root stupidities
ROOT.gROOT.SetBatch(True)

import os
import sys
import argparse
from prettytable import PrettyTable
from latextable import LatexTable
from collections import OrderedDict

#from samples import MiniDir
import regions as regions_
from miniutils import get_cutflow

def main():

    parser = argparse.ArgumentParser(description='get cutflow')
    
    parser.add_argument('-r', dest='regions', help='Region')
    parser.add_argument('-s', dest='samples', help='Samples separated with ,')
    parser.add_argument('-i', dest='files', help='Files separated with ,')
    
    parser.add_argument('--mc', help='Use MC backgrounds instead DD')

    # others
    parser.add_argument('--latex', action='store_true', default=False, help='use LatexTable instead PrettyTable')
    parser.add_argument('--noweight', action='store_true')

    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)
        
    args = parser.parse_args()
    
    ## samples
    if args.samples is None and args.files is None:
        #if args.mc:
            #samples = ['data', 'qcd', 'wgamma', 'zllgamma', 'znunugamma', 'ttbar', 'ttbarg', 'wjets', 'zjets', 'diboson', 'efake', 'jfake']
        samples = ['data', 'photonjet', 'wgamma', 'zllgamma', 'znunugamma', 'ttbar', 'ttbarg', 'wjets', 'zjets', 'diboson', 'efake', 'jfake']
        
    for region in args.regions.split(','):

        #if args.samples is not None:
        #    files = [ os.path.join(MiniDir, '%s.t146_mini.root' % sample) for sample in args.samples.split(',') ]

        #if args.files is not None:
        #    files = args.files.split(',')

        selection = getattr(regions_, region)
     
        flows = OrderedDict()

        if args.samples is not None:
            for sample in args.samples.split(','):

                cutflow = get_cutflow(sample, selection) #, scale=not args.noweight)

                cuts = [ cutflow.GetXaxis().GetBinLabel(b+1) for b in xrange(cutflow.GetNbinsX()) ]
                flows[sample] = [ cutflow.GetBinContent(b+1) for b in xrange(cutflow.GetNbinsX()) ]
    
        if args.files is not None:
            for fname in args.files.split(','):

                cutflow = get_cutflow(rootfile=fname, selection=selection, scaled=not args.noweight)
    
                cuts = [ cutflow.GetXaxis().GetBinLabel(b+1) for b in xrange(cutflow.GetNbinsX()) ]
                flows[sample] = [ cutflow.GetBinContent(b+1) for b in xrange(cutflow.GetNbinsX()) ]
        
        if args.latex:
            table = LatexTable()
        else:
            table = PrettyTable()

        table.add_column(region, cuts)
    
        for sample, flow in flows.iteritems():
            table.add_column(sample, ['%.2f' % n for n in flow])
    
        print table


if __name__ == '__main__':
    main()
