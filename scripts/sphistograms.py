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
from systematics import all_systematics

fzero = 0.0001

def main():

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-o', '--output', help='output file name', required=True)

    # samples, regions, variables
    parser.add_argument('-v', dest='variables', default='cuts', help='variables (comma separated)')
    parser.add_argument('-r', dest='regions', help='regions (comma separated)')
    parser.add_argument('-s', dest='samples', help='samples (comma separated)')
    parser.add_argument('-n', help='"L" or "H"', required=True)

    parser.add_argument('--dosyst', action='store_true')

    args = parser.parse_args()
    
    variables = args.variables.split(',')

    region_number = args.n
    
    if args.regions is None:
        args.regions = 'SR,CRQ,CRW,CRT'
        
    regions = [ '%s_%s' % (r, region_number) for r in args.regions.split(',') ]
   
    mc = [
        'wgamma',
        'zllgamma',
        'znunugamma',
        #'ttbar',
        'ttbarg',
        'photonjet',
        #'multijet',
        #'wjets',
        #'zjets',
        ]

    dd = ['efake', 'jfake']

    signals = [ 'GGM_M3_mu_%i_%i' % (m3, mu) for (m3, mu) in mass_dict.keys() ]

    histograms_ewk, histograms_gg = None, None

    data = ['data',]

    samples = []
    if args.samples is not None:
        if 'signal' in args.samples:
            samples.extend(signals)
            histograms_gg = dict()
            histograms_ewk = dict()
        elif 'mc' in args.samples:
            samples.extend(mc)
        elif 'dd' in args.samples:
            samples.extend(dd)
        elif 'data' in args.samples:
            samples.extend(data)
        else:
            samples = args.samples.split(',')
    else:
        samples = mc + data + signals +dd
        histograms_gg = dict()
        histograms_ewk = dict()

    # Systematics
    do_syst = args.dosyst

    ## high-low systematics
    systematics_expHL = [
        'EG_RESOLUTION_ALL',
        'EG_SCALE_ALL',
        'MUONS_SCALE',
        'MUONS_MS',
        'MUONS_ID',
        'JET_GroupedNP_1',
        'JET_GroupedNP_2',
        'JET_GroupedNP_3',
        'MET_SoftTrk_Scale',
        ]

    ## one-sided systematics
    systematics_expOS = [
        'MET_SoftTrk_ResoPara',
        'MET_SoftTrk_ResoPerp',
        'JET_JER_SINGLE_NP__1up',
    ]

    # signal xs: signal cross section uncertainty depends only on gluion mass (~M3) -->dict key
    

    # create histograms
    for sample in samples:

        print 'Processing sample %s ...' % sample

        histograms = []

        for region in regions:

            region_number = region.split('_')[-1]
            region_name = region.split('_')[0]
            
            if 'GGM' in sample:
                if region_name in ['SR', 'CRQ', 'CRW', 'CRT']:
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

                get_histogram = partial(miniutils.get_histogram, sample, variable=variable, region=region_name, selection=selection, lumi='data')

                hist = get_histogram(syst='Nom')

                # blind SR for now
                if 'data' in sample and region_name == 'SR':
                    hist.SetBinContent(1, 0.0)


                #name = hist.GetName() 
                #hist.SetName(name.replace('met_et', 'met'))
               
                histograms.append(hist)

                if do_syst:

                    if sample in data:
                        continue

                    # one side systematics
                    for syst in systematics_expOS:

                        if sample in dd:
                            h_low  = hist.Clone(hist.GetName().replace('Nom', syst+'Low'))
                            h_high = hist.Clone(hist.GetName().replace('Nom', syst+'High'))

                        else:
                            h_low = hist.Clone(hist.GetName().replace('Nom', syst+'Low'))

                            h_high = get_histogram(syst=syst)
                            h_high.SetName(h_high.GetName().replace(syst, syst+'High'))

                        histograms.append(h_low)
                        histograms.append(h_high)

                    # High-Low detector systematics
                    for syst in systematics_expHL:

                        if sample in dd:
                            h_low  = hist.Clone(hist.GetName().replace('Nom', syst+'Low'))
                            h_high = hist.Clone(hist.GetName().replace('Nom', syst+'High'))
                        else:
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

                    # # jes systematics
                    # if not sample in dd:
                    #     for syst in systematics_jes:

                    #         h_low  = get_histogram(sample, variable, region_name, selection, syst+'Down')
                    #         h_high = get_histogram(sample, variable, region_name, selection, syst+'Up')

                    #         histograms.append(h_low)
                    #         histograms.append(h_high)
                           


                    # # data driven
                    # ## efakes 
                    # if sample == 'efake':
                        
                    #     syst = 'eFakeRate'
                    #     efakeUpperUnc = 0.03 #upper limit in case of zero-events

                    #     h_high = get_histogram(sample, variable, region_name, selection, 'EFAKE')
                    #     h_high.SetName(h_high.GetName().replace('EFAKE', syst+'High'))

                    #     if h_high.GetEntries() == 0:
                    #         h_high.Fill(1, efakeUpperUnc)
                        
                    #     h_low = hist.Clone(hist.GetName().replace('Nom', syst+'Low'))

                    #     histograms.append(h_low)
                    #     histograms.append(h_high)

                    # ## jet fakes 
                    # if sample == 'jfake':
                    
                    #     syst = 'jFakeRate'
                    #     sigma = 0.1   ##guesstimate

                    #     h_high = get_histogram(sample, variable, region_name, selection, 'JFAKEUP')
                    #     h_low  = get_histogram(sample, variable, region_name, selection, 'JFAKEDOWN')

                    #     histograms.append(h_low)
                    #     histograms.append(h_high)


                    # theoretical 
                    syst = None
                    sigma, sigma_up, sigma_dn = None, None, None
                        
                    ## photonjet
                    if sample == 'photonjet_sherpa':

                        # ### generator (vs Pythia)
                        # syst = 'theoSysGJgen'

                        # h_low = get_histogram('photonjet_pythia', variable, region_name, selection)
                        # h_low.SetName(hist.GetName().replace('Nom', syst+'High'))

                        # h_high = hist.Clone(hist.GetName().replace('Nom', syst+'Low'))

                        # histograms.append(h_low)
                        # histograms.append(h_high)
                        
                        ### difference between sherpa and pythia at truth level
                        syst = 'theoSysGJ'
                        sigma = 1.

                    # ## ttbar
                    # if sample == 'ttbar':
                    #     syst = 'theoSysTop'
                    #     sigma = 1.

                    ## ttbargamma
                    if 'ttbarg' in sample:
                        syst = 'theoSysTopG'
                        sigma = 1

                    # ## single top gamma
                    # if 'topgamma' in sample:
                    #     syst = 'theoSysSingleTopG'
                    #     sigma = 0.068 #6.8 (%) cross section (stop wt channel note)

                    ## wgamma
                    if 'wgamma' in sample:
                        syst = 'theoSysWG'
                        sigma = 1
                    
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

                        m3 = sample.split('_')[3] #extract M3 value from sample name
                        sigma = gg_xs_unc.get(m3, 0.) #get relative uncertainty
                        
                    
                    if 'GGM_mu' in sample:
                        syst = 'SigXSec'
                        
                        mu = sample.split('_')[2] # extract mu value
                        sigma = theoSysSigXsecNumberEWK.get(mu, 0.)


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
