import sys
import argparse
import ROOT
ROOT.gROOT.SetBatch(1)

from drawutils import *
from rootutils import *

input_file  = '~/work/Susy/Run2/XS/SignalUncertaintiesUtils_Mar2017_MG_grid/MG_GGM_GG_bhmix_xs/SignalCalc.root'
output_file = 'xs_GGM_GG_bhmix.pdf'

tree = ROOT.TChain('SignalUncertainties')
tree.Add(input_file)

a_x = array('f', [])
a_y = array('f', [])
a_ex = array('f', [])
a_ey = array('f', [])

for point in tree:
    
    if point.mu != 150:
        continue

    a_x.append(point.mass1)
    a_y.append(point.crossSection)

    ey = point.Tot_error * point.crossSection

    a_ex.append(0.)
    a_ey.append(ey)


g = ROOT.TGraphErrors(len(a_x), a_x, a_y, a_ex, a_ey)
g_unc = g.Clone()
    
g.GetXaxis().SetTitle('m_{#tilde{g}} [GeV]')
g.GetYaxis().SetTitle('Cross section [pb]')

#g.GetXaxis().SetLimits(100, 1900)
g.GetYaxis().SetRangeUser(1E-5, 0.2)

set_style(g, lwidth=2, color='red', fill=True, alpha=0.5)
set_style(g_unc, lwidth=0, color='red', fill=True, alpha=0.5)


can = ROOT.TCanvas()
can.SetLogy()
can.SetGridy()

leg = ROOT.TLegend(0.60, 0.65, 0.88, 0.88)
leg.SetBorderSize(0)
leg.SetTextSize(0.025)
leg.SetHeader('#sqrt{s} = 13 TeV')
leg.AddEntry(g, '#sigma (pp #rightarrow #tilde{g}#tilde{g}) ', 'l')
leg.AddEntry(g_unc, '#alpha_{s} + scale + PDF ', 'f')

g.Draw("3 c a")
leg.Draw()

can.SaveAs(output_file)
