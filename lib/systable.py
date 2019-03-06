#!/usr/bin/env python

import os
import sys
import ROOT

try:
    import cPickle as pickle
except:
    import pickle

from latextable import LatexTable
from yieldstable import labels_latex_dict

ROOT.gSystem.Load('%s/lib/libSusyFitter.so' % os.getenv('HISTFITTER'))
ROOT.gInterpreter.ProcessLine('#include "{0}/src/Utils.h" '.format(os.getenv('HISTFITTER')))

from ROOT import Util
from cmdLineUtils import getPdfInRegions, getName

systdict = {
    'alpha_EG_RESOLUTION_ALL': '$e/\\gamma$ resolution',
    'alpha_EG_SCALE_ALL':      '$e/\\gamma$ scale',
    'alpha_EG_SCALE_AF2':      '$e/\\gamma$ scale (AF2)',

    'alpha_PH_EFF_ID_Uncertainty': 'Photon ID',
    'alpha_PH_EFF_ISO_Uncertainty': 'Photon Isolation',
    'alpha_PH_EFF_TRIGGER_Uncertainty': 'Photon Trigger',

    'alpha_EL_EFF_ID_TOTAL_1NPCOR_PLUS_UNCOR': 'Electron ID eff.',
    'alpha_EL_EFF_Iso_TOTAL_1NPCOR_PLUS_UNCOR': 'Electron iso. eff.',
    'alpha_EL_EFF_Reco_TOTAL_1NPCOR_PLUS_UNCOR': 'Electron reco. eff.',
    'alpha_EL_EFF_Trigger_TOTAL_1NPCOR_PLUS_UNCOR': 'Electron trigger eff.',

    'alpha_MUON_SCALE': 'Muon scale',
    'alpha_MUON_MS': 'Muon MS',
    'alpha_MUON_ID': 'Muon ID',
    'alpha_MUON_SAGITTA_RESBIAS': 'Muon SAGITTA ResBias',
    'alpha_MUON_SAGITTA_RHO': 'Muon SAGITTA RHO...',

    'alpha_MUON_EFF_RECO_STAT': 'Muon reco. efficiency stat.',
    'alpha_MUON_EFF_RECO_SYS':  'Muon reco. efficiency syst.',
    'alpha_MUON_EFF_ISO_STAT':  'Muon isolation efficiency stat.',
    'alpha_MUON_EFF_ISO_SYS':   'Muon isolation efficiency syst.',
    'alpha_MUON_EFF_TTVA_STAT': 'Muon TTVA efficiency stat.',
    'alpha_MUON_EFF_TTVA_SYS':  'Muon TTVA efficiency syst.',
    'alpha_MUON_EFF_BADMUON_STAT': 'Muon bad-muon efficiency stat.',
    'alpha_MUON_EFF_BADMUON_SYS':  'Muon bad-muon efficiency syst.',


    'alpha_JET_EtaIntercalibration_NonClosure_highE':  'Jet eta intercalibration non-closure (highE)',
    'alpha_JET_EtaIntercalibration_NonClosure_negEta': 'Jet eta intercalibration non-closure (negEta)',
    'alpha_JET_EtaIntercalibration_NonClosure_posEta': 'Jet eta intercalibration non-closure (posEta)',
    'alpha_JET_Flavor_Response': 'Jet flavor response',
    'alpha_JET_GroupedNP_1': 'Jet energy scale NP1',
    'alpha_JET_GroupedNP_2': 'Jet energy scale NP2',
    'alpha_JET_GroupedNP_3': 'Jet energy scale NP3',

    'alpha_JET_JER_DataVsMC': 'Jet energy resolution (DataVsMC)',
    'alpha_JET_JER_EffectiveNP_1': 'Jet energy resolution (NP1)',
    'alpha_JET_JER_EffectiveNP_2': 'Jet energy resolution (NP2)',
    'alpha_JET_JER_EffectiveNP_3': 'Jet energy resolution (NP3)',
    'alpha_JET_JER_EffectiveNP_4': 'Jet energy resolution (NP4)',
    'alpha_JET_JER_EffectiveNP_5': 'Jet energy resolution (NP5)',
    'alpha_JET_JER_EffectiveNP_6': 'Jet energy resolution (NP6)',
    'alpha_JET_JER_EffectiveNP_7restTerm': 'Jet energy resolution (NP7)',
    'alpha_JET_JvtEfficiency': 'JVT efficiency',
    'alpha_JET_fJvtEfficiency': 'fJVT efficiency',

    'alpha_FT_EFF_B_systematics': 'FT efficiency (B)',
    'alpha_FT_EFF_C_systematics': 'FT efficiency (C)',
    'alpha_FT_EFF_Light_systematics': 'FT efficiency (Light)',
    'alpha_FT_EFF_extrapolation': 'FT efficiency extrapolation',
    'alpha_FT_EFF_extrapolation_from_charm': 'FT efficiency extrapolation from charm',

    'alpha_MET_SoftTrk_ResoPara': 'MET SoftTrk resolution (Para)',
    'alpha_MET_SoftTrk_ResoPerp': 'MET SoftTrk resolution (Perp)',
    'alpha_MET_SoftTrk_Scale':    'MET SoftTrk scale',

    'alpha_PRW_DATASF': 'Pile-up re-weighting',

    'alpha_EFAKE_SYST': '$e\\to\\gamma$ fakes syst.',
    'alpha_EFAKE_STAT': '$e\\to\\gamma$ fakes stat.',

    'alpha_JFAKE_SYST': 'jet$\\to\\gamma$ fakes syst.',
    'alpha_JFAKE_STAT': 'jet$\\to\\gamma$ fakes stat.',

    'alpha_theoSysZG': '$Z\\gamma$ theo. syst.',
    'alpha_theoSysWG': '$W\\gamma$ theo. syst.',
    'alpha_theoSysTG': '$t\\bar{t}\\gamma$ theo. syst.',
    'alpha_theoSysGJ': '$\\gamma$ + jets theo. syst.',

    'mu_q': '$\\mu_{q}$',
    'mu_t': '$\\mu_{t}$',
    'mu_w': '$\\mu_{w}$',
}

