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
from rootutils import *
from collections import OrderedDict

from drawlib import colors_dict, labels_dict, calc_poisson_cl_upper, calc_poisson_cl_lower
import subprocess

region_name = 'SRL'

region_type = region_name[-1]
filename = "BkgOnlyFit_combined_BasicMeasurement_model_afterFit_%s.root" % region_name


# regions
if region_name == 'SRL':
    regions = [
        'CRM',
        'CRLW',
        'CRLT',
        'VRQ',
        # 'VRM50',
        'VRM75',
        'VRM100',
        'VRR',
        'VCRLWrt',
        'VCRLWmet',
        'VCRLTrt',
        'VCRLTmet',
        'SR',
    ]
else:
    regions = [
        'CRM',
        'CRLW',
        'CRLT',
        'VRQ',
        'VRH',
        'VCRLWht',
        'VCRLWmet',
        'VCRLTht',
        'VCRLTmet',
        'SR',
    ]

region_labels = {
    'SR': 'SR',
    'CRM': 'CRQ',
    'CRLW': 'CRW',
    'CRLT': 'CRT',
    'VRQ': 'VRQ',
    'VRM50': 'VRM50',
    'VRM75': 'VRM75',
    'VRM100': 'VRM100',
    'VCRLWrt': 'VRWM',
    'VCRLWmet':'VRWR',
    'VCRLTrt': 'VRTM',
    'VCRLTmet':'VRTR',
    'VRH': 'VRH',
    'VCRLWht': 'VRWH',
    'VCRLTht': 'VRTH',
}


set_atlas_style()

# Backgrounds
backgrounds = [
    'wgamma',
    'zllgamma',
    'znunugamma',
    'ttbarg',
    'topgamma',
    'vqqgamma',
    'ttbarghad',
    'efake',
    'jfake',
    'photonjet_sherpa'
]

mu_q = {
    'L': Value(0.94, 0.44),
    'H': Value(1.22, 0.58),
}

mu_w = {
    'L': Value(1.34, 0.89),
    'H': Value(1.24, 0.39),
}

mu_t = {
    'L': Value(1.40, 0.77),
    'H': Value(0.54, 0.37),
}


def get_histogram(sample, variable, selection='', syst='Nom'):
    hname = 'h%s%s_%s_obs_%s' % (sample, syst, region, variable)
    hname = hname.replace('_all_', '_')
    print hname

    hist = cutsfile.Get(hname)
    hist.SetDirectory(0)

    return hist.Clone()



import os, string, pickle, copy

def getSampleColor(sample):
    return 1

def get_region_color(region):

    if 'SR' in region:
        return get_color('#00ef6a')
    elif 'CR' in region:
        return get_color('#ef000e')
    else:
        return get_color('#0086ef')

    return 1

def PoissonError(obs):

    posError = ROOT.TMath.ChisquareQuantile(1. - (1. - 0.68)/2. , 2.* (obs + 1.)) / 2. - obs - 1
    negError = obs - ROOT.TMath.ChisquareQuantile((1. - 0.68)/2., 2.*obs) / 2

    symError = abs(posError-negError)/2.

    return (posError, negError, symError)

def MakeBox(color=ROOT.kGray+1, offset=0, pull=-1, horizontal=False):

    graph = ROOT.TGraph(4)

    if horizontal:
        graph.SetPoint(0,0.1+offset,0)
        graph.SetPoint(1,0.1+offset,pull)
        graph.SetPoint(2,0.9+offset,pull)
        graph.SetPoint(3,0.9+offset,0)
    else:
        graph.SetPoint(0,0,0.3+offset)
        graph.SetPoint(1,pull,0.3+offset)
        graph.SetPoint(2,pull,0.7+offset)
        graph.SetPoint(3,0,0.7+offset)

    graph.SetFillColor(color)
    graph.SetLineColor(color)
    # graph.SetLineWidth(1)
    # graph.SetLineStyle(1)

    return graph


