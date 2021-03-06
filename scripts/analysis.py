#! /usr/bin/env python


#                        -c   +------------------+   -f     +-----------+  -t
#                      +----> | cuts histograms  +--------> | workspace +------> Tables
#                      |      +------------------+   Fit    +-----+-----+
#   +--------------+   |                                          |
#   | mini ntuples +---+                                          | mu (CR -> SR)
#   +--------------+   |                                          |
#      |- Data         |      +------------------+                |        -p
#      |- MC           +----> | plots histograms +----------------+------------> Plots
#      |- Fakes          -d   +------------------+

import os
import sys
import argparse
import subprocess
import datetime
from functools import partial
from collections import OrderedDict

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)

import miniutils
import systematics as systematics_
import regions as regions_
from fitutils import get_normalization_factors
from drawutils import do_plot, do_pull_plot
from yieldstable import yieldstable, get_fit_results
from systable import systable
from utils import mkdirp, run_cmd
from rootutils import set_atlas_style

fzero = 0.0001

def do_histograms(output_path, regions, samples, do_det_syst, do_dd_syst, do_mc_syst, year, version, unblind=False,
                  ignore_missing=False):

    # Systematics
    ## high-low systematics
    systematics_exp_hl = systematics_.get_high_low_systematics()

    ## one-sided systematics
    systematics_exp_os = systematics_.get_one_side_systematics()

    # Histograms "manager"
    hlist = []

    # create histograms
    for sample in samples:

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
                             variables=['cuts'], regions=regions, selections=selections,
                             year=year, version=version, ignore_missing=ignore_missing)


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
        if do_det_syst:

            if (not sample.startswith('efake') and
                not sample.startswith('jfake') and
                not 'data' in sample):
                # and
                #                not 'GGM' in sample):

                # one side systematics
                for syst in systematics_exp_os:
                    systematics_list.append(syst)

                # High-Low detector systematics
                for syst in systematics_exp_hl:
                    systematics_list.append(syst+'__1down')
                    systematics_list.append(syst+'__1up')


        # Get histograms
        histograms = get_events(systematics=systematics_list)

        # Data
        if sample == 'data':

            for (hname, mean, unc) in histograms:

                # blind SR for now
                if 'SR' in hname and not unblind:
                    mean, unc = 0., 0.

                hlist.append((hname, mean, unc))


        # jet fakes
        elif sample == 'jfake':

        #     # SRs
        #     if 'SRL200' in regions:
        #         hlist.append(('hjfakeNom_SRL200_obs_cuts',      0.35, 0.35))
        #         hlist.append(('hjfakeNom_SRL200_obs_cutsNorm',  1.00, 0.00))

        #         hlist.append(('hjfakeJFAKE_STATLow_SRL200_obs_cuts',  fzero, fzero))
        #         hlist.append(('hjfakeJFAKE_STATHigh_SRL200_obs_cuts', 0.70, fzero))
        #         hlist.append(('hjfakeJFAKE_SYSTLow_SRL200_obs_cuts',  0.27, 0.27))
        #         hlist.append(('hjfakeJFAKE_SYSTHigh_SRL200_obs_cuts', 0.43, 0.43))

        #     if 'SRL300' in regions:
        #         hlist.append(('hjfakeNom_SRL300_obs_cuts',      0.07,     0.07))
        #         hlist.append(('hjfakeNom_SRL300_obs_cutsNorm',  7.142857, 0.00))

        #         hlist.append(('hjfakeJFAKE_STATLow_SRL300_obs_cuts',  fzero, fzero))
        #         hlist.append(('hjfakeJFAKE_STATHigh_SRL300_obs_cuts', 0.51, 0.51))
        #         hlist.append(('hjfakeJFAKE_SYSTLow_SRL300_obs_cuts',  0.01, 0.01))
        #         hlist.append(('hjfakeJFAKE_SYSTHigh_SRL300_obs_cuts', 0.15, 0.15))

        #     if 'SRH' in regions:
        #         hlist.append(('hjfakeNom_SRH_obs_cuts',       0.01, 0.01))
        #         hlist.append(('hjfakeNom_SRH_obs_cutsNorm',  50.00, 0.00))

        #         hlist.append(('hjfakeJFAKE_STATLow_SRH_obs_cuts',  fzero, fzero))
        #         hlist.append(('hjfakeJFAKE_STATHigh_SRH_obs_cuts', 0.51, 0.51))
        #         hlist.append(('hjfakeJFAKE_SYSTLow_SRH_obs_cuts',  fzero, fzero))
        #         hlist.append(('hjfakeJFAKE_SYSTHigh_SRH_obs_cuts', 0.09, 0.09))

            for (hname, mean, unc) in histograms:

                # if 'SR' in hname:
                #     continue

                rname = hname.split('_')[1]

                hlist.append((hname, mean, unc))
                if 'Nom' in hname:

                    try:
                        ratio = unc/mean
                    except:
                        ratio = 0.

                    hlist.append((hname+'Norm', ratio, 0.))

                    hlist.append(('hjfakeJFAKE_STATLow_%s_obs_cuts' % rname,  mean-unc, 0.))
                    hlist.append(('hjfakeJFAKE_STATHigh_%s_obs_cuts' % rname, mean+unc, 0.))

        # e fakes
        elif sample == 'efake':

        #     # SRH
        #     if 'SRH' in regions:
        #         hlist.append(('hefakeNom_SRH_obs_cuts',            0.044, 0.044))
        #         hlist.append(('hefakeNom_SRH_obs_cutsNorm',        1.000, 0.000))

        #         hlist.append(('hefakeEFAKE_STATLow_SRH_obs_cuts',  fzero, fzero))
        #         hlist.append(('hefakeEFAKE_STATHigh_SRH_obs_cuts', 0.044, 0.044))
        #         hlist.append(('hefakeEFAKE_SYSTLow_SRH_obs_cuts',  0.038, 0.038))
        #         hlist.append(('hefakeEFAKE_SYSTHigh_SRH_obs_cuts', 0.050, 0.050))

            for (hname, mean, unc) in histograms:

                rname = hname.split('_')[1]

                hlist.append((hname, mean, unc))
                if 'Nom' in hname:

                    try:
                        ratio = unc/mean
                    except:
                        ratio = 0.

                    hlist.append((hname+'Norm', ratio, 0.))

                    hlist.append(('hefakeEFAKE_STATLow_%s_obs_cuts' % rname,  mean-unc, 0.))
                    hlist.append(('hefakeEFAKE_STATHigh_%s_obs_cuts' % rname, mean+unc, 0.))


        # MC SUSY signal
        elif 'GGM' in sample:

            for (hname, mean, unc) in histograms:

                hlist.append((hname, mean, unc))

                # if 'Nom' in hname:

                #     xs, unc = get_xs_from_did(sample, 2)

                #     mean_dn = mean * (1-unc)
                #     mean_up = mean * (1+unc)

                #     e_dn = unc * (1-unc)
                #     e_up = unc * (1+unc)

                #     hlist.append((hname.replace('Nom', 'SigXSecLow'),  mean_dn, e_dn))
                #     hlist.append((hname.replace('Nom', 'SigXSecHigh'), mean_up, e_up))



        # MC
        else:

            for (hname, mean, unc) in histograms:

                rname = hname.split('_')[1]

                hlist.append((hname, mean, unc))



    # close/save histograms
    output_name_txt  = output_path.replace('.root', '.txt')
    output_name_root = output_path

    with open(output_name_txt, 'w+') as f:
        for (name, val, err) in hlist:
            lout = '{0: <80}          {1:.6f}  {2:.6f}\n'.format(name, val, err)
            f.write(lout)

    fin = ROOT.TFile(output_name_root, 'recreate')

    for (name, val, err) in hlist:

        hist = ROOT.TH1D(name, name, 1, 0.5, 1.5)

        hist.SetBinContent(1, val)
        hist.SetBinError(1, err)

        hist.Write(name)

    fin.Close()


