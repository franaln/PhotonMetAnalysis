#! /usr/bin/env python

# single photon analysis
# plots script

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)

import os
import sys
import argparse
import math
from functools import partial
from rootutils import *
from collections import OrderedDict
import miniutils
import regions as regions_

from drawlib import *

def main():

    parser = argparse.ArgumentParser(description='')

    # histograms file / output directory
    parser.add_argument('-i', dest='input_file')
    parser.add_argument('-o', dest='output', default='.')
    parser.add_argument('--save', help='Save histograms in this rootfile')

    # samples, regions, variables
    parser.add_argument('-v', '--variable', dest='variables', required=True)
    parser.add_argument('-r', '--region', dest='regions', help='regions separated by ,')

    # Backgrounds
    parser.add_argument('--mc', action='store_true', help='use all backgrounds from MC')
 
    # normalization
    parser.add_argument('--muq', help='Normalization factor for gam+jet')
    parser.add_argument('--muw', help='Normalization factor for W gamma')
    parser.add_argument('--mut', help='Normalization factor for ttbar gamma')

    parser.add_argument('--normqcd', action='store_true')
    parser.add_argument('--after', dest='after_fit', action='store_true')

    parser.add_argument('-l', dest='lumi')
    parser.add_argument('--data', help='data15|data16|data')

    # other
    parser.add_argument('--opt', action='store_true', help='Optimization plot')

    parser.add_argument('--sel', dest='selection', default='', help='Custom selection')
    parser.add_argument('--outname', help='If custom selection use this output_name')

    parser.add_argument('--n1', action='store_true', help='N-1 plot')
    parser.add_argument('--comp', action='store_true', dest='region_composition',
                        help='create region composition plot')
    parser.add_argument('--signal', action='store_true', help='Add signal samples (separated with ,)')
    parser.add_argument('--blind', help='Add this selection only to data')

    parser.add_argument('--debug', action='store_true', help='print debug messages')

    parser.add_argument('--pl', action='store_true', help='publink')
    parser.add_argument('--www', action='store_true', help='create webpage')

    global args
    args = parser.parse_args()

    if args.input_file:
        get_histogram = partial(get_histogram_from_file, args.input_file)
    else:
        if args.n1:
            get_histogram = partial(miniutils.get_histogram, remove_var=True, lumi=args.lumi)
        else:
            get_histogram = partial(miniutils.get_histogram, remove_var=False, lumi=args.lumi)

    # regions
    if args.regions is not None:
        regions = args.regions.split(',')
    else:
        regions = ['',]

    # variables
    variables = args.variables.split(',')

    # systematics
    syst = 'Nom' # only nominal for now

    ## plots style
    set_atlas_style()
    # set_default_style()

    # Backgrounds
    if args.mc:
        backgrounds = [
            'photonjet',
            'multijet',
            'zgamma',
            'wgamma',
            'wjets',
            'zjets',
            'ttbar',
            'ttbarg',
            ]
    else:
        backgrounds = [
            'photonjet',
            'zgamma',
            'wgamma',
            'ttbarg',
            'jfake',
            'efake',
            'diphoton',
            'vgammagamma',
            ]
   
    # Standard DATA/Backgrounds plot
    for region in regions:

        for variable in variables:

            print 'plotting %s in region %s ...' % (variable, region)

            if args.input_file:
                selection = region
            else:
                if not args.selection:
                    selection = getattr(regions_, region)
                else:
                    selection = args.selection

            if args.selection:
                region_name = region
            else:
                region_name = region[:-2]

            ## backgrounds
            h_bkg = OrderedDict()

            for name in backgrounds:
                h_bkg[name] = get_histogram(name, variable=variable, region=region_name, selection=selection, syst=syst) 

            # Scale backgrounds according to bkg-only fit
            if args.after_fit:

                if args.muq is not None:
                    
                    if ',' in args.muq:
                        mu = ( float(n) for n in args.muq.split(',') )
                        histogram_scale(h_bkg['photonjet'], *mu)

                    else:
                        h_bkg['photonjet'].Scale(float(args.muq))

                if args.muw is not None:
                    
                    if ',' in args.muw:
                        mu = ( float(n) for n in args.muw.split(',') )
                        histogram_scale(h_bkg['wgamma'], *mu)

                    else:
                        h_bkg['wgamma'].Scale(float(args.muq))

                if args.mut is not None:
                    
                    if ',' in args.mut:
                        mu = ( float(n) for n in args.mut.split(',') )
                        histogram_scale(h_bkg['ttbarg'], *mu)

                    else:
                        h_bkg['ttbarg'].Scale(float(args.muq))

                        
            # Merge backgrounds to plot
            if args.mc:
                h_bkg['vjets'] = h_bkg['wjets'].Clone()
                h_bkg['vjets'].Add(h_bkg['zjets'], 1)

            h_bkg['vgamma'] = h_bkg['wgamma'].Clone()
            h_bkg['vgamma'].Add(h_bkg['zgamma'], 1)
            
            if args.mc:
                h_bkg['tgamma'] = h_bkg['ttbarg'].Clone()
                h_bkg['tgamma'].Add(h_bkg['ttbar'], 1)
            else:
                h_bkg['tgamma'] = h_bkg['ttbarg'].Clone()

            if 'diphoton' in h_bkg:
                h_bkg['diphoton'].Add(h_bkg['vgammagamma'], 1)

            del h_bkg['wgamma']
            del h_bkg['zgamma']
            del h_bkg['ttbarg']
            if 'vgammagamma' in h_bkg:
                del h_bkg['vgammagamma']
            if args.mc:
                del h_bkg['wjets']
                del h_bkg['zjets']
                del h_bkg['ttbar']


            ## data
            if args.opt:
                h_data = None
            elif args.blind is not None:
                selection += '&& %s' % args.blind
                h_data = miniutils.get_histogram(args.data, variable=variable, region=region_name, selection=selection, syst=syst, remove_var=False, lumi=args.lumi)
            else:
                h_data = get_histogram(args.data, variable=variable, region=region_name, selection=selection, syst=syst)

            ## add overflow bins to the last bin
            for hist in h_bkg.itervalues():
                histogram_add_overflow_bin(hist)

            if h_data is not None:
                histogram_add_overflow_bin(h_data)


            ## signal
            h_signal = None
            if args.signal:
                h_signal = OrderedDict()
                    
                if region.endswith('_L'):
                    h_signal['GGM_M3_mu_1600_250'] = get_histogram('GGM_M3_mu_1600_250', variable=variable, region=region_name, selection=selection, syst=syst)
                    h_signal['GGM_M3_mu_1600_650'] = get_histogram('GGM_M3_mu_1600_650', variable=variable, region=region_name, selection=selection, syst=syst)

                    histogram_add_overflow_bin(h_signal['GGM_M3_mu_1600_250'])
                    histogram_add_overflow_bin(h_signal['GGM_M3_mu_1600_650'])

                elif region.endswith('_H'):
                    h_signal['GGM_M3_mu_1600_1250'] = get_histogram('GGM_M3_mu_1600_1250', variable=variable, region=region_name, selection=selection, syst=syst)
                    h_signal['GGM_M3_mu_1600_1450'] = get_histogram('GGM_M3_mu_1600_1450', variable=variable, region=region_name, selection=selection, syst=syst)
                    
                    histogram_add_overflow_bin(h_signal['GGM_M3_mu_1600_1250'])
                    histogram_add_overflow_bin(h_signal['GGM_M3_mu_1600_1450'])
                else:
                    h_signal['GGM_M3_mu_1700_650'] = get_histogram('GGM_M3_mu_1700_650', variable=variable, region=region_name, selection=selection, syst=syst)
                    h_signal['GGM_M3_mu_1700_1050'] = get_histogram('GGM_M3_mu_1700_1050', variable=variable, region=region_name, selection=selection, syst=syst)

                    histogram_add_overflow_bin(h_signal['GGM_M3_mu_1700_650'])
                    histogram_add_overflow_bin(h_signal['GGM_M3_mu_1700_1050'])
                    
                
            
            varname = variable.replace('[', '').replace(']', '')
                
            
            if args.selection and args.outname:
                tag = args.outname
            else:
                tag = region

            if args.opt:
                outname = os.path.join(args.output, 'can_{}_{}_opt'.format(tag, varname))
            elif args.after_fit:
                outname = os.path.join(args.output, 'can_{}_{}_afterFit'.format(tag, varname))
            else:
                outname = os.path.join(args.output, 'can_{}_{}_beforeFit'.format(tag, varname))
            
            if args.opt:
                do_plot(outname, variable, data=h_data, bkg=h_bkg, signal=h_signal, region_name=region) ##, do_ratio=False)
            else:
                do_plot(outname, variable, data=h_data, bkg=h_bkg, signal=h_signal, region_name=region)
                
            if args.pl:
                os.system('publink %s.pdf' % outname)

            # save
            if args.save is not None:
                file_name = os.path.join(args.output, args.save)
                with RootFile(file_name, 'update') as f:
                    f.write(h_data)
                    for hist in h_bkg.itervalues():
                        f.write(hist)
                    for hist in h_signal.itervalues():
                        f.write(hist)






if __name__ == '__main__':
    main()