def GetFrame(prefix, npar, horizontal=False):

    offset = 0.;
    if horizontal:
        frame = ROOT.TH2F("frame"+prefix, "", npar, 0., npar, 8, -4., 4.);
        frame.GetYaxis().SetTitleSize(0.1)
        frame.GetYaxis().CenterTitle()
        frame.GetYaxis().SetTitleOffset(0.4)
        frame.GetYaxis().SetRangeUser(-2.2, 2.2)
        frame.GetXaxis().SetLabelOffset(0.03)
        frame.GetXaxis().SetLabelSize(0.12)
        frame.GetYaxis().SetLabelSize(0.12)
        frame.GetYaxis().SetNdivisions(4)
        frame.SetYTitle("(n_{obs} - n_{exp}) / #sigma_{tot}")
    else:
        frame = ROOT.TH2F("frame"+prefix, prefix, 1, -3.5, 3.5, npar, -offset, npar+offset)

        scale=1.0
        frame.SetLabelOffset( 0.012, "Y" );# label offset on x axis
        frame.GetYaxis().SetTitleOffset( 1.25 )
        frame.GetXaxis().SetTitleSize(0.06)
        frame.GetYaxis().SetTitleSize(0.06)
        frame.GetXaxis().SetLabelSize(0.06)
        frame.GetYaxis().SetLabelSize(0.07)
        npar = len(regionList)

        frame.SetLineColor(0);
        frame.SetTickLength(0,"Y");
        frame.SetXTitle("(n_{obs} - n_{exp}) / #sigma_{tot}")
        frame.SetLabelOffset(0.001, "X")
        frame.SetTitleOffset(1. , "X")
        frame.SetTitleSize(0.06, "X" )
        frame.GetYaxis().CenterLabels(1)
        frame.GetYaxis().SetNdivisions( frame.GetNbinsY()+10, 1 );

    # global style settings
    ROOT.gPad.SetTicks();
    frame.SetLabelFont(42,"X");
    frame.SetTitleFont(42,"X");
    frame.SetLabelFont(42,"Y");
    frame.SetTitleFont(42,"Y");

    return copy.deepcopy(frame)

def GetBoxes(allp, results, frame, horizontal=False):

    counter = 0
    myr = reversed(results)
    if horizontal:
        myr = results
    for info in myr:
        name = info[0].replace(" ","")
        name = info[0].replace("_cuts","")

        if name in region_labels.keys():
            name = region_labels[name]


        if horizontal:
            for b in xrange(1,frame.GetNbinsX()+2):
                if frame.GetXaxis().GetBinLabel(b) != name: continue
                counter = b - 1
                break
            #frame.GetXaxis().SetBinLabel(counter+1,name);
        else:
            frame.GetYaxis().SetBinLabel(counter+1,name);

        color = get_region_color(name)

        graph = MakeBox(offset=counter, pull=float(info[1]), color=color, horizontal=horizontal)
        graph.Draw("LF")

        counter += 1
        allp.append(graph)

    return

