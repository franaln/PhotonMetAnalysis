#! /usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)

import sys, argparse
from miniutils import get_sample_datasets, get_sumw, get_events
from rootutils import *
from drawutils import draw_grid_frame
from  regions import SR_L, SR_H, SRincl_L, SRincl_H
from mass_dict import mass_dict



gl_min = 1146
gl_max = 2050
n1_min = 147
n1_max = 2050

gl_bins = (gl_max - gl_min) / 25
n1_bins = (n1_max - n1_min) / 25

h_srl = ROOT.TH2F('h_srl', 'h_srh', gl_bins, gl_min, gl_max, n1_bins, n1_min, n1_max)
h_srh = ROOT.TH2F('h_srh', 'h_srh', gl_bins, gl_min, gl_max, n1_bins, n1_min, n1_max)

h_sril = ROOT.TH2F('h_sril', 'h_sril', gl_bins, gl_min, gl_max, n1_bins, n1_min, n1_max)
h_srih = ROOT.TH2F('h_srih', 'h_srih', gl_bins, gl_min, gl_max, n1_bins, n1_min, n1_max)

h_srl.SetDirectory(0)
h_srh.SetDirectory(0)
h_sril.SetDirectory(0)
h_srih.SetDirectory(0)

ROOT.SetOwnership(h_srl, False)
ROOT.SetOwnership(h_srh, False)
ROOT.SetOwnership(h_sril, False)
ROOT.SetOwnership(h_srih, False)


for (m3, mu) in sorted(mass_dict.iterkeys()):

    mgl, mn1 = mass_dict[(int(m3), int(mu))]

    name = 'GGM_M3_mu_%i_%i' % (m3, mu)

    # total events
    ds = get_sample_datasets(name)[0]
    
    total_events = get_sumw(ds)

    srl_events = get_events(name, selection=SR_L, scale=False).mean
    srh_events = get_events(name, selection=SR_H, scale=False).mean

    sril_events = get_events(name, selection=SRincl_L, scale=False).mean
    srih_events = get_events(name, selection=SRincl_H, scale=False).mean

    if total_events == 0:
        continue

    srl_acceff = round(srl_events/total_events, 2)
    srh_acceff = round(srh_events/total_events, 2)

    sril_acceff = round(sril_events/total_events, 2)
    srih_acceff = round(srih_events/total_events, 2)

    h_srl.Fill(mgl, mn1, srl_acceff)
    h_srh.Fill(mgl, mn1, srh_acceff)

    h_sril.Fill(mgl, mn1, sril_acceff)
    h_srih.Fill(mgl, mn1, srih_acceff)

    # print mgl, mn1, total_events, srl_events, srh_events, sril_events, srih_events, srl_acceff, srh_acceff, sril_acceff, srih_acceff

# plot
set_atlas_style()
set_palette()

# SRL
frame_srl = draw_grid_frame() 
frame_srl.SetRightMargin(0.15)

h_srl.SetContour(999)
h_srl.GetZaxis().SetRangeUser(0, 0.4)
h_srl.SetMarkerStyle(21)
h_srl.SetMarkerSize(100)
h_srl.Draw('pcolzsame')

l = ROOT.TLatex()
l.SetNDC()
l.SetTextSize(0.035)
l.DrawLatex(0.17, 0.85, 'Acceptance #times efficiency')
l.DrawLatex(0.17, 0.78, 'SR_{L}')

frame_srl.RedrawAxis()
frame_srl.SaveAs('acc_times_eff_srl.pdf')

# SRH
frame_srh = draw_grid_frame() 
frame_srh.SetRightMargin(0.15)

h_srh.SetContour(999)
h_srh.GetZaxis().SetRangeUser(0, 0.4)
h_srh.SetMarkerStyle(21)
h_srh.SetMarkerSize(100)
h_srh.Draw('pcolzsame')

l = ROOT.TLatex()
l.SetNDC()
l.SetTextSize(0.035)
l.DrawLatex(0.17, 0.85, 'Acceptance #times efficiency')
l.DrawLatex(0.17, 0.78, 'SR_{H}')

frame_srh.RedrawAxis()
frame_srh.SaveAs('acc_times_eff_srh.pdf')

# SRIL
frame_sril = draw_grid_frame() 
frame_sril.SetRightMargin(0.15)

h_sril.SetContour(999)
h_sril.GetZaxis().SetRangeUser(0, 0.4)
h_sril.SetMarkerStyle(21)
h_sril.SetMarkerSize(100)
h_sril.Draw('pcolzsame')

l = ROOT.TLatex()
l.SetNDC()
l.SetTextSize(0.035)
l.DrawLatex(0.17, 0.85, 'Acceptance #times efficiency')
l.DrawLatex(0.17, 0.78, 'SR^{incl}_{L}')

frame_sril.RedrawAxis()
frame_sril.SaveAs('acc_times_eff_sril.pdf')

# SRIH
frame_srih = draw_grid_frame() 
frame_srih.SetRightMargin(0.15)

h_srih.SetContour(999)
h_srih.GetZaxis().SetRangeUser(0, 0.4)
h_srih.SetMarkerStyle(21)
h_srih.SetMarkerSize(100)
h_srih.Draw('pcolzsame')

l = ROOT.TLatex()
l.SetNDC()
l.SetTextSize(0.035)
l.DrawLatex(0.17, 0.85, 'Acceptance #times efficiency')
l.DrawLatex(0.17, 0.78, 'SR^{incl}_{H}')

frame_srih.RedrawAxis()
frame_srih.SaveAs('acc_times_eff_srih.pdf')


