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

# labels for dict
labels_dict = dict()
labels_dict['data']   = 'Data 2015'
labels_dict['photonjet'] = '#gamma + jets'
labels_dict['tgamma'] = 't#bar{t} #gamma /single-t #gamma'
labels_dict['vgamma'] = 'W/Z #gamma'
labels_dict['znngam'] = 'Z(#nu#nu) #gamma'
labels_dict['efake']  = 'e#rightarrow#gamma fake'
labels_dict['jfake']  = 'jet#rightarrow#gamma fake'
labels_dict['multijet']  = 'Multijet'
labels_dict['wjets']  = 'W + jets'
labels_dict['zjets']  = 'Z + jets'
labels_dict['vjets']  = 'W/Z + jets'
labels_dict['ttbar']  = 't#bar{t}'
# labels_dict['GGM_M3_mu_total_800_175']   = 'M_{3} = 800, #mu = 175'
# labels_dict['GGM_M3_mu_total_800_750']   = 'M_{3} = 800, #mu = 750'
# labels_dict['GGM_M3_mu_total_1050_750']  = 'M_{3} = 1050, #mu = 750'
# labels_dict['GGM_M3_mu_total_1050_175']  = 'M_{3} = 1050, #mu = 175'
labels_dict['GGM_M3_mu_total_1300_150']  = 'M_{3} = 1300, #mu = 150'
labels_dict['GGM_M3_mu_total_1300_650']  = 'M_{3} = 1300, #mu = 650'
# labels_dict['GGM_M3_mu_total_1050_750']  = 'M_{3} = 1050, #mu = 750'
# labels_dict['GGM_M3_mu_total_1050_950']  = 'M_{3} = 1050, #mu = 950'
# labels_dict['GGM_M3_mu_total_1250_1150'] = 'M_{3} = 1250, #mu = 1150'

# colours for the dict
colors_dict = dict()
colors_dict['photonjet'] = '#E24A33'
colors_dict['tgamma'] = '#32b45d' #'#48b432'
colors_dict['vgamma'] = '#f7fab3'
colors_dict['znngam'] = '#7A68A6'
colors_dict['efake']  = '#a4cee6'
colors_dict['jfake']  = '#348ABD'
colors_dict['multijet']  = '#348ABD'
colors_dict['wjets']  = '#BCBC93'
colors_dict['zjets']  = '#36BDBD'
colors_dict['vjets']  ='#a4cee6'
colors_dict['ttbar']  = '#32b45d'
#colors_dict['GGM_M3_mu_1050_750'] = '#141a4d'
colors_dict['GGM_M3_mu_total_1300_150'] = '#fa423a'
colors_dict['GGM_M3_mu_total_1300_650'] = '#8453fb'
# colors_dict['GGM_M3_mu_1050_750']  = '#c73444'
# colors_dict['GGM_M3_mu_1050_950']  = '#c74934'
# colors_dict['GGM_M3_mu_1250_1150'] = '#c73469'


class PlotConf(object):
    def __init__(self, xtitle, ytitle, legpos, xmin=None, xmax=None):
        self.xtitle = xtitle
        self.ytitle = ytitle
        self.legpos = legpos
        self.xmin = xmin
        self.xmax = xmax

