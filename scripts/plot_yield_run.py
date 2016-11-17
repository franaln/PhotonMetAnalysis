"""
Plot analysis selection efficiency and lumi-normalized yield (new!) in VRs, SRs and CRs as a function of the run number (obviously in data). Purpose: check for potential temporary issues in data only there for certain runs, and to reveal potential chunks of data not processed by mistake. You should normalize the per-run yield using the lumi as reported from an independent source (not the in-file metadata!), e.g. ATLAS Run Query (see e.g. this script for inspiration of how to use ARQ from python) or simply use this new script in SUSYTools to build the luminosity-vs-run histogram from your iLumiCalc file.
"""

import os
import sys
import glob
import ROOT

from rootutils import set_atlas_style, set_style
from regions import CRQ_L

sys.path.append(os.getenv('SUSY_ANALYSIS')+'/data')
from run_lumi_dict_2015 import run_lumi_dict as run_lumi_dict_2015
from run_lumi_dict_2016 import run_lumi_dict as run_lumi_dict_2016

nruns = len(run_lumi_dict_2015) + len(run_lumi_dict_2016)

run_lumi_dict = dict(run_lumi_dict_2015, **run_lumi_dict_2016)

# config
selection = 'ph_n>0 && ph_pt[0]>145  && el_n+mu_n==0 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4'
seltext   = '>0 photons, p^{#gamma}_{T}>145 GeV, no lep, >2 jets, #Delta#phi cleaning'
outname   = 'yields_lumi_presel'


h_yields = ROOT.TH1D('yields', 'yields', nruns, 0.5, nruns+0.5)
h_lumi   = ROOT.TH1D('lumi', 'lumi', nruns, 0.5, nruns+0.5)
h_yields_norm = ROOT.TH1D('yields_norm', 'yields_norm', nruns, 0.5, nruns+0.5)
h_avgmu  = ROOT.TH1D('avgmu', 'avgmu', nruns, 0.5, nruns+0.5)

h_yields_norm.Sumw2()

mean = 0

counter = 1
for run, lumi in sorted(run_lumi_dict.iteritems()):

    h_yields_norm.GetXaxis().SetBinLabel(counter, '%i' % run)

    if run > 290000:
        data = 'data16'
    else:
        data = 'data15'

    path = '/raid/falonso/mini2/v45/%s_13TeV.00%i.physics_Main.mini.*.v45_output.root' % (data, run)

    gpaths = glob.glob(path)
    # if not os.path.exists(path):
    #     path = '/raid/falonso/mini2/v37/%s_13TeV.00%i.physics_Main.mini.p2689.v37_output.root' % (data, run)

    tree = ROOT.TChain('mini')
    tree.Add(gpaths[0])

    # yield
    htemp  = ROOT.TH1D('tmp_%i' % run, 'tmp', 1, 0.5, 1.5)
    htemp.Sumw2()

    tree.Project('tmp_%i' % run, '1', selection)

    error = ROOT.Double(0.0)
    integral = htemp.IntegralAndError(1, htemp.GetNbinsX()+1, error)
    
    norm_yield = integral / lumi
    mean += norm_yield

    h_lumi.SetBinContent(counter, lumi)
    h_yields.SetBinContent(counter, integral)
    h_yields_norm.SetBinContent(counter, norm_yield)
    h_yields_norm.SetBinError(counter, error/lumi)

    print run, norm_yield

    # avgmu
    htemp = ROOT.TH1D('avgmu_%i' % run, 'avgmu', 50, 0., 50.)
    tree.Project('avgmu_%i' % run, 'avgmu', selection)

    h_avgmu.SetBinContent(counter, htemp.GetMean())
    

    counter += 1


set_atlas_style()

set_style(h_yields_norm, color=ROOT.kBlack, lwidth=1)
set_style(h_avgmu,   color='pink', lwidth=1, alpha=0.5)

c = ROOT.TCanvas('', '', 2400, 600)

c.SetFillColor(0)
c.SetBorderMode(0)
c.SetBorderSize(2)
c.SetTicks(0,1)
c.SetTickx(0)
c.SetTopMargin  (0.03)
c.SetRightMargin(0.02)
c.SetLeftMargin (0.05)
c.SetBottomMargin  (0.1)

h_yields_norm.GetYaxis().SetTitle('yield per pb^{-1}')
h_yields_norm.GetYaxis().SetTitleOffset(0.5)

h_yields_norm.GetYaxis().SetRangeUser(h_yields_norm.GetMinimum()*0.5, h_yields_norm.GetMaximum()*1.5)

h_yields_norm.Draw('p')

l = ROOT.TLine(h_yields.GetXaxis().GetXmin(), mean/nruns, h_yields.GetXaxis().GetXmax(), mean/nruns)
l.SetLineStyle(2)
l.SetLineColor(ROOT.kGray+1)
l.Draw()

h_yields_norm.Draw('p same')

x15 = len(run_lumi_dict_2015) + 0.55

l2 = ROOT.TLine(x15, -300, x15, 300)
l2.SetLineStyle(2)
l2.SetLineColor(ROOT.kAzure)
l2.Draw()

leg = ROOT.TLegend(0.82, 0.72, 0.96, 0.94)
leg.SetBorderSize(0)
leg.AddEntry(h_yields_norm, 'yield per pb^{-1}')
leg.AddEntry(l, 'mean', 'l')
leg.AddEntry(l2, '2015 | 2016', 'l')
#leg.AddEntry(h_avgmu, '#LT#mu#GT', 'l')
leg.Draw()

ll = ROOT.TLatex()
ll.SetNDC()
ll.DrawLatex(0.1, 0.88, 'Data 2015+2016, ~13.3 fb^{-1}')
ll.DrawLatex(0.1, 0.78, 'Sel: %s' % seltext)

c.RedrawAxis()

c.SaveAs(outname+'.pdf')


