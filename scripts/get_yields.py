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
from statutils import get_significance
from mass_dict import mass_dict


def scale_gamjet(sel):

    get_histogram = partial(miniutils.get_histogram, lumi='data', remove_var=True)

    
    h_met_gamjet = get_histogram('photonjet', 'met_et', 'SR', sel)

    h_met_data = get_histogram('data', 'met_et', 'SR', sel) - \
        get_histogram('multijet', 'met_et', 'SR', sel) - \
        get_histogram('vgamma', 'met_et', 'SR', sel) - \
        get_histogram('ttbar', 'met_et', 'SR', sel) - \
        get_histogram('ttbarg', 'met_et', 'SR', sel) - \
        get_histogram('wjets', 'met_et', 'SR', sel) - \
        get_histogram('zjets', 'met_et', 'SR', sel)

    
    maxbin = h_met_gamjet.FindBin(50)

    n_gamjet = h_met_gamjet.Integral(1, maxbin)
    n_data   = h_met_data.Integral(1, maxbin) 

    mu = n_data / n_gamjet

    print n_gamjet, n_data, mu

    return mu
    



def main():

    parser = argparse.ArgumentParser(description='get yields')
    
    parser.add_argument('-r', dest='regions', default='', help='Regions separated with ,')
    parser.add_argument('-s', dest='samples', help='Samples separated with ,')
    parser.add_argument('-i', dest='files', help='Files separated with ,')
    parser.add_argument('-l', dest='lumi', help='Luminosity to scale')
    parser.add_argument('--sel', dest='selection')

    parser.add_argument('--prw', action='store_true', help='apply prw weights')

    parser.add_argument('--data', action='store_true', help='Include data')
    parser.add_argument('--signal', action='store_true', help='Include signal')
    parser.add_argument('--mc', action='store_true', help='Use MC backgrounds')

    parser.add_argument('--after', action='store_true', help='Use fit normalization factors')

    parser.add_argument('--unblind', action='store_true', help='Unblind data')

    parser.add_argument('--m3', default='1400', help='M3')

    parser.add_argument('-v', dest='version', help='force mini version')

    # others
    parser.add_argument('--latex', action='store_true', help='use LatexTable instead PrettyTable')
    parser.add_argument('--nw', action='store_true')


    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)
        
    args = parser.parse_args()
    
    ## samples
    bkgs = [
        'photonjet',
        'wgamma',
        'zgamma',
        'ttbarg',
        'jfake',
        'efake',
        ]
    
    if args.mc:
        bkgs = [
            'photonjet',
            'multijet',
            'wgamma',
            'zgamma',
            #'znunugamma',
            'ttbar',
            'ttbarg',
            'vjets',
            ]
       
    signal = []
    for (m3, mu) in sorted(mass_dict.iterkeys()):
        if int(args.m3) == m3:
            signal.append('GGM_M3_mu_%d_%d' % (m3, mu))


    if args.prw:
        get_events = partial(miniutils.get_events, lumi=args.lumi, version=args.version, prw=True)
    elif args.nw:
        get_events = partial(miniutils.get_events, lumi=args.lumi, version=args.version, scale=False)
    else:
        get_events = partial(miniutils.get_events, lumi=args.lumi, version=args.version)



    if args.regions:
        regions = args.regions.split(',')

    samples = args.samples.split(',') if args.samples is not None else []

    if args.selection is not None:
        regions = []
        regions.append(args.selection)
    if args.latex:
        table = LatexTable()
    else:
        table = PrettyTable()

    # # files = args.files.split(',')
    # filelabels = [f[:10] for f in files]

    if samples:
        table.add_column('', [s for s in samples])
    elif args.data and args.signal:
        table.add_column('', ['Data',]+bkgs+['Total bkg']+signal)
    elif args.data:
        table.add_column('', ['Data',]+bkgs+['Total bkg'])
    elif args.signal:
        table.add_column('', bkgs+['Total bkg']+signal)
    else:
        table.add_column('', bkgs+['Total bkg'])

    for region in regions:

        if not region:
            continue

        try:
            selection = getattr(regions_, region)
        except:
            selection = region

        cols = OrderedDict()

        if samples:

            for sample in samples:
                evts = get_events(sample, region=region, selection=selection)
                cols[sample] = evts

        else:
            
            # Data
            if args.data:
                if 'SR' in region and not args.unblind:
                    cols['data'] = '-1'
                else:
                    cols['data'] = get_events('data', region=region, selection=selection)

            # Bkgs
            total_bkg = Value(0)
            for sample in bkgs:
        
                evts = get_events(sample, region=region, selection=selection)

                if args.after: 
                    if regions[-1] == 'L':
                        if sample == 'photonjet':
                            evts *= 0.99
                        elif sample == 'wgamma':
                            evts *= 1.12
                        elif sample == 'ttbarg':
                            evts *= 0.87
                    elif regions[-1] == 'H':
                        if sample == 'photonjet':
                            evts *= 1.16
                        elif sample == 'wgamma':
                            evts *= 1.12
                        elif sample == 'ttbarg':
                            evts *= 0.88

                cols[sample] = evts

                total_bkg += evts
           
            cols['Total bkg'] = total_bkg

            if region.startswith('CR') and args.data:
                if 'CRQ' in region or 'CRM' in region:
                    mu = (cols['data']-(total_bkg-cols['photonjet']))/cols['photonjet']
                    purity = cols['photonjet'] / total_bkg
                    cols['photonjet'] = '%s (%.2f, mu=%.2f)' % (cols['photonjet'], purity.mean, mu.mean)

                elif 'CRT' in region:
                    mu = (cols['data']-(total_bkg-cols['ttbarg']))/cols['ttbarg']
                    purity = cols['ttbarg'] / total_bkg

                    cols['ttbarg'] = '%s (%.2f%%, mu=%.2f)' % (cols['ttbarg'], purity.mean, mu.mean)

                elif 'CRW' in region:
                    mu = (cols['data']-(total_bkg-cols['wgamma']))/cols['wgamma']
                    purity = cols['wgamma'] / total_bkg

                    cols['wgamma'] = '%s (%.2f%%, mu=%.2f)' % (cols['wgamma'], purity.mean, mu.mean)


            # Signals
            if args.signal:

                for sig in signal:
                    n_s = get_events(sig, region=region, selection=selection)
                    cols[sig] = '%s (%s)' % (n_s, get_significance(n_s, total_bkg))

        table.add_column(region[:10], cols.values())
    
        
    print table


if __name__ == '__main__':
    main()
