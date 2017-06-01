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

import analysis 
import miniutils
import systematics as systematics_
import regions as regions_
from xsutils import get_xs

fzero = 0.0001


def sphistograms():

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-o', '--output', help='output file name', required=True)

    # samples, regions, variables
    parser.add_argument('-r', dest='regions', help='regions (comma separated)')
    parser.add_argument('-s', dest='samples', help='samples (comma separated)')

    # other options
    parser.add_argument('--add', action='store_true')
    parser.add_argument('--unblind', action='store_true')
    parser.add_argument('--version', help='Use this version')

    parser.add_argument('--syst', action='store_true')
    parser.add_argument('--detsyst', action='store_true')
    parser.add_argument('--ddsyst', action='store_true')
    parser.add_argument('--mcsyst', action='store_true')

    parser.add_argument('--lumi', help='data15, data16, data (2015+2016) or lumi in fb-1')

    args = parser.parse_args()


    # Create histograms
    if args.regions is None:
        parser.print_usage()
        sys.exit(1)
    
    regions = args.regions.split(',')
   
    samples = args.samples.split(',')
    if 'signal' in samples:
        samples.remove('signal')
        samples.extend(analysis.signal)

    # Systematics
    do_detector_syst = args.detsyst or args.syst
    do_dd_syst       = args.ddsyst or args.syst
    do_mc_syst       = args.mcsyst or args.syst
    
    ## high-low systematics
    systematics_expHL = systematics_.get_high_low_systematics()

    ## one-sided systematics
    systematics_expOS = systematics_.get_one_side_systematics()
  
    # Histograms "manager"
    hlist = []

    # create histograms
    for sample in samples:

        print 'Processing sample %s ...' % sample

        fixed_regions = []
        selections = []
        for region in regions:
            try:
                selections.append(getattr(regions_, region))
            except AttributeError:
                print 'Region %s not defined. continue...' % region
                continue

            fixed_regions.append(region)

        regions = fixed_regions

        get_events = partial(miniutils.get_multi_events, sample, 
                                 regions=regions, selections=selections, 
                                 lumi='data', version=args.version)

        systematics_list = ['Nom',]

        # DD backgrounds systematics
        if do_dd_syst:
            ## efakes 
            if sample.startswith('efake'):
                systematics_list.append('EFAKE_SYST__1down')
                systematics_list.append('EFAKE_SYST__1up')

            ## jet fakes 
            elif sample.startswith('jfake'):
                systematics_list.append('JFAKE_SYST__1down')
                systematics_list.append('JFAKE_SYST__1up')

        # Detector systematics
        if do_detector_syst:
                    
            if not sample.startswith('efake') and not sample.startswith('jfake') and not 'data' in sample:

                # one side systematics
                for syst in systematics_expOS:
                    systematics_list.append(syst)

                # High-Low detector systematics
                for syst in systematics_expHL:
                    systematics_list.append(syst+'__1down')
                    systematics_list.append(syst+'__1up')
                            
                    
        # Get histograms
        histograms = get_events(systematics=systematics_list)

        # Data
        if sample == 'data':

            for (hname, mean, unc) in histograms:

                # blind SR for now
                if 'SR' in hname and not args.unblind:
                    mean, unc = 0., 0.
                
                hlist.append((hname, mean, unc))


        # jet fakes
        elif sample == 'jfake':

            # SRs
            if 'SRL200' in regions:
                hlist.append(('hjfakeNom_SRL200_obs_cuts',  0.35, 0.35))
                hlist.append(('hjfakeJFAKE_STATLow_SRL200_obs_cuts',  fzero, fzero))
                hlist.append(('hjfakeJFAKE_STATHigh_SRL200_obs_cuts', fzero, fzero))
                hlist.append(('hjfakeJFAKE_SYSTLow_SRL200_obs_cuts',  0.27, 0.27))
                hlist.append(('hjfakeJFAKE_SYSTHigh_SRL200_obs_cuts', 0.43, 0.43))

            if 'SRL300' in regions:
                hlist.append(('hjfakeNom_SRL300_obs_cuts',  0.07, 0.07))
                hlist.append(('hjfakeJFAKE_STATLow_SRL300_obs_cuts',  fzero, fzero))
                hlist.append(('hjfakeJFAKE_STATHigh_SRL300_obs_cuts', 0.51, 0.51))
                hlist.append(('hjfakeJFAKE_SYSTLow_SRL300_obs_cuts',  0.01, 0.01))
                hlist.append(('hjfakeJFAKE_SYSTHigh_SRL300_obs_cuts', 0.15, 0.15))

            if 'SRH' in regions:
                hlist.append(('hjfakeNom_SRH_obs_cuts',  0.01, 0.01))
                hlist.append(('hjfakeJFAKE_STATLow_SRH_obs_cuts',  fzero, fzero))
                hlist.append(('hjfakeJFAKE_STATHigh_SRH_obs_cuts', 0.51, 0.51))
                hlist.append(('hjfakeJFAKE_SYSTLow_SRH_obs_cuts',  fzero, fzero))
                hlist.append(('hjfakeJFAKE_SYSTHigh_SRH_obs_cuts', 0.09, 0.09))

            for (hname, mean, unc) in histograms:
                
                if 'SR' in hname:
                    continue

                rname = hname.split('_')[1]

                hlist.append((hname, mean, unc))
                if 'Nom' in hname:
                    hlist.append(('hjfakeJFAKE_STATLow_%s_obs_cuts' % rname,  mean-unc, 0.))
                    hlist.append(('hjfakeJFAKE_STATHigh_%s_obs_cuts' % rname, mean+unc, 0.))

        # e fakes
        elif sample == 'efake':
            
            # SRH
            if 'SRH' in regions:
                hlist.append(('hefakeNom_SRH_obs_cuts',            0.044, 0.044))
                hlist.append(('hefakeEFAKE_STATLow_SRH_obs_cuts',  fzero, fzero))
                hlist.append(('hefakeEFAKE_STATHigh_SRH_obs_cuts', 0.044, 0.044))
                hlist.append(('hefakeEFAKE_SYSTLow_SRH_obs_cuts',  0.038, 0.038))
                hlist.append(('hefakeEFAKE_SYSTHigh_SRH_obs_cuts', 0.050, 0.050))

            for (hname, mean, unc) in histograms:

                if 'SRH' in hname:
                    continue

                rname = hname.split('_')[1]

                hlist.append((hname, mean, unc))
                if 'Nom' in hname:
                    hlist.append(('hefakeEFAKE_STATLow_%s_obs_cuts' % rname,  mean-unc, 0.))
                    hlist.append(('hefakeEFAKE_STATHigh_%s_obs_cuts' % rname, mean+unc, 0.))


        # MC
        else:

            for (hname, mean, unc) in histograms:

                rname = hname.split('_')[1]
                
                hlist.append((hname, mean, unc))

                # Fix one side systematics
                # for syst in systematics_expOS:
                #     syst = syst.replace('__1up', '')

                #     if syst in hname:
                #         if 'High' in hname:
                #             nom_name = hname.replace(syst+'High', 'Nom')
                #             name_up = hname #.replace(syst, syst+'High')
                #             name_dn = name_up.replace('High', 'Low')
                #         else:
                #             nom_name = hname.replace(syst, 'Nom')
                #             name_up = hname.replace(syst, syst+'High')
                #             name_dn = name_up.replace('High', 'Low')

                #             histograms[name_up] = hist.Clone(name_up)
                #             del histograms[hname]

                #         h_dn = histograms[nom_name].Clone(name_dn)
                #         histograms[name_dn] = h_dn


        
    # close/save histograms
    with open(args.output, 'w+') as f:
        for (name, val, err) in hlist:
            lout = '{0: <80}          {1:.6f}  {2:.6f}\n'.format(name, val, err)
            f.write(lout)



if __name__ == '__main__':
    sys.exit(sphistograms())