def do_bkgonlyfit(configfile, input_file, output_dir, region, lumi, do_validation=False, syst='', use_mc=False, logfile=None, hf_options=None):

    configfile  = os.path.abspath(configfile)
    input_file  = os.path.abspath(input_file)
    output_dir  = os.path.abspath(output_dir)

    if not os.path.exists(output_dir):
        mkdirp(output_dir)

    # move to analysis directory
    old_pwd = os.getenv('PWD')
    susy_dir = os.environ['SUSY_ANALYSIS']
    os.chdir(susy_dir + '/run')

    # Run HistFitter
    opttag = ''
    if use_mc:
        opttag += '_mc'

    if opttag:
        results_dir = 'results/PhotonMetAnalysis_bkgonly%s' % opttag
    else:
        results_dir = 'results/PhotonMetAnalysis_bkgonly'

    options = '-i %s --sr %s --rm --lumi %.2f' % (input_file, region, lumi)
    if do_validation:
        options += ' --val'
    if syst:
        options += syst
    if use_mc:
        options += ' --mc'

    hf_extra_options = ''
    if hf_options is not None:
        hf_extra_options = hf_options

    cmd = 'HistFitter.py -u \'"%s"\' -w -f -V -F bkg %s %s' % (options, hf_extra_options, configfile)
    run_cmd(cmd, logfile='hf.log', stdout=True)

    # mv logfile
    if logfile is not None:
        os.system('mv hf.log %s' % os.path.join(old_pwd, logfile))

    # mv from results dir to output dir
    mv_cmd = 'cp %s/* %s/' % (results_dir, output_dir)
    os.system(mv_cmd)

    os.chdir(old_pwd)



