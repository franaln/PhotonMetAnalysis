#! /usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)

import sys, argparse
from miniutils import get_events
from rootutils import *
from drawutils import draw_grid_frame
import regions as regions_
from mass_dict import mass_dict



backgrounds = [
    'photonjet',
    'wgamma',
    'zgamma',
    'ttbarg',
    'jfake',
    'efake',
    ]

regions = [
    'CRQ_L',
    'CRW_L',
    'CRT_L',

    'CRQ_H',
    'CRW_H',
    'CRT_H',
    
    'VR1_L',
    'VR2_L',
    'VR3_L',
    'VR4_L',
]


for region in regions:

    selection = getattr(regions_, region)

    total_bkg = 0
    for bkg in backgrounds:
        total_bkg += get_events(bkg, selection=selection).mean

    gl_min = 1146
    gl_max = 2050
    n1_min = 147
    n1_max = 2050

    gl_bins = (gl_max - gl_min) / 25
    n1_bins = (n1_max - n1_min) / 25

    hmap = ROOT.TH2F('hmap', 'hmap', gl_bins, gl_min, gl_max, n1_bins, n1_min, n1_max)
    hmap.SetDirectory(0)
    ROOT.SetOwnership(hmap, False)

    largest_cont = 0

    for (m3, mu) in mass_dict.iterkeys():

        mgl, mn1 = mass_dict[(int(m3), int(mu))]

        name = 'GGM_M3_mu_%i_%i' % (m3, mu)

        sig = get_events(name, selection=selection).mean
        contamination = round(sig/(sig+total_bkg) * 100, 2)

        if contamination > largest_cont:
            largest_cont = contamination

        hmap.Fill(mgl, mn1, contamination)



    set_atlas_style()
    set_palette()

    frame = draw_grid_frame() 
    frame.SetRightMargin(0.15)

    # hmap.GetZaxis().SetTitle('Signal Contamination [%]')
    # hmap.GetZaxis().SetTitleOffset(1.4)

    hmap.SetContour(999)
    hmap.GetZaxis().SetRangeUser(0, 100)
    hmap.SetMarkerStyle(21)
    hmap.SetMarkerSize(100)
    hmap.Draw('pcolzsame')

    l = ROOT.TLatex()
    l.SetNDC()
    l.SetTextSize(0.035)
    l.DrawLatex(0.17, 0.85, 'Signal Contamination [%]')
    l.DrawLatex(0.17, 0.78, region.replace('_L', '_{L}').replace('_H', '_{H}'))

    frame.RedrawAxis()
    frame.SaveAs('signal_contamination_'+region+'.pdf')