def make_hist(regions, results, hdata, hbkg, hbkg_up, hbkg_dn, graph_bkg, graph_bkg2, graph_bkg3, graph_data, graph_pull, hbkg_components):

    ymax = 0
    ymin = 99999999999.

    # loop over all the regions
    for counter in xrange(len(regions)):

        n_obs = 0
        n_exp = 0

        exp_syst = 0

        exp_stat = 0
        exp_stat_up = 0
        exp_stat_dn = 0

        exp_total = 0
        exp_total_up = 0
        exp_total_dn = 0

        pull = 0

        name = regions[counter].replace(" ","")
        if name in region_labels.keys():
            name = region_labels[name]

        # extract the information
        for info in results:
            if regions[counter] in info[0]:
                n_obs = info[2]
                n_exp = info[3]
                exp_syst = info[4]

                if n_exp > 0:
                    exp_stat = ROOT.TMath.Sqrt(n_exp)

                exp_stat_tuple = PoissonError(n_exp)
                exp_stat_up = exp_stat_tuple[0]
                exp_stat_dn = exp_stat_tuple[1]

                if name.find("CR") < 0:
                    exp_total    = ROOT.TMath.Sqrt(exp_stat*exp_stat + exp_syst*exp_syst)
                    exp_total_up = ROOT.TMath.Sqrt(exp_stat_up*exp_stat_up + exp_syst*exp_syst)
                    exp_total_dn = ROOT.TMath.Sqrt(exp_stat_dn*exp_stat_dn + exp_syst*exp_syst)
                else:
                    exp_total = exp_syst

                if (n_obs - n_exp)>=0 and exp_total_up != 0:
                    pull = (n_obs-n_exp)/exp_total_up

                if (n_obs - n_exp)<=0 and exp_total_dn != 0:
                    pull = (n_obs-n_exp)/exp_total_dn

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

                #bkg components
                compInfo = info[6]
                for i in xrange(len(compInfo)):
                    hbkg_components[i].SetBinContent(counter+1, compInfo[i][1])

                break

        if n_obs > ymax:
            ymax = n_obs

        if n_exp + exp_total_up > ymax:
            ymax = n_exp + exp_total_up

        if n_obs < ymin and n_obs != 0:
            ymin = n_obs

        if n_exp < ymin and n_exp != 0:
            ymin = n_exp


        graph_bkg.SetPoint(counter, hbkg.GetBinCenter(counter+1), n_exp)
        graph_bkg.SetPointError(counter,0.5,0.5, exp_total_dn, exp_total_up)

        # graph_bkg_up.SetPoint(counter,hbkg.GetBinCenter(counter+1), n_exp)
        # graph_bkg_up.SetPointError(counter,0.5,0.5, exp_total_dn, exp_total_up)

        # graph_bkg3.SetPoint(counter,hbkg.GetBinCenter(counter+1), n_exp)
        # graph_bkg3.SetPointError(counter, 0.5, 0.5, 0, 0)

        graph_data.SetPoint(counter, hbkg.GetBinCenter(counter+1), n_obs)

        #if n_obs > 0.:
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

        graph_data.SetPointError(counter, x_el, x_eu, y_el, y_eu)

        graph_pull.SetPoint(counter,hbkg.GetBinCenter(counter+1), pull)
        graph_pull.SetPointError(counter,0.,0,0,0)


        hdata.GetXaxis().SetBinLabel(counter+1, name)
        hdata.SetBinContent(counter+1, n_obs)
        #hdata.SetBinError(counter+1,0.00001)
        hdata.SetBinErrorOption(ROOT.TH1.kPoisson)

        hbkg.SetBinContent(counter+1, n_exp)
        hbkg.SetBinError(counter+1, exp_stat)

        hbkg_up.SetBinContent(counter+1, n_exp + exp_total_up)
        hbkg_dn.SetBinContent(counter+1, n_exp - exp_total_dn)


    hdata.SetMaximum(1000*ymax)
    hdata.SetMinimum(0.05)

    return


