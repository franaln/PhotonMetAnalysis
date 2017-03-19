import sys
import argparse
import ROOT
ROOT.gROOT.SetBatch(1)

from array import array
from rootutils import set_style

input_file  = '~/work/Susy/Run2/XS/SignalUncertaintiesUtils_Mar2017_MG_grid/MG_GGM_CN_bhmix_xs/SignalCalc.root'
output_file = 'xs_GGM_CN_bhmix.pdf'

tree = ROOT.TChain('SignalUncertainties')
tree.Add(input_file)

#CN_fs = [111, 112, 113, 115, 117, 122, 123, 125, 127, 133, 135, 137, 157]
CN_fs = [0, 112, 115, 117, 125, 127, 157]

graphs = []

a_x  = [ array('f', []) for i in CN_fs ]
a_y  = [ array('f', []) for i in CN_fs ]
a_ex = [ array('f', []) for i in CN_fs ]
a_ey = [ array('f', []) for i in CN_fs ]

last_mu = 0

for point in tree:

    
    xs = point.crossSection
    unc = point.Tot_error

    xs_dn = xs - xs*unc
    xs_up = xs + xs*unc

    if last_mu == 0:
        xs_all = xs
        xs_dn_all = xs_dn
        xs_up_all = xs_up
    elif point.mu == last_mu:
        xs_all += xs
        xs_dn_all += xs_dn
        xs_up_all += xs_up
    else:

        xsunc = abs(xs_up_all - xs_all)

        a_x[0].append(mn1)
        a_y[0].append(xs_all)
        a_ex[0].append(0.)
        a_ey[0].append(xsunc)

        xs_all = xs
        xs_dn_all = xs_dn
        xs_up_all = xs_up


    print point.mu, point.finalState, xs, xs_all

    if point.finalState == 111:
        mn1 = point.mass1


    fs = point.finalState
    ey = point.Tot_error * point.crossSection

    if fs == 112:
        a_x[1].append(mn1)
        a_y[1].append(xs)
        a_ex[1].append(0.)
        a_ey[1].append(ey)
    elif fs == 115:
        a_x[2].append(mn1)
        a_y[2].append(xs)
        a_ex[2].append(0.)
        a_ey[2].append(ey)
    elif fs == 117:
        a_x[3].append(mn1)
        a_y[3].append(xs)
        a_ex[3].append(0.)
        a_ey[3].append(ey)
    elif fs == 125:
        a_x[4].append(mn1)
        a_y[4].append(xs)
        a_ex[4].append(0.)
        a_ey[4].append(ey)
    elif fs == 127:
        a_x[5].append(mn1)
        a_y[5].append(xs)
        a_ex[5].append(0.)
        a_ey[5].append(ey)
    elif fs == 157:
        a_x[6].append(mn1)
        a_y[6].append(xs)
        a_ex[6].append(0.)
        a_ey[6].append(ey)

    last_mu = point.mu


print a_x[0], a_y[0]
graphs = [
    ROOT.TGraphErrors(len(a_x[0]), a_x[0], a_y[0], a_ex[0], a_ey[0]),
    ROOT.TGraphErrors(len(a_x[1]), a_x[1], a_y[1], a_ex[1], a_ey[1]),
    ROOT.TGraphErrors(len(a_x[2]), a_x[2], a_y[2], a_ex[2], a_ey[2]),
    ROOT.TGraphErrors(len(a_x[3]), a_x[3], a_y[3], a_ex[3], a_ey[3]),
    ROOT.TGraphErrors(len(a_x[4]), a_x[4], a_y[4], a_ex[4], a_ey[4]),
    ROOT.TGraphErrors(len(a_x[5]), a_x[5], a_y[5], a_ex[5], a_ey[5]),
    ROOT.TGraphErrors(len(a_x[6]), a_x[6], a_y[6], a_ex[6], a_ey[6]),
]


set_style(graphs[0], msize=0.8, lwidth=2, color='gray',   fill=True, alpha=0.5)
set_style(graphs[1], msize=0.8, lwidth=1, color='yellow', fill=True, alpha=0.5)
set_style(graphs[2], msize=0.8, lwidth=1, color='red',    fill=True, alpha=0.5)
set_style(graphs[3], msize=0.8, lwidth=1, color='purple', fill=True, alpha=0.5)
set_style(graphs[4], msize=0.8, lwidth=1, color='green',  fill=True, alpha=0.5)
set_style(graphs[5], msize=0.8, lwidth=1, color='blue',   fill=True, alpha=0.5)
set_style(graphs[6], msize=0.8, lwidth=1, color='orange', fill=True, alpha=0.5)

graphs[0].GetXaxis().SetTitle('m_{#tilde{#chi}^{0}_{1}} [GeV]')
graphs[0].GetYaxis().SetTitle('Cross section [pb]')

    
can = ROOT.TCanvas()
can.SetLogy()
can.SetGridy()

leg = ROOT.TLegend(0.65, 0.5, 0.8, 0.88)
leg.SetBorderSize(0)
leg.SetTextSize(0.025)
leg.SetHeader('#sqrt{s} = 13 TeV')

leg.AddEntry(graphs[0],  'pp #rightarrow #tilde{#chi}#tilde{#chi}', 'lf')
leg.AddEntry(graphs[1],  'pp #rightarrow #tilde{#chi}_{1}^{0} #tilde{#chi}_{2}^{0}', 'lf')
leg.AddEntry(graphs[2],  'pp #rightarrow #tilde{#chi}_{1}^{0} #tilde{#chi}_{1}^{+}', 'lf')
leg.AddEntry(graphs[3],  'pp #rightarrow #tilde{#chi}_{1}^{0} #tilde{#chi}_{1}^{-}', 'lf')
leg.AddEntry(graphs[4],  'pp #rightarrow #tilde{#chi}_{2}^{0} #tilde{#chi}_{1}^{+}', 'lf')
leg.AddEntry(graphs[5],  'pp #rightarrow #tilde{#chi}_{2}^{0} #tilde{#chi}_{1}^{-}', 'lf')
leg.AddEntry(graphs[6],  'pp #rightarrow #tilde{#chi}_{1}^{+} #tilde{#chi}_{1}^{-}', 'lf')

# # g_all.GetXaxis().SetLimits(100, 1900)
# # g_all.GetYaxis().SetRangeUser(5E-9, 50)


graphs[0].Draw("3la")
graphs[1].Draw("3l")
graphs[2].Draw("3l")
graphs[3].Draw("3l")
graphs[4].Draw("3l")
graphs[5].Draw("3l")
graphs[6].Draw("3l")

leg.Draw()
can.SaveAs(output_file)
