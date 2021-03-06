#! /usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)

import argparse
import analysis
from miniutils import get_events
from rootutils import *
from drawutils import draw_grid_frame
import regions as regions_
from signalgrid import mg_gg_grid


parser = argparse.ArgumentParser(description='draw_signal_contamination')
parser.add_argument('-r', dest='regions', help='regions', required=True)
parser.add_argument('-o', dest='output_dir', default='.', help='Output dir')
parser.add_argument('--ext', dest='extensions', default='pdf', help='')

args = parser.parse_args()

backgrounds = analysis.backgrounds

regions = args.regions.split(',')

set_atlas_style()
set_palette()

for region in regions:

    selection = getattr(regions_, region)

    total_bkg = 0
    for bkg in backgrounds:
        total_bkg += get_events(bkg, selection=selection, lumi='data').mean

    gl_min = 1300
    gl_max = 2500
    n1_min = 147
    n1_max = 2500

    gl_bins = (gl_max - gl_min) / 30
    n1_bins = (n1_max - n1_min) / 30

    hmap = ROOT.TH2F('hmap', 'hmap', gl_bins, gl_min, gl_max, n1_bins, n1_min, n1_max)
    hmap.SetDirectory(0)
    ROOT.SetOwnership(hmap, False)

    largest_cont = 0

    for (m3, mu), (mgl, mn1) in mg_gg_grid.iteritems():

        name = 'GGM_GG_bhmix_%i_%i' % (m3, mu)

        sig = get_events(name, selection=selection, lumi='data').mean
        contamination = round(sig/(sig+total_bkg) * 100, 2)

        if contamination > largest_cont:
            largest_cont = contamination

        if contamination < 0.001:
            contamination = 0.001

        hmap.Fill(mgl, mn1, contamination)


    frame = draw_grid_frame(800, 800, gl_min, gl_max, n1_min, n1_max) 
    frame.SetRightMargin(0.12)

    hmap.SetContour(999)
    hmap.GetZaxis().SetRangeUser(0, 100)
    hmap.GetZaxis().SetLabelSize(0.03)
    hmap.SetMarkerStyle(21)
    hmap.SetMarkerSize(200)
    hmap.Draw('pcolzsame')

    l = ROOT.TLatex()
    l.SetNDC()
    l.SetTextSize(0.035)
    l.DrawLatex(0.17, 0.85, 'Signal Contamination [%]')
    l.DrawLatex(0.17, 0.78, region.replace('_L', '_{L}').replace('_H', '_{H}'))

    frame.RedrawAxis()

    for ext in args.extensions.split(','):
        frame.SaveAs(args.output_dir+"/signal_contamination_"+region+'.' + ext)