def do_tables(ws, output_dir, backgrounds, regions, sr_str, do_validation, unblind=False, do_syst_tables=False, norm_dict={}):

    backgrounds_str = ','.join(backgrounds)

    ## CR
    yieldstable(ws, backgrounds_str, 'CRQ,CRW,CRT', output_dir+'/table_cr.tex', 'Control Regions', show_cr_info=True, cr_dict=norm_dict)

    ## VR
    if do_validation:
        yieldstable(ws, backgrounds_str, 'VRQ,VRM1L,VRM2L,VRM1H,VRM2H', output_dir+'/table_vrm.tex', 'VRM')

        yieldstable(ws, backgrounds_str, 'VRL1,VRL2,VRL3,VRL4', output_dir+'/table_vrl.tex', 'VRL')

        yieldstable(ws, backgrounds_str, 'VRE', output_dir+'/table_vre.tex', 'Fakes VR')

    ## SR
    yieldstable(ws, backgrounds_str, sr_str, output_dir+'/table_sr.tex', 'Signal Regions', unblind=unblind)

    # Systematic tables
    if do_syst_tables:
        systable(ws, '', 'SRL200', '%s/table_syst_srl200.tex' % output_dir)
        systable(ws, '', 'SRL300', '%s/table_syst_srl300.tex' % output_dir)
        systable(ws, '', 'SRH',    '%s/table_syst_srh.tex' % output_dir)

        systable(ws, '', 'CRQ', '%s/table_syst_crq.tex' % output_dir)
        systable(ws, '', 'CRW', '%s/table_syst_crw.tex' % output_dir)
        systable(ws, '', 'CRT', '%s/table_syst_crt.tex' % output_dir)

        # for bkg in backgrounds:
        #     systable(ws, bkg,             sr_str, '%s/table_syst_%s.tex' % (output_dir, bkg))

        if do_validation:
            systable(ws, '', 'VRL1', '%s/table_syst_vrl1.tex' % output_dir)
            systable(ws, '', 'VRL2', '%s/table_syst_vrl2.tex' % output_dir)
            systable(ws, '', 'VRL3', '%s/table_syst_vrl3.tex' % output_dir)
            systable(ws, '', 'VRL4', '%s/table_syst_vrl4.tex' % output_dir)
            systable(ws, '', 'VRQ',   '%s/table_syst_vrq.tex' % output_dir)
            systable(ws, '', 'VRM1L', '%s/table_syst_vrm1l.tex' % output_dir)
            systable(ws, '', 'VRM1H', '%s/table_syst_vrm1h.tex' % output_dir)
            systable(ws, '', 'VRM2L', '%s/table_syst_vrm2l.tex' % output_dir)
            systable(ws, '', 'VRM2H', '%s/table_syst_vrm2h.tex' % output_dir)



