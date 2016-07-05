#! /usr/bin/env python

# single photon analysis
# create histograms

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)

import os
import sys
import argparse
import re
from functools import partial

from rootutils import RootFile
import miniutils
import regions as regions_
from mass_dict import mass_dict
from signalxs import gg_xs, gg_xs_unc
import systematics

import analysis as config_analysis

fzero = 0.0001

def main():

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-o', '--output', help='output file name', required=True)

    # samples, regions, variables
    parser.add_argument('-v', dest='variables', default='cuts', help='variables (comma separated)')
    parser.add_argument('-r', dest='regions', help='regions (comma separated)')
    parser.add_argument('-s', dest='samples', help='samples (comma separated)')
    parser.add_argument('-n', help='"L" or "H"')

    # other options
    parser.add_argument('--add', action='store_true')
    parser.add_argument('--dosyst', action='store_true')
    parser.add_argument('--unblind', action='store_true')
    parser.add_argument('--version', help='Use this version')

    # scale to lumi?
    parser.add_argument('-i', '--input')
    parser.add_argument('--lumi')

    args = parser.parse_args()
    
    
    # Scale
    if args.input is not None and args.lumi is not None:
        
        if args.lumi == 'data15':
            lumi = config_analysis.lumi_data15
        elif args.lumi == 'data16':
            lumi = config_analysis.lumi_data16
        elif args.lumi == 'data':
            lumi = config_analysis.lumi_data15 + config_analysis.lumi_data16

        lumi = lumi / 1000. # input should be normalized to 1 fb-1

        print 'Scaling histogram from %s to %s (%s fb-1)' % (args.input, args.lumi, lumi)

        infile = ROOT.TFile.Open(args.input)

        keys = [ key.GetName() for key in infile.GetListOfKeys() ]

        histograms = []
        for key in keys:

            hist = infile.Get(key)

            new_hist = hist.Clone()
            new_hist.SetDirectory(0)

            if 'data' in key or 'efake' in key or 'jfake' in key:
                pass
            else:
                new_hist.Scale(lumi)

            histograms.append(new_hist)

        infile.Close()

        with RootFile(args.output, 'update') as f:
            for hist in histograms:
                f.write(hist)

        return 0



    
    variables = args.variables.split(',')

    region_number = args.n

    if region_number is None:
        parser.print_usage()
        return 1
    
    if args.regions is None:
        args.regions = 'SR,SRincl,CRQ,CRW,CRT,VRM1,VRM2,VRM3,VRD1,VRD2,VRD3,VRL1,VRL2,VRL3,VRL4'
        
    regions = [ '%s_%s' % (r, region_number) for r in args.regions.split(',') ]
   
    mc = [
        'wgamma',
        'zllgamma',
        'znunugamma',
        'ttbarg',
        'photonjet',
        #'ttbar',
        #'multijet',
        #'wjets',
        #'zjets',
        ]

    dd = ['efake15', 'jfake15', 'efake16', 'jfake16', 'efake', 'jfake']

    signals = [ 'GGM_M3_mu_%i_%i' % (m3, mu) for (m3, mu) in mass_dict.keys() ]

    histograms_ewk, histograms_gg = None, None

    data = ['data',]

    samples = []
    if args.samples is not None:
        if 'signal' in args.samples:
            samples.extend(signals)
            #histograms_gg = dict()
            #histograms_ewk = dict()
        elif 'mc' in args.samples:
            samples.extend(mc)
        elif 'dd' in args.samples:
            samples.extend(dd)
        else:
            samples = args.samples.split(',')
    else:
        samples = mc + data + signals +dd
        #histograms_gg = dict()
        #histograms_ewk = dict()

    # Systematics
    do_syst = args.dosyst

    ## high-low systematics
    systematics_expHL = systematics.get_high_low_systematics()

    ## one-sided systematics
    systematics_expOS = systematics.get_one_side_systematics()

    # existing histograms
    # existing_histograms = []
    # if args.add:
    #     f = ROOT.TFile.Open(args.output)
    #     existing_histograms = [ key.GetName() for key in f.GetListOfKeys() ]
    #     f.Close()
    

    # create histograms
    for sample in samples:

        print 'Processing sample %s ...' % sample

        histograms = []

        for region in regions:

            region_type = region.split('_')[-1]
            region_name = region.split('_')[0]
            
            if 'GGM' in sample:
                if region_name in ['SR', 'SRincl', 'CRQ', 'CRW', 'CRT']:
                    pass
                else:
                    continue

            try:
                selection = getattr(regions_, region)
            except AttributeError:
                continue

            for variable in variables:

                if not variable:
                    continue

                # unitary sample for discovery fit
                if sample == 'Unitary':
                    name = 'hUnitaryNom_%s_obs_cuts' % region_name
                    hist = ROOT.TH1F(name, name, 1, 0.5, 1.5)
                    hist.Sumw2()
                    hist.Fill(1.)
                    
                    histograms.append(hist)
                    
                    continue

                # nominal histogram
                get_histogram = partial(miniutils.get_histogram, sample, variable=variable, 
                                        region=region_name, selection=selection, 
                                        lumi=args.lumi, version=args.version)

                hist = get_histogram(syst='Nom')

                # blind SR for now
                if 'data' in sample and region_name.startswith('SR') and not args.unblind:
                    hist.SetBinContent(1, 0.0)

                # jet fakes in SR (from extrapolation)
                if sample.startswith('jfake') and region_name.startswith('SR') and variable == 'cuts':
                    if region_type == 'L':
                        hist.SetBinContent(1, 0.06)
                    elif region_type == 'H':
                        hist.SetBinContent(1, 0.00002)
                   

                histograms.append(hist)


                if do_syst:
                    
                    if 'data' in sample:
                        continue

                    if sample not in dd:

                        # one side systematics
                        for syst in systematics_expOS:
                            
                            h_low = hist.Clone(hist.GetName().replace('Nom', syst.replace('__1up', '')+'Low'))

                            h_high = get_histogram(syst=syst)
                            h_high.SetName(h_high.GetName().replace(syst, syst+'High'))

                            histograms.append(h_low)
                            histograms.append(h_high)

                        # High-Low detector systematics
                        for syst in systematics_expHL:

                            if syst in ['MET_SoftTrk_Scale', ]:
                                h_low  = get_histogram(syst=syst+'Down')
                                h_high = get_histogram(syst=syst+'Up')
                            else:
                                h_low  = get_histogram(syst=syst+'__1down')
                                h_high = get_histogram(syst=syst+'__1up')

                            histograms.append(h_low)
                            histograms.append(h_high)
                    
                        # # btag: only in the regions with bjet tag/veto
                        # if 'CRL' in region_name:
                        #     for syst in ['BJET', 'CJET', 'BMISTAG']:
                            
                        #         h_low  = get_histogram(sample, variable, region_name, selection, syst+'DOWN')
                        #         h_high = get_histogram(sample, variable, region_name, selection, syst+'UP')

                        #         histograms.append(h_low)
                        #         histograms.append(h_high)


                    # data driven
                    ## efakes 
                    if sample.startswith('efake'):
                        
                        h_low = get_histogram(syst='FegLow')
                        h_high = get_histogram(syst='FegHigh')

                        if h_high.GetBinContent(1) < fzero:
                            h_high.Fill(1, 0.045)
                            
                        histograms.append(h_low)
                        histograms.append(h_high)

                    ## jet fakes 
                    if sample.startswith('jfake'):
                    
                        h_high = get_histogram(syst='FjgLow')
                        h_low  = get_histogram(syst='FjgHigh')

                        # in SR (from extrapolation)
                        if sample.startswith('jfake') and region_name.startswith('SR') and variable == 'cuts':
                            if region_type == 'L':
                                h_low.SetBinContent(1, 0.04)
                                h_high.SetBinContent(1, 0.07)
                            elif region_type == 'H':
                                h_low.SetBinContent(1, 0.00001)
                                h_high.SetBinContent(1, 0.00003)

                        histograms.append(h_low)
                        histograms.append(h_high)


                    # theoretical 
                    syst = None
                    sigma, sigma_up, sigma_dn = None, None, None
                        
                    ## photonjet
                    if sample == 'photonjet':

                        syst = 'theoSysGJ'
                        sigma = 0.45 # FIX: ~ from Run 1

                    # ## ttbar
                    # if sample == 'ttbar':
                    #     syst = 'theoSysTop'
                    #     sigma = 1.

                    ## ttbargamma
                    if 'ttbarg' in sample:
                        syst = 'theoSysTopG'
                        sigma = 0.2 # FIX: ~ from Run 1

                    # ## single top gamma
                    # if 'topgamma' in sample:
                    #     syst = 'theoSysSingleTopG'
                    #     sigma = 0.068 #6.8 (%) cross section (stop wt channel note)

                    ## wgamma
                    if 'wgamma' in sample:
                        syst = 'theoSysWG'
                        sigma = 0.2 # FIX ~ from Run 1
                    
                    ## zgamma
                    if ('zllgamma' in sample) or ('znunugamma' in sample):
                        syst = 'theoSysZG'
                        sigma = 1   ##guestimate

                    # ## diboson
                    # if 'diboson' in sample:
                    #     syst = 'theoSysVV'
                    #     sigma = 1.   ##guestimate

                    ## signal
                    if 'GGM_M3' in sample:
                        syst = 'SigXSec'

                        m3 = int(sample.split('_')[3]) #extract M3 value from sample name
                        sigma = gg_xs_unc.get(m3, 0.) #get relative uncertainty
                        
                    
                    if 'GGM_mu' in sample:
                        syst = 'SigXSec'
                        
                        mu = int(sample.split('_')[2]) # extract mu value
                        # sigma = theoSysSigXsecNumberEWK.get(mu, 0.)


                    if syst is not None:
                        
                        if sigma_up is None and sigma_dn is None:
                            sigma_up = sigma
                            sigma_dn = sigma

                        h_high = hist.Clone(hist.GetName().replace('Nom', syst+'High'))
                        h_high.Scale(1 + sigma_up)
                        
                        h_low =  hist.Clone(hist.GetName().replace('Nom', syst+'Low'))
                        h_low.Scale(1 - sigma_dn)

                        histograms.append(h_high)
                        histograms.append(h_low)
                        

        # save histograms
        if histograms:
            with RootFile(args.output, 'update') as f:
                for hist in histograms:
                    f.write(hist)

        # if 'GGM_M3_mu' in sample:
        #     histograms_gg.update({ hist.GetName(): hist for hist in list(histograms) })
        # elif 'GGM_mu' in sample:
        #     histograms_ewk.update({ hist.GetName(): hist for hist in list(histograms) })


    # sum strong and ewk histograms
    # if histograms_gg is not None and histograms_ewk is not None:
        
    #     histograms = []

    #     for name, hist in histograms_gg.iteritems():
            
    #         mu = re.findall(r'\d+', name.split('_')[4])[0] #extract mu value from sample name

    #         # get the correspondent ewk point
    #         for ewkmu in ewkdict.itervalues():
    #             if ewkmu == int(mu):
    #                 break
    #         else:
    #             ewkmu = int(strong_ewk_fix[mu])
                
    #         ewk_name = 'hGGM_mu_' + '_'.join(name.replace(mu, str(ewkmu)).split('_')[4:])

    #         h = hist.Clone(name.replace('GGM_M3_mu', 'GGM_M3_mu_all'))
            
    #         # sum ewk contribution only if > 0
    #         if histograms_ewk[ewk_name].GetBinContent(1) > fzero:
    #             h.Add(histograms_ewk[ewk_name], 1.0)

    #         histograms.append(h)

    #     with RootFile(args.output, 'update') as f:
    #         for hist in histograms:
    #             f.write(hist)



if __name__ == '__main__':
    sys.exit(main())
