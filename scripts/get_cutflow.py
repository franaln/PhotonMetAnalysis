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

import regions as regions_
from miniutils import get_cutflow

def main():

    parser = argparse.ArgumentParser(description='get cutflow')
    
    parser.add_argument('-r', dest='regions', help='Region')
    parser.add_argument('-s', dest='samples', help='Samples separated with ,')
    parser.add_argument('-i', dest='files', help='Files separated with ,')
    parser.add_argument('-l', dest='luminosity', help='Luminosity [fb-1]')
    parser.add_argument('-p', dest='percentage', action='store_true', help='Show percentage')
    parser.add_argument('-v', dest='version', help='Mini version')
    parser.add_argument('--latex', action='store_true', default=False, help='use LatexTable instead PrettyTable')
    parser.add_argument('--sel', dest='selection', help='Selection')
    parser.add_argument('--pre', dest='preselection', action='store_true', help='add preselection cutflow')

    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)
        
    args = parser.parse_args()
    
    ## samples
    if args.samples is None and args.files is None:
        sys.exit(1)        

    if args.regions is None:
        args.regions = 'Sel'

    do_scale = True
    if args.luminosity == "0":
        do_scale = False

    for region in args.regions.split(','):

        try:
            selection = getattr(regions_, region)
        except:
            selection = args.selection

        flows = OrderedDict()

        if args.samples is not None:
            for sample in args.samples.split(','):

                cutflow = get_cutflow(sample, selection=selection, lumi=args.luminosity, preselection=args.preselection, scale=do_scale, version=args.version)

                cuts = [ cutflow.GetXaxis().GetBinLabel(b+1) for b in xrange(cutflow.GetNbinsX()) ]
                flows[sample] = [ cutflow.GetBinContent(b+1) for b in xrange(cutflow.GetNbinsX()) ]
    
        if args.files is not None:
            for fname in args.files.split(','):

                cutflow = get_cutflow(fname, selection=selection, preselection=args.preselection, scale=do_scale, version=args.version)
    
                cuts = [ cutflow.GetXaxis().GetBinLabel(b+1) for b in xrange(cutflow.GetNbinsX()) ]
                flows[os.path.basename(fname)] = [ cutflow.GetBinContent(b+1) for b in xrange(cutflow.GetNbinsX()) ]
        
        if args.latex:
            table = LatexTable()
        else:
            table = PrettyTable()

        table.add_column(region, cuts)
    
        for sample, flow in flows.iteritems():
            
            total = float(flow[0])

            if args.percentage:
                table.add_column(sample, ['%.2f (%d%%)' % (n, int(round(100*(n/total)))) for n in flow])
            else:
                table.add_column(sample, ['%.2f' % n for n in flow])
    
        print table


if __name__ == '__main__':
    main()