def do_plots_histograms(output_path, regions, samples, variables, year, version, ignore_missing=False):

    syst = 'Nom' # only nominal for now

    selections = []
    for region in regions:
        selections.append(getattr(regions_, region))

    get_histograms = partial(miniutils.get_histograms, year=year, version=version, syst=syst,
                             variables=variables, regions=regions, selections=selections, ignore_missing=ignore_missing)

    for sample in samples:

        hlist = get_histograms(sample)

        fin = ROOT.TFile(output_path, 'update')

        for hist in hlist:
            hist.Write(hist.GetName(), ROOT.TObject.kOverwrite)

        fin.Close()


def prepare_histograms_for_plots(input_path, output_path, regions, backgrounds, variables,
                                 ws=None, merge_dict={}, norm_dict={}):

    syst = 'Nom' # only nominal for now

    file_ = ROOT.TFile.Open(input_path)

    h_data = []

    h_bkg       = { name: [] for name in backgrounds }

    for region in regions:

        for variable in variables:

            ## data
            h_data.append(get_histogram_from_file(file_, 'data', variable, region, ''))

            ## backgrounds
            for name in backgrounds:
                h_bkg[name].append(get_histogram_from_file(file_, name, variable, region, syst))

    # Scale background with scale factors, if workspace not None
    if ws is not None and norm_dict:

        mus = get_normalization_factors(ws)

        for cr, bkg in norm_dict.items():
            if cr in mus:
                mu = mus[cr]
                for hist in h_bkg[bkg]:
                    hist.Scale(mu[0])

    # Merge backgrounds to plot
    if merge_dict:

        for merge_name, merge_list in merge_dict.items():

            h_bkg[merge_name] = [ hist.Clone(hist.GetName().replace(merge_list[0], merge_name)) for hist in h_bkg[merge_list[0]] ]

            for name in merge_list[1:]:
                for h1, h2 in zip(h_bkg[merge_name], h_bkg[name]):
                    h1.Add(h2, 1)

            for name in merge_list:
                del h_bkg[name]


    fin = ROOT.TFile(output_path, 'recreate')

    for hist in h_data:
        hist.Write(hist.GetName())
    for hlist in h_bkg.itervalues():
        for hist in hlist:
            hist.Write(hist.GetName())

    fin.Close()



def get_histogram_from_file(file_, sample, variable, region, syst='Nom'):

    if sample.startswith('data'):
        syst = ''

    hname = 'h%s%s_%s_obs_%s' % (sample, syst, region, miniutils.get_escaped_variable(variable))
    hist = file_.Get(hname)
    hist.SetDirectory(0)

    return hist.Clone()


def do_plots(histograms_path, output_dir, regions, backgrounds, variables, data_label, unblind=False, output_label='afterFit'):

    # histograms file
    file_ = ROOT.TFile.Open(histograms_path)

    syst = 'Nom'

    # Standard DATA/Backgrounds plot
    for region in regions:

        for variable in variables:

            ## data
            if region.startswith('SR') and not unblind:
                continue #h_data = None

            print 'plotting %s in region %s ...' % (variable, region)

            h_data = get_histogram_from_file(file_, 'data', variable, region, syst)

            ## backgrounds
            h_bkg = OrderedDict()

            for name in backgrounds:
                h_bkg[name] = get_histogram_from_file(file_, name, variable, region, syst)


            ## signal
            h_signal = None
            # if args.signal:
            #     h_signal = OrderedDict()

            #     if 'SRL' in region:
            #         signal1 = 'GGM_GG_bhmix_1900_450'
            #         signal2 = 'GGM_GG_bhmix_1900_650'
            #     elif 'SRH' in region:
            #         signal1 = 'GGM_GG_bhmix_1900_1810'
            #         signal2 = 'GGM_GG_bhmix_1900_1860'
            #     else:
            #         signal1 = 'GGM_GG_bhmix_1900_650'
            #         signal2 = 'GGM_GG_bhmix_1900_1650'

            #     h_signal[signal1] = get_histogram(signal1, variable=variable, region=region_name, selection=selection, syst=syst)
            #     h_signal[signal2] = get_histogram(signal2, variable=variable, region=region_name, selection=selection, syst=syst)

            varname = variable.replace('[', '').replace(']', '')

            outname = os.path.join(output_dir, 'can_{}_{}_{}'.format(region, varname, output_label))

            do_plot(outname, variable, data=h_data, bkg=h_bkg, signal=h_signal, region_name=region, do_ratio=True, data_label=data_label)


    file_.Close()



