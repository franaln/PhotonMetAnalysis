#! /usr/bin/env python2.7

import math
import argparse
from array import array

import ROOT

GEV = 1000.

def create_object_arrow(pt, phi, color, arrow='|>'):
    # rescale pt
    pt_scaled = pt * pt_scale

    # calc x and y
    x = 0.5 + pt_scaled * math.cos(phi)
    y = 0.5 + pt_scaled * math.sin(phi)

    # create arrow
    arrow = ROOT.TArrow(0.5, 0.5, x, y, 0.02, arrow)
    arrow.SetLineWidth(2)
    arrow.SetLineColor(color)
    arrow.SetFillColor(color)

    return arrow

def create_jet_cone(pt, phi, color):

    # rescale pt
    pt_scaled = pt * pt_scale

    # calc x and y
    x1 = 0.5 + pt_scaled * math.cos(phi-0.2)
    y1 = 0.5 + pt_scaled * math.sin(phi-0.2)

    x2 = 0.5 + pt_scaled * math.cos(phi+0.2)
    y2 = 0.5 + pt_scaled * math.sin(phi+0.2)

    x = array('f', [0.5, x1, x2, 0.5])
    y = array('f', [0.5, y1, y2, 0.5])

    pline = ROOT.TPolyLine(4, x, y)
    pline.SetLineWidth(2)
    pline.SetLineColor(color)
    pline.SetFillColorAlpha(color, 0.7)

    return pline