def make_hist_pull_plot(samples, regions, prefix, hresults):

    ROOT.gStyle.SetOptStat(0000)

    npar = len(regions)

    hdata = ROOT.TH1F(prefix, prefix, npar, 0, npar);
    #hdata.SetMarkerStyle(20)

    hbkg    = ROOT.TH1F("hbkg", "hbkg", npar,0, npar);

    hbkg_up = ROOT.TH1F("hbkg_up","hbkg_up", npar, 0, npar);
    hbkg_up.SetLineStyle(2)

    hbkg_dn = ROOT.TH1F("hbkg_dn", "hbkg_dn", npar, 0, npar);
    hbkg_dn.SetLineStyle(2)

    hbkg_components = []
    for sam in samples.split(","):
        h = ROOT.TH1F("hbkg_"+sam,"hbkg_"+sam, npar, 0, npar)
        hbkg_components.append(h)


    graph_bkg  = ROOT.TGraphAsymmErrors(npar)
    graph_bkg2 = ROOT.TGraphAsymmErrors(npar)
    graph_bkg3 = ROOT.TGraphAsymmErrors(npar)
    graph_data = ROOT.TGraphAsymmErrors(npar)
    graph_pull = ROOT.TGraphAsymmErrors(npar)

    make_hist(regions, hresults, hdata, hbkg, hbkg_dn, hbkg_up, graph_bkg, graph_bkg2, graph_bkg3, graph_data, graph_pull, hbkg_components)

    c = ROOT.TCanvas("c"+prefix,prefix,800,600);

    cup   = ROOT.TPad("u", "u", 0., 0.305, 0.99, 1)
    cdown = ROOT.TPad("d", "d", 0., 0.01, 0.99, 0.295)

    cup.SetLogy()

    cup.SetFillColor(0);
    cup.SetBorderMode(0);
    cup.SetBorderSize(2);
    cup.SetTicks()
    cup.SetTopMargin   ( 0.1 );
    cup.SetRightMargin ( 0.05 );
    cup.SetBottomMargin( 0.0025 );
    cup.SetLeftMargin( 0.10 );
    cup.SetFrameBorderMode(0);
    cup.SetFrameBorderMode(0);
    cup.Draw()

    cdown.SetGridx();
    cdown.SetGridy();
    cdown.SetFillColor(0);
    cdown.SetBorderMode(0);
    cdown.SetBorderSize(2);
    cdown.SetTickx(1);
    cdown.SetTicky(1);
    cdown.SetTopMargin   ( 0.003 );
    cdown.SetRightMargin ( 0.05 );
    cdown.SetBottomMargin( 0.3 );
    cdown.SetLeftMargin( 0.10 );
    cdown.Draw()

    c.SetFrameFillColor(ROOT.kWhite)

    cup.cd()

    stack = ROOT.THStack("stack","stack")


    # merge backgrounds
    to_merge = {}
    merged_bkgs = OrderedDict()

    for sample, hist in zip(samples.split(','), hbkg_components):
        to_merge[sample] = hist

    merged_bkgs['gamjet'] = to_merge['photonjet_sherpa']
    merged_bkgs['tgamma'] = to_merge['topgamma'] + to_merge['ttbarg'] + to_merge['ttbarghad']
    merged_bkgs['efake'] = to_merge['efake']
    merged_bkgs['jfake'] = to_merge['jfake']
    merged_bkgs['vgamma'] = to_merge['wgamma'] + to_merge['zllgamma'] + to_merge['vqqgamma'] + to_merge['znunugamma']

    hbkgComponents = merged_bkgs

    for sam, h in hbkgComponents.iteritems():
        set_style(h, color=colors_dict[sam], fill=True)

    # SM stack
    def _compare(a, b):
        amax = a.GetMaximum()
        bmax = b.GetMaximum()
        return cmp(int(amax), int(bmax))

    for hist in sorted(hbkgComponents.itervalues(), _compare):
        stack.Add(hist)


    # Total background
    sm_total = None
    sm_totalerr = None
    sm_total_style = 3354
    sm_total_color = ROOT.kGray+3

    sm_stat_color = ROOT.kGray+1
    sm_syst_color = ROOT.kGray+3

    for h in hbkgComponents.itervalues():
        if sm_total is None:
            sm_total = histogram_equal_to(h)

        sm_total += h


    sm_total_stat = sm_total.Clone()


    sm_total.SetLineWidth(2)
    sm_total.SetLineColor(sm_total_color)
    sm_total.SetFillColor(0)
    sm_total.SetMarkerSize(0)

    sm_total_stat.SetFillColor(sm_total_color)
    sm_total_stat.SetLineColor(sm_total_color)
    sm_total_stat.SetFillStyle(sm_total_style)
    sm_total_stat.SetLineWidth(2)
    sm_total_stat.SetMarkerSize(0)

    # add entries to legend
    legymin = 0.55
    legymax = 0.85

    legxmin = 0.55
    legxmax = 0.91

    legend1 = legend(legxmin, legymin, legxmax, legymax, columns=2)
    legend2 = legend(legxmin, legymin-.15, legxmax-0.035, legymin -.01)

    for name, hist in hbkgComponents.iteritems():
        legend1.AddEntry(hist, labels_dict[name], 'f')

    legend1.AddEntry(sm_total_stat, "stat #oplus syst", 'f')
    legend1.AddEntry(graph_data, labels_dict['data'], 'pl')



    graph_bkg.SetLineWidth(2)
    graph_bkg.SetMarkerSize(0)
    graph_bkg.SetFillStyle(sm_total_style)
    graph_bkg.SetLineColor(sm_total_color)
    graph_bkg.SetFillColor(sm_total_color)

    set_style(graph_data, msize=1, lwidth=2, color=ROOT.kBlack)
    set_style(hdata, msize=1, lwidth=2, color=ROOT.kBlack)


    hdata.GetYaxis().SetTitle("Number of events")
    hdata.GetYaxis().SetTitleSize(0.05)
    hdata.GetYaxis().SetTitleOffset(0.9)
    hdata.GetXaxis().SetLabelSize(0.06)
    hdata.GetYaxis().SetLabelSize(0.05)


    hdata.Draw('e0')
    #graph_data.Draw("P0Z")
    stack.Draw("same")
    # hbkg.Draw("hist,same")
    # hbkg_up.Draw("hist,same")
    # hbkg_dn.Draw("hist,same")
    # sm_total.Draw("histsame")

    graph_bkg.Draw("P2same")
    sm_total.Draw("histsame")
    #graph_data.Draw("P0Z")
    hdata.Draw('e0same')

    text = '#sqrt{s} = 8 TeV, 20.3 fb^{-1}'
    t = ROOT.TLatex(0, 0, text)
    t.SetNDC()
    t.SetTextFont(42)
    t.SetTextSize(0.05)
    t.SetTextColor(ROOT.kBlack)
    t.DrawLatex(0.15, 0.70, text)


    legend1.Draw()

    cup.RedrawAxis()

    cdown.cd()

    # Draw frame with pulls
    frame = GetFrame(prefix, npar, horizontal=True)
    for b in xrange(1,hdata.GetNbinsX()+1):
        frame.GetXaxis().SetBinLabel(b ,hdata.GetXaxis().GetBinLabel(b))

    frame.Draw()

    allp = []
    GetBoxes(allp, hresults, frame, True)

    c.Print("histpull_"+prefix+".pdf")

    return



