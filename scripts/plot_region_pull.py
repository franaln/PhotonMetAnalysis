#! /usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)

import os
import sys
import math
import argparse
import subprocess
import pickle
from collections import OrderedDict

from rootutils import *
import style
from style import colors_dict, labels_dict
from drawutils import calc_poisson_cl_upper, calc_poisson_cl_lower
from yieldstable import latexfitresults
import analysis

parser = argparse.ArgumentParser(description='plot regions pull')
    
parser.add_argument('--ws', dest='workspace', required=True, help='Input workspace')
parser.add_argument('-o', dest='output_dir', default='.', help='Output dir')
parser.add_argument('-r', dest='regions', help='regions')
parser.add_argument('--unblind', action='store_true', help='Unblind! (use with caution)')
parser.add_argument('--ext', dest='extensions', default='pdf', help='')

args = parser.parse_args()

workspace = args.workspace
regions = args.regions.split(',')

set_atlas_style()

# Backgrounds
backgrounds = analysis.backgrounds

max_pull = 3.0

def get_region_color(region):
    return get_color('#80807a')


def get_poisson_error(obs):

    posError = ROOT.TMath.ChisquareQuantile(1. - (1. - 0.68)/2. , 2.* (obs + 1.)) / 2. - obs - 1
    negError = obs - ROOT.TMath.ChisquareQuantile((1. - 0.68)/2., 2.*obs) / 2

    return (posError, negError)


def make_box(color=ROOT.kGray+1, offset=0, pull=-1, horizontal=False):

    if pull > 0.:
        miny = -0.02
    else:
        miny = 0.02

    if pull > max_pull:
        pull = max_pull-0.05
    elif pull < -max_pull:
        pull = -max_pull+0.05


    box = ROOT.TBox(0.1+offset, miny, 0.9+offset, pull)

    box.SetFillColor(color)
    box.SetLineColor(color)

    return box


def get_frame(npar, horizontal=False):

    frame = ROOT.TH2F("frame", "", npar, 0., npar, 8, -4., 4.);
    frame.GetYaxis().SetTitleSize(0.10)
    frame.GetYaxis().CenterTitle()
    frame.GetYaxis().SetTitleOffset(0.35)
    frame.GetYaxis().SetRangeUser(-max_pull, max_pull)
    frame.GetXaxis().SetLabelOffset(0.03)
    frame.GetXaxis().SetLabelSize(0.12)
    frame.GetYaxis().SetLabelSize(0.12)
    frame.GetYaxis().SetNdivisions(4)
    frame.SetYTitle("(n_{#lower[-0.3]{obs}} - n_{exp}) / #sigma_{tot}")
        
    # global style settings
    ROOT.gPad.SetTicks();
    frame.SetLabelFont(42, "X");
    frame.SetTitleFont(42, "X");
    frame.SetLabelFont(42, "Y");
    frame.SetTitleFont(42, "Y");

    return copy.deepcopy(frame)


def get_boxes(regions_pull, frame, horizontal=False):

    allp = []

    counter = 0
    myr = reversed(regions_pull)
    if horizontal:
        myr = regions_pull

    for region, pull in myr:
        name = region.replace(" ","")
        name = region.replace("_cuts","")
        
        if not args.unblind and name.startswith('SR'):
            continue

        if horizontal:
            for b in xrange(1,frame.GetNbinsX()+2):
                if frame.GetXaxis().GetBinLabel(b) != name: 
                    continue
                counter = b - 1
                break
        else:
            frame.GetYaxis().SetBinLabel(counter+1,name);

        color = get_region_color(name)

        box = make_box(offset=counter, pull=pull, color=color, horizontal=horizontal)
        box.Draw()

        counter += 1
        allp.append(box) 

    return allp