def draw_event(evt, figname):

    # variables
    # ph_pt = ntuple.ph_pt
    # ph_phi = ntuple.ph_phi

    # jet1_pt = ntuple.jet1_pt
    # jet1_phi = ntuple.jet1_phi

    # jet2_pt = ntuple.jet2_pt
    # jet2_phi = ntuple.jet2_phi

    # met_et = ntuple.met_et
    # met_phi = ntuple.met_phi

    # canvas
    canvas = ROOT.TCanvas('c1', 'c1', 600, 600)
    canvas.Range(0, 0, 1, 1)

    box1 = ROOT.TLine(0, 0, 1, 0)
    box2 = ROOT.TLine(0, 1, 1, 1)
    box3 = ROOT.TLine(0, 0, 0, 1)
    box4 = ROOT.TLine(1, 0, 1, 1)
    box1.SetLineColor(ROOT.kGray+1)
    box2.SetLineColor(ROOT.kGray+1)
    box3.SetLineColor(ROOT.kGray+1)
    box4.SetLineColor(ROOT.kGray+1)
    box1.SetLineWidth(2)
    box2.SetLineWidth(2)
    box3.SetLineWidth(2)
    box4.SetLineWidth(2)
    box1.Draw()
    box2.Draw()
    box3.Draw()
    box4.Draw()

    # scale pt
    global pt_scale
    
    all_pt  = [ evt.ph_pt[i] for i in xrange(evt.ph_n) ]
    all_pt += [ evt.el_pt[i] for i in xrange(evt.el_n) ]
    all_pt += [ evt.mu_pt[i] for i in xrange(evt.mu_n) ]
    all_pt += [ evt.jet_pt[i] for i in xrange(evt.jet_n) ]

    ptmax = max(*all_pt) 
    pt_scale = 0.5/ptmax 

    # scale
    l_scale = ROOT.TLine(0.01, 0.02, 0.06, 0.02)
    l_scale.Draw()

    l1_scale = ROOT.TLine(0.01, 0.017, 0.01, 0.023)
    l2_scale = ROOT.TLine(0.06, 0.017, 0.06, 0.023)
    l1_scale.Draw()
    l2_scale.Draw()

    t_scale = ROOT.TLatex(0.08, 0.012, '%.2f GeV' % (ptmax/10.))
    t_scale.SetTextSize(0.02)
    t_scale.Draw()

    # draw axis
    lx = ROOT.TLine(0.5, 0, 0.5, 1)
    lx.SetLineColor(ROOT.kGray+1)
    lx.Draw()

    ly = ROOT.TLine(0, 0.5, 1, 0.5)
    ly.SetLineColor(ROOT.kGray+1)
    ly.Draw()

    # draw arrows
    photons = []
    electrons = []
    muons = []
    jets = []
    for i in xrange(evt.ph_n):
        ph = create_object_arrow(evt.ph_pt[i], evt.ph_phi[i], ROOT.kAzure-7)
        photons.append(ph)
    
    for i in xrange(evt.el_n):
        el = create_object_arrow(evt.el_pt[i], evt.el_phi[i], ROOT.kGray+3)
        electrons.append(el)

    for i in xrange(evt.mu_n):
        mu = create_object_arrow(evt.mu_pt[i], evt.mu_phi[i], ROOT.kGray+3)
        muons.append(mu)

    for i in xrange(evt.jet_n):
        jet = create_jet_cone(evt.jet_pt[i], evt.jet_phi[i], ROOT.kGreen-3)
        jets.append(jet)

    met  = create_object_arrow(evt.met_et, evt.met_phi, ROOT.kRed-4, arrow='')
    met.SetLineStyle(2)


    for jet in jets:
        jet.Draw('f')
        jet.Draw()

    for mu in muons:
        mu.Draw()

    for el in electrons:
        el.Draw()

    for ph in photons:
        ph.Draw()

    met.Draw()

    label1 = ROOT.TLatex(0.90, 0.95, 'photons')
    label1.SetTextSize(0.02)
    label1.SetTextColor(ROOT.kAzure-7)
    label1.Draw()

    label2 = ROOT.TLatex(0.90, 0.92, 'jets')
    label2.SetTextSize(0.02)
    label2.SetTextColor(ROOT.kGreen-3)
    label2.Draw()

    label3 = ROOT.TLatex(0.90, 0.89, 'e/#mu')
    label3.SetTextSize(0.02)
    label3.SetTextColor(ROOT.kGray+3)
    label3.Draw()

    label4 = ROOT.TLatex(0.90, 0.86, 'E_{T}^{miss}')
    label4.SetTextSize(0.02)
    label4.SetTextColor(ROOT.kRed-4)
    label4.Draw()

    # Event info
    ei_1 = ROOT.TLatex(0.7, 0.012, 'Run %i, Event %i' % (evt.run, evt.event))
    ei_1.SetTextSize(0.02)
    ei_1.Draw()

    # if photons:
    #     ei_2 = ROOT.TLatex(0.66, 0.08, '%i photons, p_{T} = %.2f GeV' % (evt.ph_n, evt.ph_pt[0]))
    #     ei_2.SetTextSize(0.015)
    #     ei_2.Draw()

    # # if electrons or muons:
    # #     ei_3 = ROOT.TLatex(0.66, 0.05, '%i leptons, p_{T} = %.2f GeV' % (evt.el_n+evt.mu_n, evt.mu_pt[0]))
    # #     ei_3.SetTextSize(0.015)
    # #     ei_3.Draw()

    # if jets:
    #     ei_4 = ROOT.TLatex(0.66, 0.06, '%i jets, p_{T} = %.2f GeV' % (evt.jet_n, evt.jet_pt[0]))
    #     ei_4.SetTextSize(0.015)
    #     ei_4.Draw()

    # ei_5 = ROOT.TLatex(0.66, 0.04, 'MET = %.2f GeV, HT = %.2f GeV' % (evt.met_et, evt.ht))
    # ei_5.SetTextSize(0.015)
    # ei_5.Draw()

    canvas.Print(figname)



def main():

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-i', '--input', help='input file', required=True)
    parser.add_argument('-o', '--output', help='output name', required=True)

    parser.add_argument('-s', dest='selection', help='selection')

    args = parser.parse_args()


    ROOT.gROOT.SetBatch(1)
    
    chain = ROOT.TChain('mini')
    chain.Add(args.input)

    selection = args.selection

    ROOT.gDirectory.Delete('list*')
    chain.SetEntryList(0)

    total_events = chain.GetEntries()
    chain.Draw('>>list', selection, 'entrylist')
    entry_list = ROOT.gDirectory.Get('list')

    chain.SetEntryList(entry_list)
    selected_events = entry_list.GetN()

    if selected_events <= 0:
        print 'No events passing this selection... '
        return

    for event in xrange(selected_events):

        n = entry_list.Next()
        chain.GetEntry(n)

        draw_event(chain, '%s_%i.pdf' % (args.output, event))


if __name__ == '__main__':
    main()