systdict_root = {

    'alpha_JET_EtaIntercalibration_NonClosure': 'Jet eta intercalibration non-closure',
    'alpha_JET_GroupedNP_1': 'Jet energy scale NP1',
    'alpha_JET_GroupedNP_2': 'Jet energy scale NP2',
    'alpha_JET_GroupedNP_3': 'Jet energy scale NP3',

    'alpha_JET_JER_SINGLE_NP': 'Jet energy resolution',

    'alpha_MET_SoftTrk_ResoPara': 'MET SoftTrk resolution (Para)',
    'alpha_MET_SoftTrk_ResoPerp': 'MET SoftTrk resolution (Perp)',
    'alpha_MET_SoftTrk_Scale':    'MET SoftTrk scale',

    'alpha_EG_RESOLUTION_ALL': 'e/#gamma resolution',
    'alpha_EG_SCALE_ALL':      'e/#gamma scale',

    'alpha_PH_Iso_DDonoff': 'Photon isolation',

    'alpha_MUON_SCALE': 'Muon scale',
    'alpha_MUON_MS': 'Muon MS',
    'alpha_MUON_ID': 'Muon ID',
    'alpha_MUON_SAGITTA_RESBIAS': 'Muon SAGITTA ResBias',
    'alpha_MUON_SAGITTA_RHO': 'Muon SAGITTA RHO...',

    'alpha_PH_EFF_ID_Uncertainty': 'Photon ID',
    'alpha_JET_JvtEfficiency': 'JVT efficiency',
    'alpha_EL_EFF_ID_TOTAL_1NPCOR_PLUS_UNCOR': 'Electron ID eff.',
    'alpha_EL_EFF_Iso_TOTAL_1NPCOR_PLUS_UNCOR': 'Electron iso. eff.',
    'alpha_EL_EFF_Reco_TOTAL_1NPCOR_PLUS_UNCOR': 'Electron reco. eff.',
    'alpha_EL_EFF_Trigger_TOTAL_1NPCOR_PLUS_UNCOR': 'Electron trigger eff.',

    'alpha_MUON_EFF_STAT': 'Muon efficiency stat.',
    'alpha_MUON_EFF_SYS': 'Muon efficiency syst.',
    'alpha_MUON_ISO_STAT': 'Muon isolation stat.',
    'alpha_MUON_ISO_SYS': 'Muon isolation syst.',
    'alpha_MUON_TTVA_STAT': 'Muon TTVA stat.',
    'alpha_MUON_TTVA_SYS': 'Muon TTVA syst.',
    'alpha_PRW_DATASF': 'Pile-up re-weighting',

    'alpha_EFAKE_SYST': 'e#rightarrow#gamma fakes syst.',
    'alpha_EFAKE_STAT': 'e#rightarrow#gamma fakes stat.',

    'alpha_JFAKE_SYST': 'jet#rightarrow#gamma fakes syst.',
    'alpha_JFAKE_STAT': 'jet#rightarrow#gamma fakes stat.',

    'alpha_theoSysZG': 'Z#gamma theo. syst.',
    'alpha_theoSysWG': 'W#gamma theo. syst.',
    'alpha_theoSysTG': 't#bar{t}#gamma theo. syst.',
    'alpha_theoSysGJ': '#gamma + jets theo. syst.',

    'mu_q': '#mu_{q}',
    'mu_t': '#mu_{t}',
    'mu_w': '#mu_{w}',
}


