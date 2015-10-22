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
from functools import partial

import regions as regions_
import miniutils
from rootutils import Value

def main():

    parser = argparse.ArgumentParser(description='get cutflow')
    
    parser.add_argument('-r', dest='regions', default='', help='Regions separated with ,')
    parser.add_argument('-s', dest='samples', help='Samples separated with ,')
    parser.add_argument('-i', dest='files', help='Files separated with ,')
    parser.add_argument('-l', dest='lumi', help='Luminosity to scale')
    parser.add_argument('--sel', dest='selection')

    parser.add_argument('--mc', help='Use MC backgrounds instead DD')

    # others
    parser.add_argument('--latex', action='store_true', default=False, help='use LatexTable instead PrettyTable')
    parser.add_argument('--nw', action='store_true')

    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)
        
    args = parser.parse_args()
    
    ## samples
    bkgs = [
        'photonjet',
        'multijet',
        'vgamma',
        'ttbar',
        'ttbarg',
        'wjets',
        'zjets',
        ]

    signal = [
        'ggm1',
        'ggm2',
        ]

    get_events = partial(miniutils.get_events, lumi=args.lumi)
        
    regions = args.regions.split(',')

    if args.selection is not None:
        regions.append(args.selection)
    if args.latex:
        table = LatexTable()
    else:
        table = PrettyTable()

    table.add_column('', ['Data',]+bkgs+['Total bkg']+signal)

    for region in regions:

        if not region:
            continue

        try:
            selection = getattr(regions_, region)
        except:
            selection = region

        cols = OrderedDict()

        # Data
        cols['Data'] = get_events('data', region, selection)

        # Bkgs
        total_bkg = Value(0)
        for sample in bkgs:
        
            evts = get_events(sample, region, selection)
            cols[sample] = evts

            total_bkg += evts
            
        cols['Total bkg'] = total_bkg

        # Signals
        for sig in signal:
            cols[sig] = get_events(sig, region, selection)

        table.add_column(region[:10], cols.values())
    

    print table


if __name__ == '__main__':
    main()
