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
from signalgrid import grid_m3_mu


parser = argparse.ArgumentParser(description='draw_signal_contamination')
parser.add_argument('-r', dest='regions', help='regions')
parser.add_argument('-o', dest='output_dir', default='.', help='Output dir')
parser.add_argument('--ext', dest='extensions', default='pdf', help='')

args = parser.parse_args()

backgrounds = analysis.backgrounds

if args.regions:
    regions = args.regions.split(',')
else:
    regions = [ cr + '_L' for cr in analysis.cr_regions ] + \
        [ cr + '_H' for cr in analysis.cr_regions ] + \
        [ vr + '_L' for vr in analysis.vr_regions ] + \
        [ vr + '_H' for vr in analysis.vr_regions ] 

set_atlas_style()
set_palette()

for region in regions:

    selection = getattr(regions_, region)

    total_bkg = 0
    for bkg in backgrounds:
        total_bkg += get_events(bkg, selection=selection, lumi='data').mean

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

    for (m3, mu), (mgl, mn1) in grid_m3_mu.iteritems():

        name = 'GGM_M3_mu_%i_%i' % (m3, mu)

        sig = get_events(name, selection=selection, lumi='data').mean
        contamination = round(sig/(sig+total_bkg) * 100, 2)

        if contamination > largest_cont:
            largest_cont = contamination

        hmap.Fill(mgl, mn1, contamination)


    frame = draw_grid_frame() 
    frame.SetRightMargin(0.15)

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

    for ext in args.extensions.split(','):
        frame.SaveAs(args.output_dir+"/signal_contamination_"+region+'.' + ext)


