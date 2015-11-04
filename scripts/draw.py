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
    parser.add_argument('-o', dest='output_dir', default='.')
    parser.add_argument('--save', help='Save histograms in this rootfile')

    # samples, regions, variables
    parser.add_argument('-v', '--variable', dest='variables', required=True)
    parser.add_argument('-r', '--region', dest='regions', help='regions separated by ,')
    parser.add_argument('-s', '--sample', dest='samples', help='samples separated by ,')

    # Backgrounds
    # parser.add_argument('--mc', action='store_true', help='use all backgrounds from MC')
    # parser.add_argument('--qcd', default='sherpa', help='alpgen, pythia or sherpa')

    # normalization
    # parser.add_argument('--muqcd',  dest='mu_qcd', help='Normalization factor for gam+jet')
    # parser.add_argument('--muwgam', dest='mu_wgam', help='Normalization factor for W gamma')
    # parser.add_argument('--mutgam', dest='mu_tgam', help='Normalization factor for ttbar gamma')
    # parser.add_argument('--norm', action='store_true')
    parser.add_argument('--normqcd', action='store_true')

    # other
    parser.add_argument('--opt', action='store_true', help='Optimization plot')
    parser.add_argument('--sel', dest='selection', default='', help='Custom selection')
    parser.add_argument('--n1', action='store_true', help='N-1 plot')
    parser.add_argument('--comp', action='store_true', dest='region_composition',
                        help='create region composition plot')
    parser.add_argument('--signal', action='store_true', help='Add signal samples (separated with ,)')
    parser.add_argument('--blind', action='store_true', help='Don\'t include the data')

    parser.add_argument('--debug', action='store_true', help='print debug messages')

    parser.add_argument('--pl', action='store_true', help='publink')

    global args
    args = parser.parse_args()

    # if args.input_file:
    #     # get_histogram = partial(get_histogram_from_file, args.input_file)
    #     get_histogram = partial(miniutils.get_histogram, rootfile=args.input_file)
    # else:

    get_histogram = miniutils.get_histogram
    get_histogram = partial(get_histogram, remove_var=True)

    # output directory
    #utils.mkdirp(args.output_dir)

    # regions
    if args.regions is not None:
        regions = args.regions.split(',')
    else:
        regions = ['',]

    # variables
    variables = args.variables.split(',')

    # samples
    if args.samples is not None:
        samples = args.samples.split(',')

    # systematics
    syst = 'Nom' # only nominal for now

    ## plots style
    set_atlas_style()
    # set_default_style()

    # Backgrounds
    backgrounds = [
        'photonjet',
        'multijet',
        'vgamma',
        'wjets',
        'zjets',
        'ttbar',
        'ttbarg',
        ]
    # dibsoon, topgamma?

    # Region composition
    # if args.region_composition:

    #     h_comp_bkg = OrderedDict()
    #     for name in backgrounds:
    #         h_comp_bkg[name] = Hist(name, len(regions), 0, len(regions))

    #     h_comp_data = Hist('data', len(regions), 0, len(regions))

    #     for i, region in enumerate(regions):

    #         if args.input_file:
    #             selection = region
    #         else:
    #             if not args.selection:
    #                 selection = getattr(regions_, region)
    #             else:
    #                 selection = args.selection

    #         region_name = region[:-2]

    #         # get regions histogram
    #         h_region_data = get_histogram('data', 'cuts', '', selection, syst)

    #         if args.blind and 'SR' in region:
    #             h_region_data.SetBinContent(1, 0)
    #             h_region_data.SetBinError(1, 0)

    #         h_region_bkg = dict()
    #         for name in h_comp_bkg.iterkeys():
    #             h_region_bkg[name] = get_histogram(name, 'cuts', '', selection, syst)

    #         # normalize
    #         if not all(v is None for v in [args.mu_qcd, args.mu_wgam, args.mu_tgam]):
    #             normalize_backgrounds(h_region_bkg)
    #         elif args.normqcd:
    #             normalize_qcd_to_data(h_region_data, h_region_bkg)

    #         # add to composition histogram
    #         n = h_region_data.GetBinContent(1)
    #         e = h_region_data.GetBinError(1)

    #         h_comp_data.SetBinContent(i+1, n)
    #         h_comp_data.SetBinError(i+1, e)

    #         h_comp_data.GetXaxis().SetBinLabel(i+1, region_name)

    #         for name in h_comp_bkg.iterkeys():
    #             n = h_region_bkg[name].GetBinContent(1)
    #             e = h_region_bkg[name].GetBinError(1)

    #             h_comp_bkg[name].SetBinContent(i+1, n)
    #             h_comp_bkg[name].SetBinError(i+1, e)

    #             h_comp_bkg[name].GetXaxis().SetBinLabel(i+1, region_name)


    #     for bkg, hist in h_comp_bkg.iteritems():
    #         set_hist_style(hist, color=colors_dict[bkg], fill=True)

    #     set_hist_style(h_comp_data, markersize=1.2, linewidth=1, color=kBlack)

    #     plot(h_comp_bkg, h_comp_data, None, 'cuts',
    #          os.path.join(args.output_dir, 'region_composition'))

    #     if args.save:
    #         file_name = os.path.join(args.output_dir, args.save)
    #         with RootFile(file_name, 'update') as f:
    #             f.write(h_comp_bkg)
    #             f.write(h_comp_data)

    #     return

    # Custom plot
    # if args.samples is not None:

    #     for region in regions:
    #         for variable in variables:
    #             print 'plotting %s in region %s ...' % (variable, region)

    #             if not args.selection:
    #                 selection = getattr(regions_, region)
    #             else:
    #                 selection = args.selection

    #             # create histograms
    #             histograms = []
    #             for sample in samples:
    #                 h = get_histogram(sample, variable, '', selection, syst)

    #                 histograms.append(h)

    #             # configure histograms
    #             icol = 1
    #             for sample, hist in zip(samples, histograms):
    #                 try:
    #                     set_hist_style(hist, color=colors[sample])
    #                 except KeyError:
    #                     set_hist_style(hist, color=icol)
    #                     icol += 1

    #             # plot
    #             conf = plots_conf.get(variable, plots_conf['default'])

    #             p = Plot('plot')

    #             for sample, hist in zip(samples, histograms):
    #                 p.add(sample, hist, 'hist')

    #             if 'BIN' in conf.ytitle:
    #                 ytitle = conf.ytitle.replace('BIN', '{:.2f}'.format(h_data_toplot.GetBinWidth(1)))
    #             else:
    #                 ytitle = conf.ytitle

    #             p.create(logy=True, xtitle=conf.xtitle, ytitle=ytitle, xmin=conf.xmin,
    #                         xmax=conf.xmax, include_ratio=True)

    #             if not region:
    #                 output_name = 'plot_sel_%s' %  variable
    #             else:
    #                 output_name = 'plot_%s_%s' % (region, variable)


    #             p.save(output_name+'.eps')
    #             p.save(output_name+'.png')

    #     return

    

    # Standard DATA/Backgrounds plot
    if not args.input_file:

        for region in regions:
            for variable in variables:
                print 'plotting %s in region %s ...' % (variable, region)

                # if args.input_file:
                #     selection = region
                # else:
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
                    h_bkg[name] = get_histogram(name, variable, region_name, selection, syst)

                
                h_bkg['vjets'] = h_bkg['wjets'].Clone()
                h_bkg['vjets'].Add(h_bkg['zjets'], 1)

                h_bkg['tgamma'] = h_bkg['ttbarg'].Clone()
                h_bkg['tgamma'].Add(h_bkg['ttbar'], 1)

                del h_bkg['wjets']
                del h_bkg['zjets']
                del h_bkg['ttbarg']
                del h_bkg['ttbar']


                ## data
                if args.blind or args.opt:
                    h_data = None
                else:
                    h_data = get_histogram('data', variable, region_name, selection, syst)

                ## add overflow bins to the last bin
                for hist in h_bkg.itervalues():
                    histogram_add_overflow_bin(hist)

                if h_data is not None:
                    histogram_add_overflow_bin(h_data)

                ## signal
                h_signal = OrderedDict()
                if 'SR' in region:

                    signals = {
                        'GGM_M3_mu_1500_450': 'ggm1',
                        'GGM_M3_mu_1400_1250': 'ggm2', 
                        }

                    for name, sig in signals.iteritems():
                        h_signal[name] = get_histogram(sig, variable, region_name, selection, syst)
                        histogram_add_overflow_bin(h_signal[name])


                #blinded = args.blind and (region == 'SR')

                ## before fit plot
                # plot(h_bkg, h_data, h_signal, variable, os.path.join(args.output_dir, 'can_{}_{}_beforeFit'.format(region_name, variable)), blinded)

                # outname = os.path.join(args.output_dir, 'can_{}_{}_beforeFit'.format(region, variable))
                # do_plot(outname, variable, h_data, h_bkg, h_signal, region_name=region)

                ## after fit plot
                h_bkg_after = dict(h_bkg)

                ## normalization
                # if not any(v is None for v in [args.mu_qcd, args.mu_wgam, args.mu_tgam]):
                #     normalize_backgrounds(h_bkg_after)
                # if args.normqcd:

                #     #     h_data_met = get_histogram('data', 'met_et', region_name, selection, syst)
                #     # h_bkg_met = {}
                #     # for name in backgrounds:
                #     #     h_bkg_met[name] = get_histogram(name, 'met_et', region_name, selection, syst)
                    
                #     #     s = normalize_qcd_to_data(h_data_met, h_bkg_met)
                #     pass

                varname = variable.replace('[', '').replace(']', '')
                
                if args.opt:

                    outname = os.path.join(args.output_dir, 'opt_{}_{}'.format(region, varname))
                    do_plot(outname, variable, bkg=h_bkg_after, signal=h_signal, region_name=region)

                else:

                    outname = os.path.join(args.output_dir, 'can_{}_{}_afterFit'.format(region, varname))
                    do_plot(outname, variable, h_data, h_bkg_after, h_signal, region_name=region)

                if args.pl:
                    os.system('publink %s.pdf' % outname)

                # save
                if args.save is not None:
                    file_name = os.path.join(args.output_dir, args.save)
                    with RootFile(file_name, 'update') as f:
                        for hist in h_bkg_after.itervalues():
                            f.write(hist)
                        for hist in h_signal.itervalues():
                            f.write(hist)
                        f.write(h_data)

    # Standard plot from histograms
    # if args.input_file:
    #     for region in regions:
    #         for variable in variables:
    #             print 'plotting %s in region %s ...' % (variable, region)

    #             selection = region
    #             region_name = region[:-2]

    #             ## backgrounds
    #             h_bkg = OrderedDict()

    #             for name in backgrounds:
    #                 if 'alpgen' in name:
    #                     h_bkg[name] = get_histogram(name.replace('_alpgen',''), variable, region_name, selection, syst)
    #                 else:
    #                     h_bkg[name] = get_histogram(name, variable, region_name, selection, syst)

    #             ## data
    #             if args.blind:
    #                 h_data = None
    #             else:
    #                 h_data = get_histogram('data', variable, region_name, selection, syst)

    #             ## signal
    #             h_signal = OrderedDict()

    #             if '2' in region:
    #                 signals = ['GGM_M3_mu_all_1050_175', 'GGM_M3_mu_all_1150_175', 'GGM_M3_mu_all_1150_650']
    #             elif '3' in region:
    #                 signals = ['GGM_M3_mu_all_1050_750', 'GGM_M3_mu_all_1050_950', 'GGM_M3_mu_all_1250_1150']
    #             else:
    #                 signals = ['GGM_M3_mu_all_1050_175', 'GGM_M3_mu_all_1150_175', 'GGM_M3_mu_all_1150_650']

    #             for sig in signals:
    #                 h_signal[sig] = get_histogram(sig, variable, region_name, selection, syst)


    #             ## configure histograms
    #             for bkg, hist in h_bkg.iteritems():
    #                 set_hist_style(hist, color=colors[bkg], fill=True)

    #             if h_data is not None:
    #                 set_hist_style(h_data, msize=1.2, lwidth=1, color=ROOT.kBlack)

    #             if h_signal:
    #                 for sig, hist in h_signal.iteritems():
    #                     set_hist_style(hist, msize=1.2, lwidth=2, lstyle=2, color=colors[sig])

    #             blinded = args.blind and (region == 'SR')

    #             plot(h_bkg, h_data, h_signal, variable, os.path.join(args.output_dir, 'can_{}_{}_afterFit'.format(region_name, variable)), blinded)





if __name__ == '__main__':
    main()