def latexfitresults(filename, region, sample, resultName, dataname, doAsym):
    """
    Method: set all parameters constant, except for the one you're interested in,
    calculate the systematic/error propagated due to that parameter

    filename: The filename containing afterFit workspace
    resultname: The name of fit result (typically='RooExpandedFitResult_afterFit' or 'RooExpandedFitResult_beforeFit'
    region: The region to be used for systematics breakdown calculation
    sample: The sample to be used insted of total pdf (default='' not defined, hence total pdf used)
    dataname: The name of dataset (default='obsData')
    doAsym: Calculates asymmetric errors taken from MINOS (default=True)
    """

    #pick up workspace from file
    workspacename = 'w'
    w = Util.GetWorkspaceFromFile(filename,workspacename)
    if w is None:
        print "ERROR : Cannot open workspace:", workspacename
        sys.exit(1)

    #pickup RooExpandedFitResult from workspace with name resultName (either before or after fit)
    result = w.obj(resultName)
    if result is None:
        print "ERROR : Cannot open fit result", resultName
        sys.exit(1)

    # load workspace snapshot related to resultName (=set all parameters to values after fit)
    snapshot =  'snapshot_paramsVals_' + resultName
    w.loadSnapshot(snapshot)

    # pick up dataset from workspace
    data_set = w.data(dataname)
    if data_set is None:
        print "ERROR : Cannot open dataset: ", "data_set"
        sys.exit(1)

    #pick up channel category (RooCategory) from workspace
    region_cat = w.obj("channelCat")
    data_set.table(region_cat).Print("v");

    # find full (long) name list of region (i.e. short=SR3J, long=SR3J_meffInc30_JVF25pt50)
    region_full_name = Util.GetFullRegionName(region_cat, region);

    # set a boolean whether we're looking at a sample or the full (multi-sample) pdf/model
    chosen_sample = bool(sample)

    # define regSys set, for all names/numbers to be saved in
    reg_sys = {}

    # define channelCat call for this region and reduce the dataset to this category/region
    region_cat_str = 'channelCat==channelCat::' + region_full_name.Data()
    data_region = data_set.reduce(region_cat_str)

    # retrieve and save number of observed (=data) events in region
    nobs_region = 0.
    if data_region:
        nobs_region = data_region.sumEntries()
    else:
        print " ERROR : dataset-category dataRegion not found"

    # if looking at a sample, there is no equivalent N_obs (only for the full model)
    if chosen_sample:
        reg_sys['sqrtnobsa'] = 0.
    else:
        reg_sys['sqrtnobsa'] = ROOT.TMath.Sqrt(nobs_region)

    # get the pdf for the total model or just for the sample in region
    if chosen_sample:
        pdf_in_region = getPdfInRegions(w, sample, region)
    else:
        raw_pdf_in_region = Util.GetRegionPdf(w, region)
        var_in_region =  Util.GetRegionVar(w, region)
        prod_list = raw_pdf_in_region.pdfList()

        foundRRS = 0
        for idx in xrange(prod_list.getSize()):
            if prod_list[idx].InheritsFrom("RooRealSumPdf"):
                rrspdf_int =  prod_list[idx].createIntegral(ROOT.RooArgSet(var_in_region));
                pdf_in_region = rrspdf_int
                foundRRS += 1

        if foundRRS > 1 or foundRRS == 0:
            print " \n\n WARNING: ", pdf.GetName(), " has ", foundRRS, " instances of RooRealSumPdf"
            print pdf.GetName(), " component list:", prodList.Print("v")

        if not pdf_in_region:
            if chosenSample:
                print " \n Warning, could not find pdf in region = ",region, " for sample = ",sample
            else:
                print " \n Warning, could not find pdf in region = ",region

    # calculate fitted pdf number of events and full error
    n_fitted_in_region = pdf_in_region.getVal()
    reg_sys['sqrtnfitted'] = ROOT.TMath.Sqrt(n_fitted_in_region)
    reg_sys['nfitted'] = n_fitted_in_region

    pdf_fitted_err_in_region = Util.GetPropagatedError(pdf_in_region, result, doAsym)
    reg_sys['totsyserr'] = pdf_fitted_err_in_region


    # calculate error per (floating) parameter in fitresult
    # get a list of floating parameters to loop over
    fpf = result.floatParsFinal()

    # set all floating parameters constant
    for idx in xrange(fpf.getSize()):
        parname = fpf[idx].GetName()
        par = w.var(parname)
        par.setConstant(True)

    for idx in xrange(fpf.getSize()):
        parname = fpf[idx].GetName()
        par = w.var(parname)
        par.setConstant(False)
        reg_sys['syserr_'+parname] =  Util.GetPropagatedError(pdf_in_region, result, doAsym)
        par.setConstant(True)

    return reg_sys



