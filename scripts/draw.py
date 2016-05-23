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

def normalize_qcd_to_data():

    bin0 = hdata.FindBin(0)
    bin1 = hdata.FindBin(50)

    data_norm = hdata.Integral(bin0, bin1)
    
    bkg_norm = 0.0
    qcd_norm = 0.0
    for name, hist in hbkg.iteritems():
        if name in ('smpdata', 'qcd', 'photonjet'):
            qcd_norm = hist.Integral(bin0, bin1)
        else:
            bkg_norm += hist.Integral(bin0, bin1)

    s = (data_norm-bkg_norm)/qcd_norm if qcd_norm > 0.0 else 1.0

    print 'MET < 50 GeV -> Data: %.2f, QCD: %.2f, Others: %.2f' % (data_norm, qcd_norm, bkg_norm)
    print 'factor = %.2f' % s
    return s


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
    # parser.add_argument('--qcd', default='sherpa', help='alpgen, pythia or sherpa')

    # normalization
    parser.add_argument('--muq', help='Normalization factor for gam+jet')
    parser.add_argument('--muw', help='Normalization factor for W gamma')
    parser.add_argument('--mut', help='Normalization factor for ttbar gamma')

    parser.add_argument('--normqcd', action='store_true')
    parser.add_argument('--after', dest='after_fit', action='store_true')

    parser.add_argument('-l', dest='lumi')

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

    # if args.input_file:
    #     # get_histogram = partial(get_histogram_from_file, args.input_file)
    #     get_histogram = partial(miniutils.get_histogram, rootfile=args.input_file)
    # else:

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
    if args.variables == 'all':
        variables = ['ph_pt[0]', 
                     'jet_n', 'bjet_n', 'jet_pt', 
                     'met_et', 'ht', 'meff', 
                     'rt2', 'rt4', 
                     'dphi_gammet', 
                     'dphi_gamjet', 
                     'dphi_jetmet', ]
    else:
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
            'zllgamma',
            'znunugamma',
            'wgamma',
            'wjets',
            'zjets',
            'ttbar',
            'ttbarg',
            ]
    else:
        backgrounds = [
            'photonjet',
            'zllgamma',
            'znunugamma',
            'wgamma',
            'ttbarg',
            'jfake',
            'efake'
            ]
   
    # dibsoon, topgamma?

    # mu_t = Value(1.70, 0.62) 
    # mu_w = Value(0.40, 0.32)
    # mu_p = Value()

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

                
            if args.after_fit:

                if args.muq is not None:
                    
                    if ',' in args.muq:
                        mu = ( float(n) for n in args.muq.split(',') )
                        histogram_scale(h_bkg['photonjet'], *mu)

                    else:
                        h_bkg['photonjet'].Scale(float(args.muq))


                
                # else:
                #     if '_L' in region:
                #         h_bkg['photonjet'].Scale(0.85)
                #         h_bkg['wgamma']   .Scale(0.52)
                #         h_bkg['ttbarg']   .Scale(0.78)

                #     elif '_H' in region:
                #         pass


            if args.mc:
                h_bkg['vjets'] = h_bkg['wjets'].Clone()
                h_bkg['vjets'].Add(h_bkg['zjets'], 1)

            h_bkg['vgamma'] = h_bkg['wgamma'].Clone()
            h_bkg['vgamma'].Add(h_bkg['zllgamma'], 1)
            h_bkg['vgamma'].Add(h_bkg['znunugamma'], 1)
            
            if args.mc:
                h_bkg['tgamma'] = h_bkg['ttbarg'].Clone()
                h_bkg['tgamma'].Add(h_bkg['ttbar'], 1)
            else:
                h_bkg['tgamma'] = h_bkg['ttbarg'].Clone()

            del h_bkg['wgamma']
            del h_bkg['zllgamma']
            del h_bkg['znunugamma']
            del h_bkg['ttbarg']
            if args.mc:
                del h_bkg['wjets']
                del h_bkg['zjets']
                del h_bkg['ttbar']


            ## data
            if args.opt:
                h_data = None
            elif args.blind is not None:
                selection += '&& %s' % args.blind
                h_data = miniutils.get_histogram('data', variable=variable, region=region_name, selection=selection, syst=syst, remove_var=False, lumi=args.lumi)
            else:
                h_data = get_histogram('data', variable=variable, region=region_name, selection=selection, syst=syst)

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
                    h_signal['GGM_M3_mu_1700_250'] = get_histogram('GGM_M3_mu_1700_250', variable=variable, region=region_name, selection=selection, syst=syst)
                    h_signal['GGM_M3_mu_1700_650'] = get_histogram('GGM_M3_mu_1700_650', variable=variable, region=region_name, selection=selection, syst=syst)

                    histogram_add_overflow_bin(h_signal['GGM_M3_mu_1700_250'])
                    histogram_add_overflow_bin(h_signal['GGM_M3_mu_1700_650'])

                elif region.endswith('_H'):
                    h_signal['GGM_M3_mu_1400_1050'] = get_histogram('GGM_M3_mu_1400_1050', variable=variable, region=region_name, selection=selection, syst=syst)
                    h_signal['GGM_M3_mu_1400_1375'] = get_histogram('GGM_M3_mu_1400_1375', variable=variable, region=region_name, selection=selection, syst=syst)
                    
                    histogram_add_overflow_bin(h_signal['GGM_M3_mu_1400_1050'])
                    histogram_add_overflow_bin(h_signal['GGM_M3_mu_1400_1375'])
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
