#! /usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)

import sys, argparse
from miniutils import get_sample_datasets, get_sumw, get_events
from rootutils import *
from drawutils import draw_grid_frame, grid_histogram
from  regions import SRL200, SRL300, SRH
from signalgrid import mg_gg_grid

import style

gl_min = 1146
gl_max = 2400
n1_min = 147
n1_max = 2400

gl_bins = (gl_max - gl_min) / 25
n1_bins = (n1_max - n1_min) / 25

h_sel_srl200 = grid_histogram('h_sel_srl200')
h_sel_srl300 = grid_histogram('h_sel_srl300')
h_sel_srh = grid_histogram('h_sel_srh')

h_srl200     = grid_histogram('h_srl200')
h_srl300     = grid_histogram('h_srl300')
h_srh     = grid_histogram('h_srh')

h_sel_srl200.SetDirectory(0)
h_sel_srl300.SetDirectory(0)
h_sel_srh.SetDirectory(0)
h_srl200.SetDirectory(0)
h_srl300.SetDirectory(0)
h_srh.SetDirectory(0)

ROOT.SetOwnership(h_srl200, False)
ROOT.SetOwnership(h_srl300, False)
ROOT.SetOwnership(h_srh, False)
ROOT.SetOwnership(h_sel_srl200, False)
ROOT.SetOwnership(h_sel_srl300, False)
ROOT.SetOwnership(h_sel_srh, False)

for (m3, mu), (mgl, mn1) in sorted(mg_gg_grid.iteritems()):

    name = 'GGM_GG_bhmix_%i_%i' % (m3, mu)

    # total events
    ds = get_sample_datasets(name)[0]
    total_events = get_sumw(ds)

    if total_events == 0:
        continue

    srl200_events_scaled = get_events(name, selection=SRL200, lumi='data').mean
    srl300_events_scaled = get_events(name, selection=SRL300, lumi='data').mean
    srh_events_scaled    = get_events(name, selection=SRH,    lumi='data').mean

    h_sel_srl200.Fill(mgl, mn1, round(srl200_events_scaled, 2))
    h_sel_srl300.Fill(mgl, mn1, round(srl300_events_scaled, 2))
    h_sel_srh   .Fill(mgl, mn1, round(srh_events_scaled, 2))

    srl200_events = get_events(name, selection=SRL200, scale=False).mean
    srl300_events = get_events(name, selection=SRL300, scale=False).mean
    srh_events    = get_events(name, selection=SRH, scale=False).mean

    ## acc x eff
    srl200_acceff = round(srl200_events/total_events, 2)
    srl300_acceff = round(srl300_events/total_events, 2)
    srh_acceff = round(srh_events/total_events, 2)

    h_srl200.Fill(mgl, mn1, srl200_acceff)
    h_srl300.Fill(mgl, mn1, srl300_acceff)
    h_srh.Fill(mgl, mn1, srh_acceff)


# plot
set_atlas_style()

# SRL200
frame_srl200 = draw_grid_frame() 
frame_srl200.SetRightMargin(0.15)

h_srl200.SetContour(999)
h_srl200.GetZaxis().SetRangeUser(0, 0.4)
h_srl200.SetMarkerStyle(21)
h_srl200.SetMarkerSize(100)
h_srl200.Draw('pcolzsame')

l = ROOT.TLatex()
l.SetNDC()
l.SetTextSize(0.035)
l.DrawLatex(0.17, 0.85, 'Acceptance #times efficiency')
l.DrawLatex(0.17, 0.78, 'SRL200')

frame_srl200.RedrawAxis()
frame_srl200.SaveAs('acc_times_eff_srl200.pdf')

# SRL300
frame_srl300 = draw_grid_frame() 
frame_srl300.SetRightMargin(0.15)

h_srl300.SetContour(999)
h_srl300.GetZaxis().SetRangeUser(0, 0.4)
h_srl300.SetMarkerStyle(21)
h_srl300.SetMarkerSize(100)
h_srl300.Draw('pcolzsame')

l = ROOT.TLatex()
l.SetNDC()
l.SetTextSize(0.035)
l.DrawLatex(0.17, 0.85, 'Acceptance #times efficiency')
l.DrawLatex(0.17, 0.78, 'SRL300')

frame_srl300.RedrawAxis()
frame_srl300.SaveAs('acc_times_eff_srl300.pdf')

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
l.DrawLatex(0.17, 0.78, 'SRH')

frame_srh.RedrawAxis()
frame_srh.SaveAs('acc_times_eff_srh.pdf')


# Expected events
# SRL200
frame_exp_srl200 = draw_grid_frame() 
frame_exp_srl200.SetRightMargin(0.15)

h_sel_srl200.SetContour(999)
h_sel_srl200.GetZaxis().SetRangeUser(0.5, 10)
h_sel_srl200.SetMarkerStyle(21)
h_sel_srl200.SetMarkerSize(0.8)
h_sel_srl200.Draw('text same')

l = ROOT.TLatex()
l.SetNDC()
l.SetTextSize(0.035)
l.DrawLatex(0.17, 0.85, 'Expected events '+style.data_label)
l.DrawLatex(0.17, 0.78, 'SRL200')

frame_exp_srl200.RedrawAxis()
frame_exp_srl200.SaveAs('exp_events_srl200.pdf')

# SRL300
frame_exp_srl300 = draw_grid_frame() 
frame_exp_srl300.SetRightMargin(0.15)

h_sel_srl300.SetContour(999)
h_sel_srl300.GetZaxis().SetRangeUser(0.5, 10)
h_sel_srl300.SetMarkerStyle(21)
h_sel_srl300.SetMarkerSize(0.8)
h_sel_srl300.Draw('text same')

l = ROOT.TLatex()
l.SetNDC()
l.SetTextSize(0.035)
l.DrawLatex(0.17, 0.85, 'Expected events '+style.data_label)
l.DrawLatex(0.17, 0.78, 'SRL300')

frame_exp_srl300.RedrawAxis()
frame_exp_srl300.SaveAs('exp_events_srl300.pdf')

# SRH
frame_exp_srh = draw_grid_frame() 
frame_exp_srh.SetRightMargin(0.15)

h_sel_srh.SetContour(999)
h_sel_srh.GetZaxis().SetRangeUser(0, 10)
h_sel_srh.SetMarkerStyle(21)
h_sel_srh.SetMarkerSize(0.8)
h_sel_srh.Draw('text same')

l = ROOT.TLatex()
l.SetNDC()
l.SetTextSize(0.035)
l.DrawLatex(0.17, 0.85, 'Expected events '+style.data_label)
l.DrawLatex(0.17, 0.78, 'SRH')

frame_exp_srh.RedrawAxis()
frame_exp_srh.SaveAs('exp_events_srh.pdf')