def systable(workspace, samples, channels, output_name):

    chan_str = channels.replace(",","_")
    chan_list = channels.split(",")

    chosen_sample = False
    if samples:
        sample_str = samples.replace(",","_") + "_"
        from cmdLineUtils import cmdStringToListOfLists
        sample_list = cmdStringToListOfLists(samples)
        chosen_sample = True

    show_percent = True
    doAsym = True

    result_name = 'RooExpandedFitResult_afterFit'

    skip_list = ['sqrtnobsa', 'totbkgsysa', 'poisqcderr','sqrtnfitted','totsyserr','nfitted']

    chan_sys = {}
    orig_chan_list = list(chan_list)
    chan_list = []

    # calculate the systematics breakdown for each channel/region given in chanList
    # choose whether to use method-1 or method-2
    # choose whether calculate systematic for full model or just a sample chosen by user
    for chan in orig_chan_list:

        if not chosen_sample:
            reg_sys = latexfitresults(workspace, chan, '', result_name, 'obsData', doAsym)

            chan_sys[chan] = reg_sys
            chan_list.append(chan)
        else:
            for sample in sample_list:
                sample_name = getName(sample)

                reg_sys = latexfitresults(workspace, chan, sample, result_name, 'obsData', doAsym)
                chan_sys[chan+"_"+sample_name] = reg_sys
                chan_list.append(chan+"_"+sample_name)

    # write out LaTeX table by calling function from SysTableTex.py function tablefragment
    #line_chan_sys_tight = tablefragment(chanSys,chanList,skiplist,chanStr,showPercent)
    if not chosen_sample:
        field_names = ['\\textbf{Uncertainties}',] + [ '\\textbf{%s}' % reg for reg in  chan_list ]
    elif len(sample_list) == 1:
        sample_label = labels_latex_dict.get(getName(sample_list[0]), getName(sample_list[0]))

        field_names = ['\\textbf{Uncertainties (%s)}' % sample_label ] + [ '\\textbf{%s}' % (reg.split('_')[0]) for reg in  chan_list ]
    else:
        field_names = ['\\textbf{Uncertainties}',] + [ '\\textbf{%s (%s)}' % (reg.split('_')[0], reg.split('_')[1]) for reg in  chan_list ]
    align = ['l',] + [ 'r' for i in chan_list ]

    tablel = LatexTable(field_names, align=align, env=True)

    # print the total fitted (after fit) number of events
    row = ['Total background expectation',]
    for region in chan_list:
        row.append("$%.2f$"  % chan_sys[region]['nfitted'])

    tablel.add_row(row)
    tablel.add_line()

    # print sqrt(N_obs) - for comparison with total systematic
    row = ['Total statistical $(\\sqrt{N_\\mathrm{exp}})$',]
    for region in chan_list:
        row.append("$\\pm %.2f$" % chan_sys[region]['sqrtnfitted'])

    tablel.add_row(row)

    # print total systematic uncertainty
    row = [ 'Total background systematic', ]

    for region in chan_list:
        percentage = chan_sys[region]['totsyserr']/chan_sys[region]['nfitted'] * 100.0
        row.append("$\\pm %.2f\ [%.2f\%%]$" % (chan_sys[region]['totsyserr'], percentage))

    tablel.add_row(row)
    tablel.add_line()
    tablel.add_line()

    # print systematic uncertainty per floated parameter (or set of parameters, if requested)
    d = chan_sys[chan_list[0]]
    m_listofkeys = sorted(d.iterkeys(), key=lambda k: d[k], reverse=True)


    # uncertanties dict
    unc_dict = dict()
    unc_order = []
    for name in m_listofkeys:

        if name in skip_list:
            continue

        printname = name.replace('syserr_','')

        #slabel = label.split('_')
        #label = 'MC stat. (%s)' % slabel[2]

        # skip negligible uncertainties in all requested regions:
        zero = True
        for index, region in enumerate(chan_list):
            percentage = chan_sys[region][name]/chan_sys[region]['nfitted'] * 100.0

            if ('%.4f' % chan_sys[region][name]) != '0.0000' and ('%.2f' % percentage) != '0.00':
                zero = False

        if zero:
            continue

        # Parameter name -> parameter label
        if printname.startswith('gamma_stat'):
            label = 'MC stat.'

        elif printname.startswith('gamma_shape_JFAKE_STAT_jfake'):
            label = 'jet $\\to\\gamma$ fakes stat.'

        elif printname.startswith('gamma_shape_EFAKE_STAT_efake'):
            label = '$e\\to\\gamma$ fakes stat.'

        else:
            if printname in systdict and systdict[printname]:
                label = systdict[printname]
            else:
                label = printname

        # Fill dict
        for index, region in enumerate(chan_list):

            if printname.startswith('gamma') and not region.split('_')[0] in printname:
                continue

            if not label in unc_dict:
                unc_dict[label] = []
                unc_order.append(label)

            if not show_percent:
                unc_dict[label].append("$\\pm %.2f$" % chan_sys[region][name])
            else:
                percentage = chan_sys[region][name]/chan_sys[region]['nfitted'] * 100.0
                if percentage < 1:
                    unc_dict[label].append("$\\pm %.2f\ [%.2f\%%]$" % (chan_sys[region][name], percentage))
                else:
                    unc_dict[label].append("$\\pm %.2f\ [%.1f\%%]$" % (chan_sys[region][name], percentage))



    # fill table
    for label in unc_order:
        tablel.add_row([label,] + unc_dict[label])

    tablel.add_line()

    tablel.save_tex(output_name)


if __name__ == "__main__":
    pass