def make_hist_pull_plot(samples, regions, results):

    ROOT.gStyle.SetOptStat(0000)

    npar = len(regions)

    # Make histograms
    ymax = 0
    ymin = 99999999999.

    hdata = ROOT.TH1F('data', 'data', npar, 0, npar)
    hbkg  = ROOT.TH1F("hbkg", "hbkg", npar,0, npar)

    hbkg_components = []
    for sam in samples.split(","):
        h = ROOT.TH1F("hbkg_"+sam,"hbkg_"+sam, npar, 0, npar)
        hbkg_components.append(h)

    graph_bkg  = ROOT.TGraphAsymmErrors(npar)
    graph_data = ROOT.TGraphAsymmErrors(npar)

    # loop over all the regions
    regions_pull = []
    for counter, region in enumerate(regions):

        # extract the information
        for info in results:
            if info[0] == region:
                break

        name = region.replace(" ","") #.replace('SRi', 'SR')

        n_obs = info[1]
        n_exp = info[2]
        exp_syst = info[3]
        
        exp_stat = 0
        exp_stat_up = 0
        exp_stat_dn = 0

        if n_exp > 0:
            exp_stat = ROOT.TMath.Sqrt(n_exp)
            exp_stat_up, exp_stat_dn = get_poisson_error(n_exp)
        
        exp_total = 0
        exp_total_up = 0
        exp_total_dn = 0

        exp_total    = ROOT.TMath.Sqrt(exp_stat*exp_stat + exp_syst*exp_syst)
        exp_total_up = ROOT.TMath.Sqrt(exp_stat_up*exp_stat_up + exp_syst*exp_syst)
        exp_total_dn = ROOT.TMath.Sqrt(exp_stat_dn*exp_stat_dn + exp_syst*exp_syst)

        pull = 0
        if (n_obs - n_exp) > 0 and exp_total_up != 0:
            pull = (n_obs - n_exp)/exp_total_up
        if (n_obs - n_exp) <= 0 and exp_total_dn != 0:
            pull = (n_obs - n_exp)/exp_total_dn

        if -0.02 < pull < 0: 
            pull = -0.02 ###ATT: ugly
        if 0 < pull < 0.02:  
            pull = 0.02 ###ATT: ugly

        if region.find("SR")>=0 and not args.unblind:
            n_obs = -100
            pull = 0

        if n_obs == 0 and n_exp == 0:
            pull = 0
            n_obs = -100
            n_pred = -100
            exp_total = 0
            exp_syst = 0
            exp_stat = 0
            exp_stat_up = 0
            exp_stat_dn = 0
            exp_total_up = 0
            exp_total_dn = 0

        regions_pull.append((region, pull))

        #bkg components
        compInfo = info[4]
        for i in xrange(len(compInfo)):
            hbkg_components[i].SetBinContent(counter+1, compInfo[i][1])

        if n_obs > ymax:
            ymax = n_obs

        if n_exp + exp_total_up > ymax:
            ymax = n_exp + exp_total_up

        if n_obs < ymin and n_obs != 0:
            ymin = n_obs

        if n_exp < ymin and n_exp != 0:
            ymin = n_exp

        graph_bkg.SetPoint(counter, hbkg.GetBinCenter(counter+1), n_exp)
        graph_bkg.SetPointError(counter, 0.5, 0.5, exp_total_dn, exp_total_up)

        graph_data.SetPoint(counter, hbkg.GetBinCenter(counter+1), n_obs)

        binErrUp, binErrLow = 0,0
        if n_obs > 0.:
            binErrUp   = calc_poisson_cl_upper(0.68, n_obs) - n_obs
            binErrLow  = n_obs - calc_poisson_cl_lower(0.68, n_obs)

        y_eu = binErrUp
        y_el = binErrLow

        if n_obs > 0.:
            x_eu = hbkg.GetXaxis().GetBinWidth(counter+1)/2.0
            x_el = hbkg.GetXaxis().GetBinWidth(counter+1)/2.0
        else:
            x_eu = 0
            x_el = 0

        hdata.GetXaxis().SetBinLabel(counter+1, name)
        hdata.SetBinContent(counter+1, n_obs)
        hdata.SetBinErrorOption(ROOT.TH1.kPoisson)

        graph_data.SetPointError(counter, x_el, x_eu, y_el, y_eu)

        hbkg.SetBinContent(counter+1, n_exp)
        hbkg.SetBinError(counter+1, exp_total)

    hdata.SetMaximum(1000*ymax)
    hdata.SetMinimum(0.05)

    # Plot
    c = ROOT.TCanvas("c",'', 1000, 600);

    c.SetFrameFillColor(ROOT.kWhite)

    cup   = ROOT.TPad("u", "u", 0., 0.305, 0.99, 1)
    cdown = ROOT.TPad("d", "d", 0., 0.01, 0.99, 0.295)

    cup.SetLogy()

    cup.SetFillColor(0)
    cup.SetBorderMode(0)
    cup.SetBorderSize(2)
    cup.SetTicks()
    cup.SetTopMargin    (0.1)
    cup.SetRightMargin  (0.02)
    cup.SetBottomMargin (0.0025)
    cup.SetLeftMargin   (0.08)
    cup.SetFrameBorderMode(0)
    cup.SetFrameBorderMode(0)
    cup.Draw()

    cdown.SetGridx()
    cdown.SetGridy()

    cdown.SetFillColor(0)
    cdown.SetBorderMode(0)
    cdown.SetBorderSize(2)
    cdown.SetTickx(1)
    cdown.SetTicky(1)
    cdown.SetTopMargin   (0.003)
    cdown.SetRightMargin (0.02)
    cdown.SetBottomMargin(0.20)
    cdown.SetLeftMargin  (0.08)
    cdown.Draw()

    cup.cd()

    ## bkg stack
    stack = ROOT.THStack("stack", "stack")

    to_merge = {}
    merged_bkgs = OrderedDict()

    for sample, hist in zip(samples.split(','), hbkg_components):
        to_merge[sample] = hist

    merged_bkgs['gamjet'] = to_merge['photonjet']
    merged_bkgs['tgamma'] = to_merge['ttbarg'] #+ to_merge['ttbarghad'] to_merge['topgamma'] + 
    merged_bkgs['fakes'] = to_merge['efake'] + to_merge['jfake']
    merged_bkgs['wgamma'] = to_merge['wgamma']
    merged_bkgs['zgamma'] = to_merge['zllgamma'] + to_merge['znunugamma']
    merged_bkgs['diphoton'] = to_merge['diphoton'] + to_merge['vgammagamma']

    if 'vqqgamma' in merged_bkgs:
        merged_bkgs['vgamma'] += to_merge['vqqgamma']


    for sam, h in merged_bkgs.iteritems():
        set_style(h, color=colors_dict[sam], fill=True)

    def _compare(a, b):
        amax = a.GetMaximum()
        bmax = b.GetMaximum()
        return cmp(int(amax), int(bmax))

    for hist in sorted(merged_bkgs.itervalues(), _compare):
        stack.Add(hist)

    # Total background
    sm_total_style = 3354
    sm_total_color = ROOT.kGray+3

    hbkg_total = hbkg.Clone()

    hbkg.SetLineWidth(2)
    hbkg.SetLineColor(sm_total_color)
    hbkg.SetFillColor(0)
    hbkg.SetMarkerSize(0)

    hbkg_total.SetFillColor(sm_total_color)
    hbkg_total.SetLineColor(sm_total_color)
    hbkg_total.SetFillStyle(sm_total_style)
    hbkg_total.SetLineWidth(2)
    hbkg_total.SetMarkerSize(0)

    # add entries to legend
    legymin = 0.53
    legymax = 0.85

    legxmin = 0.53
    legxmax = 0.91

    legend1 = legend(legxmin, legymin, legxmax, legymax, columns=2)
    legend2 = legend(legxmin, legymin-.15, legxmax-0.035, legymin -.01)

    for name, hist in merged_bkgs.iteritems():
        legend1.AddEntry(hist, labels_dict[name], 'f')

    legend1.AddEntry(hbkg_total, "stat #oplus syst", 'f')
    legend1.AddEntry(graph_data, 'Data', 'pl')

    set_style(graph_data, msize=1, lwidth=2, color=ROOT.kBlack)
    set_style(hdata, msize=1, lwidth=2, color=ROOT.kBlack)

    hdata.GetYaxis().SetTitle("Number of events")
    hdata.GetYaxis().SetTitleSize(0.06)
    hdata.GetYaxis().SetTitleOffset(0.65)
    hdata.GetXaxis().SetLabelSize(0.00)
    hdata.GetYaxis().SetLabelSize(0.05)


    # current
    hdata.Draw('p')
    stack.Draw("histsame")
    graph_data.Draw("P0Z")
    hbkg.Draw("histsame")
    hbkg_total.Draw("E2same][")
    graph_data.Draw("P0Z")

    text = style.data_label
    t = ROOT.TLatex(0, 0, text)
    t.SetNDC()
    t.SetTextFont(42)
    t.SetTextSize(0.05)
    t.SetTextColor(ROOT.kBlack)

    t.DrawLatex(0.15, 0.80, style.atlas_label)
    t.DrawLatex(0.15, 0.72, text)
    #t.DrawLatex(0.15, 0.64, region_name) #.replace('L', '{L}').replace('H', '{H}'))

    legend1.Draw()

    cup.RedrawAxis()

    cdown.cd()

    # Draw frame with pulls
    frame = get_frame(npar)
    for b in xrange(1, hdata.GetNbinsX()+1):
        label = hdata.GetXaxis().GetBinLabel(b)
        if 'SRi' in label:
            label = label.replace('SRi', 'SR')

        if label.endswith('L'):
            label = label[:-1]+'_{L}'
        elif label.endswith('H'):
            label = label[:-1]+'_{H}'

        frame.GetXaxis().SetBinLabel(b, label)

    frame.GetXaxis().SetLabelSize(0.15)
    frame.Draw()


    l1 = ROOT.TLine(0, -1., npar, -1.)
    l2 = ROOT.TLine(0,  1., npar,  1.)
    
    ROOT.SetOwnership(l1, False)
    ROOT.SetOwnership(l2, False)
    
    l1.SetLineStyle(3)
    l2.SetLineStyle(3)
    
    l1.Draw()
    l2.Draw()


    allp = get_boxes(regions_pull, frame, True)
    
    for ext in args.extensions.split(','):
        c.Print(args.output_dir+'/pull_regions.' + ext)

    return




# Run YieldsTable.py with all regions and samples requested
pickle_filename = "yield_all.pickle"

samples = ','.join(backgrounds)

cmd = "YieldsTable.py -c %s -s %s -w %s -o yield_all.tex" % (",".join(regions), samples, workspace)
print cmd
subprocess.call(cmd, shell=True)
picklefile = open(pickle_filename,'rb')

mydict = pickle.load(picklefile)

results = []

for region in mydict["names"]:

    index = mydict["names"].index(region)

    n_obs = mydict["nobs"][index]
    n_exp = mydict["TOTAL_FITTED_bkg_events"][index]

    exp_syst = mydict["TOTAL_FITTED_bkg_events_err"][index]

    n_exp_components = []
    for sam in samples.split(","):
        if "Fitted_events_"+sam in mydict:
            n_exp_components.append((sam, mydict["Fitted_events_"+sam][index]))
        else:
            n_exp_components.append((sam, 0.))

    results.append((region, n_obs, n_exp, exp_syst, n_exp_components))


#pull
make_hist_pull_plot(samples, regions, results)
