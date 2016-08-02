#! /usr/bin/env python2.7

import math
import argparse

import ROOT

GEV = 1000.

def create_object_arrow(pt, phi, color):
    # rescale pt
    pt_scaled = pt * pt_scale

    # calc x and y
    x = 0.5 + pt_scaled * math.cos(phi)
    y = 0.5 + pt_scaled * math.sin(phi)

    # create arrow
    arrow = ROOT.TArrow(0.5, 0.5, x, y, 0.02, '|>')
    arrow.SetLineWidth(2)
    arrow.SetLineColor(color)
    arrow.SetFillColor(color)

    return arrow


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
    canvas = ROOT.TCanvas('c1')
    canvas.Range(0, 0, 1, 1)

    # scale pt
    global pt_scale
    
    all_pt = [ evt.ph_pt[i] for i in xrange(evt.ph_n) ]
    all_pt += [ evt.el_pt[i] for i in xrange(evt.el_n) ]
    all_pt += [ evt.mu_pt[i] for i in xrange(evt.mu_n) ]
    all_pt += [ evt.jet_pt[i] for i in xrange(evt.jet_n) ]

    ptmax = max(*all_pt) * 0.9
    pt_scale = 0.5/ptmax 

    # draw axis
    lx = ROOT.TLine(0.5, 0, 0.5, 1)
    lx.SetLineColor(ROOT.kGray+2)
    lx.Draw()

    ly = ROOT.TLine(0, 0.5, 1, 0.5)
    ly.SetLineColor(ROOT.kGray+2)
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
        elotons.append(el)

    for i in xrange(evt.mu_n):
        mu = create_object_arrow(evt.mu_pt[i], evt.mu_phi[i], ROOT.kGray+3)
        muotons.append(mu)

    for i in xrange(evt.jet_n):
        jet = create_object_arrow(evt.jet_pt[i], evt.jet_phi[i], ROOT.kGreen-3)
        jets.append(jet)

    met  = create_object_arrow(evt.met_et, evt.met_phi, ROOT.kRed-4)
    met.SetLineStyle(2)

    for ph in photons:
        ph.Draw()

    for mu in muons:
        mu.Draw()

    for el in electrons:
        el.Draw()

    for jet in jets:
        jet.Draw()

    met.Draw()

    label1 = ROOT.TLatex(0.90, 0.17, 'photons')
    label1.SetTextSize(0.038)
    label1.SetTextColor(ROOT.kAzure-7)
    label1.Draw()

    label2 = ROOT.TLatex(0.90, 0.12, 'jets')
    label2.SetTextSize(0.038)
    label2.SetTextColor(ROOT.kGreen-3)
    label2.Draw()

    label3 = ROOT.TLatex(0.90, 0.07, 'e/#mu')
    label3.SetTextSize(0.038)
    label3.SetTextColor(ROOT.kGray+3)
    label3.Draw()

    label4 = ROOT.TLatex(0.90, 0.02, 'E_{T}^{miss}')
    label4.SetTextSize(0.038)
    label4.SetTextColor(ROOT.kRed-4)
    label4.Draw()

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