# Regions pull pot
def do_regions_pull_plot(ws, output_name, backgrounds, plot_bkgs, regions, merge_dict={}, unblind=False, data_label='', plot_significance=False):

    backgrounds_str = ','.join(backgrounds)
    regions_str     = ','.join(regions)

    mydict = get_fit_results(ws, backgrounds_str, regions_str)

    # Create histograms
    n_regions = len(regions)

    # Make histograms
    h_obs = ROOT.TH1F('h_obs', 'h_obs', n_regions, 0, n_regions)
    h_exp = ROOT.TH1F("h_exp", "h_exp", n_regions, 0, n_regions)

    h_bkg_dict = {}
    for name in backgrounds:
        h_bkg_dict[name] = ROOT.TH1F("h_bkg_"+name,"h_bkg_"+name, n_regions, 0, n_regions)

    # loop over all the regions
    for counter, region in enumerate(regions):

        index = mydict["names"].index(region+'_cuts')

        n_obs = mydict["nobs"][index]
        n_exp = mydict["TOTAL_FITTED_bkg_events"][index]

        exp_syst = mydict["TOTAL_FITTED_bkg_events_err"][index]

        n_exp_components = []
        for sam in backgrounds:
            if "Fitted_events_"+sam in mydict:
                h_bkg_dict[sam].SetBinContent(counter+1, mydict["Fitted_events_"+sam][index])
            else:
                h_bkg_dict[sam].SetBinContent(counter+1, 0.)

        if region.find("SR")>=0 and not unblind:
            n_obs = -100

        h_obs.GetXaxis().SetBinLabel(counter+1, region)
        h_obs.SetBinContent(counter+1, n_obs)
        h_obs.SetBinErrorOption(ROOT.TH1.kPoisson)

        h_exp.SetBinContent(counter+1, n_exp)
        h_exp.SetBinError(counter+1, exp_syst)

    if merge_dict:

        for merge_name, merge_list in merge_dict.items():

            h_bkg_dict[merge_name] = h_bkg_dict[merge_list[0]].Clone(h_bkg_dict[merge_list[0]].GetName().replace(merge_list[0], merge_name))

            for name in merge_list[1:]:
                h_bkg_dict[merge_name].Add(h_bkg_dict[name], 1)

            for name in merge_list:
                del h_bkg_dict[name]

    h_bkg_dict_sorted = OrderedDict()
    for name in plot_bkgs:
        h_bkg_dict_sorted[name] = h_bkg_dict[name]

    do_pull_plot(output_name, h_obs, h_exp, h_bkg_dict_sorted, data_label=data_label, plot_significance=plot_significance)