plots_conf = dict()
plots_conf['cuts']         = PlotConf('', 'Events', 'right')
plots_conf['ph_n']         = PlotConf('Number of photons', 'Events', 'right')
plots_conf['el_n']         = PlotConf('Number of electrons', 'Events', 'right')
plots_conf['jet_n']        = PlotConf('Number of jets', 'Events', 'right')
plots_conf['ph_pt']        = PlotConf('p_{T}^{#gamma} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['ph_eta']       = PlotConf('Photon #eta', 'Events / (BIN GeV)', 'right')
plots_conf['ph_phi']       = PlotConf('Photon #phi', 'Events / (BIN GeV)', 'right')
plots_conf['ph_iso']       = PlotConf('Isolation (Etcone20) [GeV]', 'Events (1/BIN GeV)', 'right')
plots_conf['met_et']       = PlotConf('E_{T}^{miss} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['met_phi']      = PlotConf('#phi^{miss}', 'Events', 'right')
plots_conf['ht']           = PlotConf('H_{T} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['jet_pt']      = PlotConf('Jet p_{T} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['jet_eta']     = PlotConf('Jet #eta', 'Events', 'right')
# plots_conf['jet1_phi']     = PlotConf('leading jet #phi', 'Events', 'right')
# plots_conf['jet2_pt']      = PlotConf('2nd leading jet p_{T} [GeV]', 'Events', 'right')
# plots_conf['jet2_eta']     = PlotConf('2nd leading #eta', 'Events', 'right')
# plots_conf['jet2_phi']     = PlotConf('2nd leading #phi', 'Events', 'right')
plots_conf['rt2']          = PlotConf('R_{T}^{2}', 'Events', 'left', 0.3, 1.1)
plots_conf['rt4']          = PlotConf('R_{T}^{4}', 'Events / BIN', 'left', 0.3, 1.1)
plots_conf['dphi_jetmet']  = PlotConf('#Delta#phi(jet^{1,2}, E_{T}^{miss})', 'Events', 'right')
plots_conf['dphi_jetmet_alt'] = PlotConf('#Delta#phi(jet^{1..4}, E_{T}^{miss})', 'Events', 'right')
plots_conf['dphi_jet1met'] = PlotConf('#Delta#phi(j^{1}, E_{T}^{miss})', 'Events', 'right')
plots_conf['dphi_jet2met'] = PlotConf('#Delta#phi(j^{2}, E_{T}^{miss})', 'Events', 'right')
plots_conf['dphi_jet3met'] = PlotConf('#Delta#phi(j^{3}, E_{T}^{miss})', 'Events', 'right')
plots_conf['dphi_gamjet']  = PlotConf('#Delta#phi(#gamma, jet)', 'Events', 'right')
plots_conf['dphi_gammet']  = PlotConf('#Delta#phi(#gamma, E_{T}^{miss})', 'Events', 'right')
plots_conf['default'] = PlotConf('','', 'right')


def do_plot(plotname, variable, h_data, h_bkg, h_signal, 
            do_bkg_total=True, do_ratio=True, include_ratio=True, region_name=''):
    
    
    if '[' in variable:
        vartmp = variable[:variable.find('[')]
        conf = plots_conf.get(vartmp)
    else:
        conf = plots_conf.get(variable)

    xtitle = conf.xtitle
    ytitle = conf.ytitle
    xmin = conf.xmin
    xmax = conf.xmax
    legpos = conf.legpos


    can = canvas(plotname, plotname, 800, 800)
    can.cd()

    def calc_size(pad):
        pad_width = pad.XtoPixel(pad.GetX2())
        pad_height = pad.YtoPixel(pad.GetY1())

        if pad_width < pad_height:
            tsize = 28.6 / pad_width
        else:
            tsize = 28.6 / pad_height
        return tsize

    if do_ratio:

        cup   = ROOT.TPad("u", "u", 0., 0.305, 0.99, 1)
        cdown = ROOT.TPad("d", "d", 0., 0.01, 0.99, 0.295)
        cup.SetRightMargin(0.05)
        cup.SetBottomMargin(0.005)

        cup.SetTickx()
        cup.SetTicky()
        cdown.SetTickx()
        cdown.SetTicky()
        cdown.SetRightMargin(0.05)
        cdown.SetBottomMargin(0.3)
        cdown.SetTopMargin(0.0054)
        cdown.SetFillColor(ROOT.kWhite)
        cup.Draw()
        cdown.Draw()

        #if logy:
        cup.SetLogy()

        cup.SetTopMargin(0.08)
        cdown.SetBottomMargin(0.4)

        up_size = calc_size(cup)
        dn_size = calc_size(cdown)

    else:
        #if logy:
        can.SetLogy()

        can.SetLeftMargin(0.15)
        up_size = calc_size(can)
        dn_size = calc_size(can) 


    # configure histograms
    for name, hist in h_bkg.iteritems():
        set_style(hist, color=colors_dict[name], fill=True)
        hist.SetLineColor(ROOT.kBlack)

    set_style(h_data, msize=1, lwidth=2, color=ROOT.kBlack)

    for sig, hist in h_signal.iteritems():
        set_style(hist, msize=1.2, lwidth=2, lstyle=2, color=colors_dict[sig])

    # create SM stack
    sm_stack = ROOT.THStack()

    def _compare(a, b):
        amax = a.GetMaximum()
        bmax = b.GetMaximum()
        return cmp(int(amax), int(bmax))

    for hist in sorted(h_bkg.itervalues(), _compare):
        sm_stack.Add(hist)
    #sm_stack.Add(h_data)

    # Total background
    sm_total = None
    sm_totalerr = None

    sm_total_style = 3354
    sm_total_color = ROOT.kGray+3

    sm_stat_color = ROOT.kGray+1
    sm_syst_color = ROOT.kGray+3

    for h in h_bkg.itervalues():
        if sm_total is None:
            sm_total = histogram_equal_to(h)
        sm_total += h

    sm_total_stat = sm_total.Clone()
    #sm_total_all  = sm_total.Clone()

    # for b in xrange(sm_total_all.GetNbinsX()):
    
    #     mean = sm_total_all.GetBinContent(b+1)

    #     if mean < 0.000000001:
    #         continue

    #     stat = sm_total_all.GetBinError(b+1) / mean
    #     syst = systematics[region_name]

    #     err = math.sqrt(stat*stat + syst*syst)

    #     self.sm_total_all.SetBinError(b+1, err*mean)

    if sm_total is not None:
        sm_total.SetLineWidth(2)
        sm_total.SetLineColor(sm_total_color)
        sm_total.SetFillColor(0)
        sm_total.SetMarkerSize(0)

        sm_total_stat.SetFillColor(sm_total_color)
        sm_total_stat.SetLineColor(sm_total_color)
        sm_total_stat.SetFillStyle(sm_total_style)
        sm_total_stat.SetLineWidth(2)
        sm_total_stat.SetMarkerSize(0)

        # sm_total_all.SetFillColor(sm_syst_color)
        # sm_total_all.SetLineColor(sm_syst_color)
        # sm_total_all.SetFillStyle(sm_total_style)
        # sm_total_all.SetLineWidth(2)
        # sm_total_all.SetMarkerSize(0)

    # add entries to legend
    if do_ratio:
        legymin = 0.65
        legymax = 0.88

        if legpos == 'left':
            legxmin = 0.20
            legxmax = 0.53
        elif legpos == 'right':
            legxmin = 0.55
            legxmax = 0.88
    else:
        legymin = 0.80
        legymax = 0.94

        if legpos == 'left':
            legxmin = 0.20
            legxmax = 0.53
        elif legpos == 'right':
            legxmin = 0.65
            legxmax = 0.92

    legend1 = legend(legxmin, legymin, legxmax, legymax, columns=2)
    legend2 = legend(legxmin, legymin-.15, legxmax-0.035, legymin -.01)

    for name, hist in h_bkg.iteritems():
        legend1.AddEntry(hist, labels_dict[name], 'f')

    if do_bkg_total and sm_total is not None:
        legend1.AddEntry(sm_total_stat, "SM Total", 'f')
        #legend1.AddEntry(sm_total_all, "stat #oplus syst", 'f')
    
    if h_data is not None:
        legend1.AddEntry(h_data, labels_dict['data'], 'pl')

    # we don't want to plot signals in Control Regions
    if 'CR' in region_name:
        h_signal = {}

    if h_signal :
        for name, hist in h_signal.iteritems():
            legend2.AddEntry(hist, labels_dict[name], 'f')

    if do_ratio:
        cup.cd()

    # first histogram to configure (ROO de mierda)
    # if h_bkg:
    #     chist = sm_stack
    # else:
    #     chist = h_data

    #if sm_stack is not None:
    sm_stack.Draw('hist')

    if xmin is not None and xmax is not None:
        sm_stack.GetXaxis().SetRangeUser(xmin, xmax)

    if sm_stack.GetXaxis().GetXmax() < 5.:
        sm_stack.GetXaxis().SetNdivisions(512)
    else:
        sm_stack.GetXaxis().SetNdivisions(508)

    if do_ratio:
        cup.RedrawAxis()
    else:
        can.RedrawAxis()

    sm_stack.SetMinimum(0.01)

    #if logy:
    if 'dphi' in variable:
        sm_stack.SetMaximum(sm_stack.GetMaximum()*100000)
    else:
        sm_stack.SetMaximum(sm_stack.GetMaximum()*1000)
    #else:
    #    sm_stack.SetMaximum(sm_stack.GetMaximum())

    sm_stack.GetXaxis().SetTitle(xtitle)
    sm_stack.GetXaxis().SetTitleOffset(1.2)
    sm_stack.GetXaxis().SetLabelSize(0.)

    sm_stack.GetXaxis().SetLabelSize(up_size)
    sm_stack.GetXaxis().SetTitleSize(up_size*1.3)
    sm_stack.GetYaxis().SetLabelSize(up_size)
    sm_stack.GetYaxis().SetTitleSize(up_size*1.3)

 
    if 'BIN' in ytitle:
        if h_bkg:
            width = sm_total.GetBinWidth(1)
        else:
            width = h_data.GetBinWidth(1)
        if width > 10:
            ytitle = ytitle.replace('BIN', '{:.0f}'.format(width))
        else:
            ytitle = ytitle.replace('BIN', '{:.2f}'.format(width))

    sm_stack.GetYaxis().SetTitle(ytitle)
    if do_ratio:
        sm_stack.GetYaxis().SetTitleOffset(0.8)
    else:
        sm_stack.GetYaxis().SetTitleOffset(1.2)


    h_data.Draw("P same")

    if sm_total is not None:
        sm_total.Draw("histsame")
        sm_total_stat.Draw("E2same][")


    for h in h_signal.itervalues():
        h.Draw('histsame')

    h_data.Draw("Psame")

    if do_ratio:
        cup.RedrawAxis()
    else:
        can.RedrawAxis()

    legend1.Draw()
    legend2.Draw()

    # ATLAS label
    l = ROOT.TLatex(0,0,'ATLAS')
    l.SetNDC()
    l.SetTextFont(72)
    l.SetTextSize(0.05)
    l.SetTextColor(ROOT.kBlack)
    p = ROOT.TLatex(0,0, 'Internal')
    p.SetNDC()
    p.SetTextFont(42)
    p.SetTextColor(ROOT.kBlack)
    p.SetTextSize(0.05)
    delx = 0.085*696*ROOT.gPad.GetWh()/(472*ROOT.gPad.GetWw())
    if not do_ratio:
        delx += 0.05
    if legpos == 'right':
        axmin = 0.20 ; aymin = 0.83
        if not do_ratio:
            aymin = 0.88
    else:
        axmin = 0.60 ; aymin = 0.83

    l.DrawLatex(axmin, aymin, "ATLAS")
    p.DrawLatex(axmin+delx, aymin, 'Internal')

    # luminosity
    text = '#sqrt{s} = 13 TeV, 84.97 pb^{-1}' 
    t = ROOT.TLatex(0, 0, text)
    t.SetNDC()
    t.SetTextFont(42)
    t.SetTextSize(0.04)
    t.SetTextColor(ROOT.kBlack)
    if legpos == 'right':
        if do_ratio:
            t.DrawLatex(0.20, 0.73, text)
        else:
            t.DrawLatex(0.20, 0.78, text)
    else:
        t.DrawLatex(0.60, 0.73, text)

      
    # text = 'Selection: '
    li = ROOT.TLine()
    li.SetLineStyle(2)
    li.SetLineWidth(2)
    li.SetLineColor(ROOT.kBlack)

    ar = ROOT.TArrow(0, 0, 0, 0, 0.008, "|>")
    ar.SetLineWidth(2)
    ar.SetLineColor(ROOT.kBlack)

    rl = ROOT.TLatex()
    rl.SetTextSize(0.035)
    rl.SetTextColor(ROOT.kBlack)

    if variable == 'met_et' and region_name == 'SR_L':
        li.DrawLine(50, 0, 50, 4000)
        li.DrawLine(200, 0, 200, 4000)

        ar.DrawArrow(50, 2500, 25, 2500)
        ar.DrawArrow(200, 10, 225, 10)

        rl.DrawLatex(25, 1000, 'CR_{QCD,L}')
        rl.DrawLatex(210, 20, 'SR_{L}')
    else:
        if '_L' in region_name:
            text = region_name.replace('_L', '_{L}')
        elif '_H' in region_name:
            text = region_name.replace('_H', '_{H}')
        
        t = ROOT.TLatex(0, 0, text)
        t.SetNDC()
        t.SetTextColor(ROOT.kBlack)
        t.SetTextFont(42)
        t.SetTextSize(0.04)
        if legpos == 'right':
            t.DrawLatex(0.20, 0.64, text)
        else:
            t.DrawLatex(0.6, 0.64, text)


    if do_ratio:
        ratio = h_data.Clone()
        ratio.Divide(sm_total)

        # remove the point from the plot if zero
        for b in xrange(ratio.GetNbinsX()):
            if ratio.GetBinContent(b+1) < 0.00001:
                ratio.SetBinContent(b+1, -1)

        cdown.cd()
        ratio.SetTitle('')
        ratio.SetStats(0)
        ratio.SetMarkerStyle(20)
        ratio.SetMarkerSize(1)
        ratio.SetLineWidth(2)
        ratio.SetLineColor(ROOT.kBlack)
        ratio.SetMarkerColor(ROOT.kBlack)

        # x axis
        ratio.GetXaxis().SetTitle(xtitle)
        if xmin is not None and xmax is not None:
            ratio.GetXaxis().SetRangeUser(xmin, xmax)
        ratio.GetXaxis().SetLabelSize(dn_size)
        ratio.GetXaxis().SetTitleSize(dn_size*1.3)
        ratio.GetXaxis().SetTitleOffset(1.)
        ratio.GetXaxis().SetLabelOffset(0.03)
        ratio.GetXaxis().SetTickLength(0.06)

        if ratio.GetXaxis().GetXmax() < 5.:
            ratio.GetXaxis().SetNdivisions(512)
        else:
            ratio.GetXaxis().SetNdivisions(508)

        # y axis
        ratio.GetYaxis().SetTitle('Data / SM')
        ratio.GetYaxis().SetLabelSize(dn_size)
        ratio.GetYaxis().SetTitleSize(dn_size*1.3)
        ratio.GetYaxis().SetRangeUser(0, 2.2)
        ratio.GetYaxis().SetNdivisions(504)
        ratio.GetYaxis().SetTitleOffset(0.3)
        ratio.GetYaxis().SetLabelOffset(0.01)

        err_band_stat = ROOT.TGraphAsymmErrors(ratio.GetNbinsX())
        # self.err_band_all  = ROOT.TGraphAsymmErrors(self.ratio.GetNbinsX())

        for bin_ in xrange(ratio.GetNbinsX()):

            x    = sm_total.GetBinCenter(bin_+1)
            xerr = sm_total.GetBinWidth(bin_+1)/2

            sm_y     = sm_total.GetBinContent(bin_+1)

            sm_stat_high = sm_total_stat.GetBinError(bin_+1)
            sm_stat_low  = sm_total_stat.GetBinError(bin_+1)

            #     sm_all_high = self.sm_total_all.GetBinError(bin_+1)
            #     sm_all_low  = self.sm_total_all.GetBinError(bin_+1)

            try:
                stat_low  = sm_stat_low/sm_y
            #         all_low  = sm_all_low/sm_y
            except ZeroDivisionError:
                stat_low = 0.0
            #         all_low = 0.0

            try:
                stat_high = sm_stat_high/sm_y
            #         all_high = sm_all_high/sm_y
            except ZeroDivisionError:
                stat_high = 0.0
            #         all_high = 0.0

            err_band_stat.SetPoint(bin_, x, 1.)
            err_band_stat.SetPointError(bin_, xerr, xerr, stat_low, stat_high)

            #     self.err_band_all.SetPoint(bin_, x, 1.)
            #     self.err_band_all.SetPointError(bin_, xerr, xerr, all_low, all_high)


        err_band_stat.SetLineWidth(2)
        err_band_stat.SetMarkerSize(0)
        err_band_stat.SetFillStyle(sm_total_style)
        err_band_stat.SetLineColor(sm_total_color)
        err_band_stat.SetFillColor(sm_total_color)

        # self.err_band_all.SetMarkerSize(0)
        # self.err_band_all.SetFillStyle(self.sm_total_style)
        # self.err_band_all.SetLineColor(self.sm_syst_color)
        # self.err_band_all.SetFillColor(self.sm_syst_color)
        # self.err_band_all.SetLineWidth(2)

        ratio.Draw()
        # self.err_band_all.Draw('P2same')
        err_band_stat.Draw('P2same')
        ratio.Draw('same e0')

        firstbin = ratio.GetXaxis().GetFirst()
        lastbin  = ratio.GetXaxis().GetLast()
        xmax     = ratio.GetXaxis().GetBinUpEdge(lastbin)
        xmin     = ratio.GetXaxis().GetBinLowEdge(firstbin)

        lines = [None, None, None,]
        lines[0] = ROOT.TLine(xmin, 1., xmax, 1.)
        lines[1] = ROOT.TLine(xmin, 0.5,xmax, 0.5)
        lines[2] = ROOT.TLine(xmin, 1.5,xmax, 1.5)

        lines[0].SetLineWidth(1)
        lines[0].SetLineStyle(2)
        lines[1].SetLineStyle(3)
        lines[2].SetLineStyle(3)

        for line in lines:
            line.Draw()

    can.Print(plotname+'.pdf')


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
    parser.add_argument('--sel', dest='selection', default='', help='Custom selection')
    parser.add_argument('--n1', action='store_true', help='N-1 plot')
    parser.add_argument('--comp', action='store_true', dest='region_composition',
                        help='create region composition plot')
    parser.add_argument('--signal', action='store_true', help='Add signal samples (separated with ,)')
    parser.add_argument('--blind', action='store_true', help='Don\'t include the data')

    parser.add_argument('--debug', action='store_true', help='print debug messages')

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
        #'diboson',
        'wjets',
        'zjets',
        'ttbar',
        #'ttbarg',
        #'topgamma',
        ]


    # Region composition
    if args.region_composition:

        h_comp_bkg = OrderedDict()
        for name in backgrounds:
            h_comp_bkg[name] = Hist(name, len(regions), 0, len(regions))

        h_comp_data = Hist('data', len(regions), 0, len(regions))

        for i, region in enumerate(regions):

            if args.input_file:
                selection = region
            else:
                if not args.selection:
                    selection = getattr(regions_, region)
                else:
                    selection = args.selection

            region_name = region[:-2]

            # get regions histogram
            h_region_data = get_histogram('data', 'cuts', '', selection, syst)

            if args.blind and 'SR' in region:
                h_region_data.SetBinContent(1, 0)
                h_region_data.SetBinError(1, 0)

            h_region_bkg = dict()
            for name in h_comp_bkg.iterkeys():
                h_region_bkg[name] = get_histogram(name, 'cuts', '', selection, syst)

            # normalize
            if not all(v is None for v in [args.mu_qcd, args.mu_wgam, args.mu_tgam]):
                normalize_backgrounds(h_region_bkg)
            elif args.normqcd:
                normalize_qcd_to_data(h_region_data, h_region_bkg)

            # add to composition histogram
            n = h_region_data.GetBinContent(1)
            e = h_region_data.GetBinError(1)

            h_comp_data.SetBinContent(i+1, n)
            h_comp_data.SetBinError(i+1, e)

            h_comp_data.GetXaxis().SetBinLabel(i+1, region_name)

            for name in h_comp_bkg.iterkeys():
                n = h_region_bkg[name].GetBinContent(1)
                e = h_region_bkg[name].GetBinError(1)

                h_comp_bkg[name].SetBinContent(i+1, n)
                h_comp_bkg[name].SetBinError(i+1, e)

                h_comp_bkg[name].GetXaxis().SetBinLabel(i+1, region_name)


        for bkg, hist in h_comp_bkg.iteritems():
            set_hist_style(hist, color=colors_dict[bkg], fill=True)

        set_hist_style(h_comp_data, markersize=1.2, linewidth=1, color=kBlack)

        plot(h_comp_bkg, h_comp_data, None, 'cuts',
             os.path.join(args.output_dir, 'region_composition'))

        if args.save:
            file_name = os.path.join(args.output_dir, args.save)
            with RootFile(file_name, 'update') as f:
                f.write(h_comp_bkg)
                f.write(h_comp_data)

        return

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

                del h_bkg['wjets']
                del h_bkg['zjets']

                ## data
                if args.blind:
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

                    signals = ['GGM_M3_mu_total_1300_150', 'GGM_M3_mu_total_1300_650', ]

                    for sig in signals:
                        h_signal[sig] = get_histogram(sig, variable, region_name, selection, syst, truth=True)
                        histogram_add_overflow_bin(h_signal[sig])


                blinded = args.blind and (region == 'SR')

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

    
                if region.endswith('_L'):
                    s =  0.72
                elif region.endswith('_H'):
                    s = 0.67

                h_bkg_after['photonjet'].Scale(s)


                outname = os.path.join(args.output_dir, 'can_{}_{}_afterFit'.format(region, variable))
                do_plot(outname, variable, h_data, h_bkg_after, h_signal, region_name=region)

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