# h_comp_bkg = OrderedDict()
# for name in backgrounds:
#     h_comp_bkg[name] = ROOT.TH1F(name, name, len(regions), 0, len(regions))

# h_comp_data = ROOT.TH1F('data', 'data', len(regions), 0, len(regions))


# for i, region in enumerate(regions):

#     # get regions histogram
#     h_region_data = get_histogram('data', 'cuts', region)


#     h_region_bkg = dict()
#     for name in h_comp_bkg.iterkeys():
#         h_region_bkg[name] = get_histogram(name, 'cuts', region)


#     # scale bkgs
#     histogram_scale(h_region_bkg['photonjet_sherpa'], mu_q[region_type])

#     histogram_scale(h_region_bkg['wgamma'], mu_w[region_type])
#     histogram_scale(h_region_bkg['vqqgamma'], mu_w[region_type])

#     histogram_scale(h_region_bkg['ttbarg'], mu_t[region_type])
#     histogram_scale(h_region_bkg['ttbarghad'], mu_t[region_type])




#     # add to composition histogram
#     n = h_region_data.GetBinContent(1)
#     e = h_region_data.GetBinError(1)

#     h_comp_data.SetBinContent(i+1, n)
#     h_comp_data.SetBinError(i+1, e)

#     h_comp_data.GetXaxis().SetBinLabel(i+1, region)