def main():

    parser = argparse.ArgumentParser(description='analysis.py')

    # Input/output
    # version, data
    parser.add_argument('-v', '--version', help='Mini-ntuples version')
    parser.add_argument('--data', help='2015+2016 or 2017')
    parser.add_argument('-o', dest='output_dir', help='Output directory')

    # Steps
    parser.add_argument('-c', '--chist',  action='store_true', help='Do "ntuples -> cuts histograms" step')
    parser.add_argument('-d', '--dhist',  action='store_true', help='Do "ntuples -> distributions histograms" step')
    parser.add_argument('-f', '--fit',    action='store_true', help='Do "histograms -> fit" step')
    parser.add_argument('-t', '--tables', action='store_true', help='Do "fit -> tables" step')
    parser.add_argument('-p', '--plots',  action='store_true', help='Do "histograms/fit -> plots" step')


    # Systematics
    parser.add_argument('--syst', action='store_true', help='Include all systematics (detector + DD + MC)')
    parser.add_argument('--detsyst', action='store_true', help='Include detector systematics')
    parser.add_argument('--ddsyst', action='store_true', help='Include DD systematics')
    parser.add_argument('--mcsyst', action='store_true', help='Include MC systematics')

    # Extra options
    parser.add_argument('--conf', help='HistFitter config file')
    parser.add_argument('--unblind', action='store_true', help='Unblind Signal Regions! Use with caution, you can discover SUSY')
    parser.add_argument('--noval', action='store_true', help='Don\'t include Validation Regions')
    parser.add_argument('--mc', action='store_true', help='Use only MC')

    # Histogram options
    parser.add_argument('--force',  action='store_true', help='Force histogram creation')
    parser.add_argument('-s', '--sample', help='Only update histograms for this sample')

    parser.add_argument('--ignore-missing', dest='ignore_missing', action='store_true', help='Ignore missing samples. Do not use this option! ')



    args = parser.parse_args()

    step_chist   = args.chist
    step_dhist   = args.dhist
    step_fit    = args.fit
    step_tables = args.tables
    step_plots  = args.plots

    if not any([step_chist, step_dhist, step_fit, step_tables, step_plots]) or args.output_dir is None or args.version is None or args.data is None:
        parser.print_usage()
        sys.exit(1)


    # Configuration
    unblind = args.unblind
    data = args.data
    version = args.version
    do_validation = (not args.noval)
    use_mc = args.mc

    do_det_syst = False
    do_dd_syst  = False
    do_mc_syst  = False
    if args.syst:
        syst_str = ' --syst'
        do_det_syst = True
        do_dd_syst = True
        do_mc_syst = True
    else:
        syst_str = ''
        if args.detsyst:
            do_det_syst = True
            syst_str += ' --detsyst'
        if args.ddsyst:
            do_dd_syst = True
            syst_str += ' --ddsyst'
        if args.mcsyst:
            do_mc_syst = True
            syst_str += ' --mcsyst'


    # -------
    # Regions
    # -------
    srs = ['SRL200', 'SRL300', 'SRH']
    crs = ['CRQ', 'CRW', 'CRT']
    vrs = [
        'VRQ',
        'VRM1L', 'VRM2L',
        'VRM1H', 'VRM2H',
        'VRL1', 'VRL2', 'VRL3', 'VRL4',
        'VRE'
    ]

    sr_str = ','.join(srs)
    if do_validation:
        regions = crs + vrs + srs
        regions_str = '%s,%s,%s' % (','.join(srs), ','.join(crs), ','.join(vrs))
    else:
        regions = crs + srs
        regions_str = '%s,%s' % (','.join(srs), ','.join(crs))

    # -------
    # Samples
    # -------
    mc_samples = [
        'photonjet',
        'wgamma',
        'zllgamma',
        'znunugamma',
        'ttgamma',
        'diphoton',
        ]

    mc_fake_samples = [ 'ttbar', 'multijet', 'wjets', 'zjets' ]

    dd_samples = [
        'efake',
        'jfake',
        ]

    if use_mc:
        backgrounds = mc_samples + mc_fake_samples
    else:
        backgrounds = dd_samples + mc_samples

    samples = ['data', ] + backgrounds

    #backgrounds_str = 'photonjet,wgamma,[zllgamma,znunugamma],ttgamma,efake,jfake,diphoton'
    #backgrounds_str = 'photonjet,wgamma,[zllgamma,znunugamma],ttgamma'
    backgrounds_str = ','.join(backgrounds)

    # -----
    # Plots
    # -----
    plot_variables = [
        'ph_pt[0]',
        'jet_n',
        'bjet_n',
        'jet_pt[0]',
        'met_et',
        'ht',
        'meff',
        'dphi_jetmet',
        'dphi_gammet',
        'dphi_gamjet',
        'rt4',
        ]

    #plot_bkgs = ['photonjet', 'wgamma','zgamma', 'fakes', 'ttgamma', 'diphoton']
    plot_bkgs = ['photonjet', 'wgamma','zgamma', 'efake', 'jfake', 'ttgamma', 'diphoton']

    plot_regions = regions

    plot_bkg_merge_dict = {
        'zgamma': ['zllgamma', 'znunugamma',],
        #'fakes': ['efake', 'jfake']
        }

    plot_bkg_norm_dict = {
        'CRQ': 'photonjet',
        'CRW': 'wgamma',
        'CRT': 'ttgamma',
        }


    lumi = 0.
    for year in data.split('+'):
        lumi += miniutils.lumi_dict.get(year, 0.)

    lumi /= 1000.

    data_label = '#sqrt{s} = 13 TeV, %.1f fb^{-1}' % lumi

    # ------------------
    # Results output dir
    # ------------------
    susy_dir = os.environ['SUSY_ANALYSIS']

    results_dir = args.output_dir

    log_dir        = '%s/log'        % results_dir
    histograms_dir = '%s/histograms' % results_dir
    fit_dir        = '%s/fit'        % results_dir
    tables_dir     = '%s/tables'     % results_dir
    plots_dir      = '%s/plots'      % results_dir

    mkdirp(results_dir)
    mkdirp(log_dir)
    mkdirp(histograms_dir)
    mkdirp(fit_dir)
    mkdirp(tables_dir)
    mkdirp(plots_dir)


    #-------------------
    # Create Histograms
    #-------------------
    histograms_txt_path = '%s/histograms_cuts.txt' % (histograms_dir)
    histograms_path     = '%s/histograms_cuts.root' % (histograms_dir)

    if step_chist and (not os.path.isfile(histograms_path) or args.force):
        print('Creating cuts histograms ...')
        do_histograms(histograms_path, regions, samples, do_det_syst, do_dd_syst, do_mc_syst, data, version, unblind,
                      ignore_missing=args.ignore_missing)

    # Observables distributions
    histograms_plots_path           = '%s/histograms_plots.root' % (histograms_dir)
    histograms_plots_before_path    = '%s/histograms_plots_before.root' % (histograms_dir)
    histograms_plots_after_path     = '%s/histograms_plots_after.root' % (histograms_dir)

    if step_dhist and (not os.path.isfile(histograms_plots_path) or args.force or args.sample is not None):
        print('Creating histograms for plots ...')

        if args.force and os.path.isfile(histograms_plots_path):
            os.remove(histograms_plots_path)

        if args.sample is not None:
            do_plots_histograms(histograms_plots_path, plot_regions, args.sample.split(','), plot_variables, data, version)
        else:
            do_plots_histograms(histograms_plots_path, plot_regions, samples, plot_variables, data, version, ignore_missing=args.ignore_missing)


    #--------------
    # Bkg-only Fit
    #--------------
    if args.conf is not None:
        configfile = os.path.abspath(args.conf)
    else:
        configfile = susy_dir + '/lib/PhotonMet_HistFitter_config.py'

    ws = fit_dir + "/BkgOnlyFit_combined_BasicMeasurement_model_afterFit.root"

    if step_fit:
        print('Performing bkg-only fit ...')
        do_bkgonlyfit(configfile, histograms_path, fit_dir, sr_str, lumi, do_validation, syst_str, use_mc, '%s/bkgonlyfit.log' % log_dir, hf_options='-D correlationMatrix') #  -m ALL


    #--------
    # Tables
    #--------
    if step_tables:
        print('Creating tables ...')
        do_tables(ws, tables_dir, backgrounds, regions, sr_str, do_validation, unblind, (do_det_syst or do_mc_syst or do_dd_syst), plot_bkg_norm_dict)


    #-------
    # Plots
    #-------
    if step_plots:

        print('Preparing histograms for plots...')
        prepare_histograms_for_plots(histograms_plots_path, histograms_plots_before_path, plot_regions, backgrounds, plot_variables, merge_dict=plot_bkg_merge_dict)
        prepare_histograms_for_plots(histograms_plots_path, histograms_plots_after_path,  plot_regions, backgrounds, plot_variables, merge_dict=plot_bkg_merge_dict, ws=ws, norm_dict=plot_bkg_norm_dict)


        ## Pull plot
        print('Creating pull plot ...')
        do_regions_pull_plot(ws, plots_dir+'/regions_pull.pdf', backgrounds, plot_bkgs, regions, plot_bkg_merge_dict, unblind=unblind, data_label=data_label)

        #do_regions_pull_plot(ws, plots_dir+'/regions_pull_significance.pdf', backgrounds, plot_bkgs, regions, plot_bkg_merge_dict, unblind=unblind, data_label=data_label, plot_significance=True)

        set_atlas_style()

        # Before fit plots
        print('Creating before-fit plots ...')
        do_plots(histograms_plots_before_path, plots_dir, plot_regions, plot_bkgs, plot_variables, data_label, unblind=unblind, output_label='beforeFit')

        # After fit plots
        print('Creating after-fit plots ...')
        do_plots(histograms_plots_after_path, plots_dir, plot_regions, plot_bkgs, plot_variables, data_label, unblind=unblind, output_label='afterFit')







if __name__ == '__main__':
    main()
