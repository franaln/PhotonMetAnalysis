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

import analysis 

fzero = 0.0001


class HistManager:

    def __init__(self, path):
        self.path = path
        self.histograms = []

    def __del__(self):
        self.close()

    def add(self, h):
        if len(self.histograms) > 50:
            self.save()
            del self.histograms[:]

        self.histograms.append(h)

    def save(self):
        with RootFile(self.path, 'update') as f:
            for hist in self.histograms:
                f.write(hist)

    def close(self):
        if self.histograms:
            self.save()



def sphistograms():

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-o', '--output', help='output file name', required=True)

    # samples, regions, variables
    parser.add_argument('-v', dest='variables', default='cuts', help='variables (comma separated)')
    parser.add_argument('-r', dest='regions', help='regions (comma separated)')
    parser.add_argument('-s', dest='samples', help='samples (comma separated)')
    parser.add_argument('-n', help='"L" or "H"')

    parser.add_argument('--year', help='Select only MC event corresponding to this year')

    # other options
    parser.add_argument('--add', action='store_true')
    parser.add_argument('--dosyst', action='store_true')
    parser.add_argument('--unblind', action='store_true')
    parser.add_argument('--version', help='Use this version')
    parser.add_argument('--prw', action='store_true', help='Use pile-up reweighting')

    # scale to lumi?
    parser.add_argument('-i', '--input')
    parser.add_argument('--lumi', help='data15, data16, data (2015+2016) or lumi in fb-1')

    # sum 2015 and 2016
    parser.add_argument('--sum', help='Sum this two files')

    args = parser.parse_args()

    # Scale to lumi
    if args.input is not None and args.lumi is not None:
        
        if args.lumi == 'data15':
            lumi = analysis.lumi_data15
        elif args.lumi == 'data16':
            lumi = analysis.lumi_data16
        elif args.lumi == 'data':
            lumi = analysis.lumi_data15 + analysis.lumi_data16
        else:
            lumi = float(args.lumi) * 1000.
        
        lumi = lumi / 1000. # input should be normalized to 1 fb-1

        print 'Scaling histogram from %s to %s (%s fb-1)' % (args.input, args.lumi, lumi)

        infile = ROOT.TFile.Open(args.input)

        keys = [ key.GetName() for key in infile.GetListOfKeys() ]

        histograms = HistManager(args.output)

        for key in keys:

            hist = infile.Get(key)

            new_hist = hist.Clone()
            new_hist.SetDirectory(0)

            if 'data' in key or 'efake' in key or 'jfake' in key:
                pass
            else:
                new_hist.Scale(lumi)

            histograms.add(new_hist)
                
        infile.Close()
        histograms.close()

        return 0

    # Sum 2015 + 2016
    if args.sum is not None:

        files = args.sum.split(',')

        print 'Summing %s and %s to %s' % (files[0], files[1], args.output)

        infile1 = ROOT.TFile.Open(files[0])
        infile2 = ROOT.TFile.Open(files[1])

        keys = [ key.GetName() for key in infile1.GetListOfKeys() ]

        histograms = HistManager(args.output)

        for key in keys:
            if 'Unitary' in key or 'data' in key or 'efake' in key or 'jfake' in key:
                continue

            hist1 = infile1.Get(key)
            hist2 = infile2.Get(key.replace('data15', 'data16').replace('efake15', 'efake16').replace('jfake15', 'jfake16'))
            
            new_hist = hist1.Clone(hist1.GetName().replace('data15', 'data').replace('efake15', 'efake').replace('jfake15', 'jfake'))
            new_hist.SetDirectory(0)

            new_hist.Add(hist2, 1.0)

            histograms.add(new_hist)

        infile1.Close()
        infile2.Close()

        histograms.close()

        return 0


    # Create histograms
    variables = args.variables.split(',')

    region_type = args.n
    if region_type is None:
        print 'error: indicate the region type: L or H'
        return 1

    if args.regions is None or args.regions == 'all':
        args.regions = ','.join(analysis.sr_regions + analysis.cr_regions + analysis.vr_regions)
    
    regions = [ '%s_%s' % (r, region_type) for r in args.regions.split(',') ]
   
    data = ['data15', 'data16', 'data',]

    samples = []
    if args.samples is not None:
        if 'signal' in args.samples:
            samples.extend(analysis.signal)
        elif 'bkg' in args.samples:
            samples.extend(mc)
        else:
            samples = args.samples.split(',')

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

        #histograms = []
        histograms = HistManager(args.output)

        for region in regions:

            region_name, region_type = region.split('_')
            
            # don't need signal in VR
            if 'GGM' in sample:
                if region_name not in analysis.sr_regions + analysis.cr_regions:
                    continue

            try:
                selection = getattr(regions_, region)
            except AttributeError:
                print 'Region %s not defined. continue...' % region
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
                    
                    histograms.add(hist)
                    
                    continue

                # nominal histogram
                get_histogram = partial(miniutils.get_histogram, sample, variable=variable, 
                                        region=region_name, selection=selection, 
                                        lumi=args.lumi, version=args.version, year=args.year, use_prw=args.prw)

                h_nom = get_histogram(syst='Nom')

                # blind SR for now
                if 'data' in sample and region_name.startswith('SR') and not args.unblind:
                    h_nom.SetBinContent(1, 0.0)

                # jet fakes in SR (from extrapolation)
                if sample == 'jfake' and region_name.startswith('SR') and variable == 'cuts':
                    if region_type == 'L':
                        h_nom.SetBinContent(1, 0.04)
                    elif region_type == 'H':
                        h_nom.SetBinContent(1, 0.0001)

                histograms.add(h_nom)


                if do_syst:
                    
                    if 'data' in sample:
                        continue

                    if not sample.startswith('efake') and not sample.startswith('jfake'):

                        # one side systematics
                        for syst in systematics_expOS:
                            
                            h_dn = h_nom.Clone(h_nom.GetName().replace('Nom', syst.replace('__1up', '')+'Low'))

                            h_up = get_histogram(syst=syst)
                            h_up.SetName(h_up.GetName().replace(syst, syst+'High'))

                            histograms.add(h_dn)
                            histograms.add(h_up)

                        # High-Low detector systematics
                        for syst in systematics_expHL:

                            if syst in ['MET_SoftTrk_Scale', ]:
                                h_dn  = get_histogram(syst=syst+'Down')
                                h_up = get_histogram(syst=syst+'Up')
                            else:
                                h_dn  = get_histogram(syst=syst+'__1down')
                                h_up = get_histogram(syst=syst+'__1up')

                            histograms.add(h_dn)
                            histograms.add(h_up)
                    
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
                        
                        h_dn = get_histogram(syst='FegLow')
                        h_up = get_histogram(syst='FegHigh')
                        
                        if h_up.GetBinContent(1) < fzero:
                            h_up.Fill(1, 0.045)
                            
                        histograms.add(h_dn)
                        histograms.add(h_up)

                    ## jet fakes 
                    if sample.startswith('jfake'):
                    
                        h_dn = get_histogram(syst='FjgLow')
                        h_up = get_histogram(syst='FjgHigh')

                        # in SR (from extrapolation)
                        if sample == 'jfake' and region_name.startswith('SR') and variable == 'cuts':
                            if region_type == 'L':
                                h_dn.SetBinContent(1, 0.03)
                                h_up.SetBinContent(1, 0.05)
                            elif region_type == 'H':
                                h_dn.SetBinContent(1, 0.0001)
                                h_up.SetBinContent(1, 0.0001)
                            
                        histograms.add(h_dn)
                        histograms.add(h_up)


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
                    if 'zllgamma' in sample or 'znunugamma' in sample or 'zgamma' in sample:
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
                        
                    
                    if syst is not None:
                        
                        if sigma_up is None and sigma_dn is None:
                            sigma_up = sigma
                            sigma_dn = sigma

                        h_up = h_nom.Clone(h_nom.GetName().replace('Nom', syst+'High'))
                        h_up.Scale(1 + sigma_up)
                        
                        h_dn =  h_nom.Clone(h_nom.GetName().replace('Nom', syst+'Low'))
                        h_dn.Scale(1 - sigma_dn)

                        histograms.add(h_up)
                        histograms.add(h_dn)
                        

        # close/save histograms
        histograms.close()



if __name__ == '__main__':
    sys.exit(sphistograms())