#     for name in h_comp_bkg.iterkeys():
#         n = h_region_bkg[name].GetBinContent(1)
#         e = h_region_bkg[name].GetBinError(1)

#         h_comp_bkg[name].SetBinContent(i+1, n)
#         h_comp_bkg[name].SetBinError(i+1, e)

#         h_comp_bkg[name].GetXaxis().SetBinLabel(i+1, region)




# # merge backgrounds
# merged_bkgs = OrderedDict()

# merged_bkgs['gamjet'] = h_comp_bkg['photonjet_sherpa']
# merged_bkgs['tgamma'] = h_comp_bkg['topgamma'] + h_comp_bkg['ttbarg'] + h_comp_bkg['ttbarghad']
# merged_bkgs['efake'] = h_comp_bkg['efake']
# merged_bkgs['jfake'] = h_comp_bkg['jfake']
# merged_bkgs['vgamma'] = h_comp_bkg['wgamma'] + h_comp_bkg['zllgamma'] + h_comp_bkg['vqqgamma'] + h_comp_bkg['znunugamma']

# h_comp_bkg = merged_bkgs


# # plot!
# drawlib.do_plot('region_composition', 'cuts', data=h_comp_data, bkg=h_comp_bkg, do_ratio=True, ratio_type='significance')


# Run YieldsTable.py with all regions and samples requested
pickleFilename = "yield_%s_all.pickle" % (region_name)

samples = ','.join(backgrounds)

if not os.path.isfile(pickleFilename):
    cmd = "YieldsTable.py -c %s -s %s -w %s -o yield_%s_all.tex -t %s" % (",".join(regions), samples, filename, region_name, region_name)
    print cmd
    subprocess.call(cmd, shell=True)


# Open the pickle
# makePullPlot(pickleFilename, regionList, samples, renamedRegions, region, False)



try:
    picklefile = open(pickleFilename,'rb')
except IOError:
    print "Cannot open pickle %s, continuing to next" % pickleFilename

mydict = pickle.load(picklefile)

results = []

for region in mydict["names"]:

    index = mydict["names"].index(region)

    n_obs = mydict["nobs"][index]
    n_exp = mydict["TOTAL_FITTED_bkg_events"][index]

    exp_syst = mydict["TOTAL_FITTED_bkg_events_err"][index]

    exp_stat_tuple = PoissonError(n_exp)
    exp_stat = exp_stat_tuple[2]

    total_u  = ROOT.TMath.Sqrt(exp_syst*exp_syst + exp_stat_tuple[2]*exp_stat_tuple[2])
    total_ul = ROOT.TMath.Sqrt(exp_syst*exp_syst + exp_stat_tuple[1]*exp_stat_tuple[1])
    total_uh = ROOT.TMath.Sqrt(exp_syst*exp_syst + exp_stat_tuple[0]*exp_stat_tuple[0])

    if (n_obs-n_exp) > 0 and total_uh != 0:
        pull = (n_obs-n_exp)/total_uh

    if (n_obs-n_exp) <= 0 and total_ul != 0:
        pull = (n_obs-n_exp)/total_ul

    n_exp_components = []
    for sam in samples.split(","):
        n_exp_components.append((sam, mydict["Fitted_events_"+sam][index]))

    if -0.02 < pull < 0:
        pull = -0.02 ###ATT: ugly

    if 0 < pull < 0.02:
        pull = 0.02 ###ATT: ugly

    # if region.find("SR")>=0 and doBlind:
    #     nbObs = -100
    #     pull = 0

    results.append((region, pull, n_obs, n_exp, exp_syst, total_u, n_exp_components))


#pull
make_hist_pull_plot(samples, regions, region_name, results)
