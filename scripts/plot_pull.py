#! /usr/bin/env python
# single photon analysis

import os
import sys
import argparse
import ROOT
from array import array
from rootutils import set_atlas_style
from systable import systdict_root

ROOT.gROOT.SetBatch(True)

ROOT.gSystem.Load('%s/lib/libSusyFitter.so' % os.getenv('HISTFITTER'))
ROOT.gInterpreter.ProcessLine('#include "{0}/src/Utils.h" '.format(os.getenv('HISTFITTER')))
ROOT.gROOT.Reset()

parser = argparse.ArgumentParser(description='')
parser.add_argument('-w', dest='workspace_file', required=True, help='Workspace file')
parser.add_argument('-o', dest='output_dir', required=True, help='output directory')

args = parser.parse_args()

wfile = args.workspace_file

w = ROOT.Util.GetWorkspaceFromFile(wfile, 'w') #orkspacename)

result = w.obj('RooExpandedFitResult_afterFit')


np_list = result.floatParsFinal()
np_size = np_list.getSize()

y = array('d')
y_dn = array('d')
y_up = array('d')

names = []
x = array('d')
xe = array('d')

counter = 0
for i in xrange(np_size):

    np = np_list[i]

    name = np.GetName()
    
    if name.startswith('gamma_stat') or name.startswith('mu_'):
        continue

    names.append(systdict_root[name])
    
    val = np.getVal()
    val_up = np.getErrorHi()
    val_dn = np.getErrorLo() 

    print val_dn, val_up

    x.append(counter)
    xe.append(0)

    y.append(val)
    y_dn.append(abs(val_dn))
    y_up.append(val_up)

    counter += 1



# plot
set_atlas_style()

c = ROOT.TCanvas('pulls', '', 1200, 500)
c.SetBottomMargin(0.32)
c.SetTopMargin(0.03)
c.SetRightMargin(0.02)
c.SetLeftMargin(0.06)

frame = ROOT.TH2D('frame_', '', len(y), -0.5, len(y)-0.5, 5, -1.2, 1.2)
frame.SetYTitle('Uncertainty After Fit')
frame.SetXTitle('')
frame.Draw()
frame.GetYaxis().SetTitleOffset(0.5)

eg = ROOT.TGraphAsymmErrors(len(x), x, y, xe, xe, y_dn, y_up)
eg.SetMarkerStyle(20)
eg.Draw('sameP')

pone = ROOT.TLine(-0.5, 1, len(x)-0.5, 1)
pone.SetLineStyle(3)
pone.Draw('same')
zero = ROOT.TLine(-0.5, 0, len(x)-0.5, 0)
zero.SetLineStyle(2)
zero.Draw('same')
mone = ROOT.TLine(-0.5, -1, len(x)-0.5, -1)
mone.SetLineStyle(3)
mone.Draw('same')

for abin in xrange(len(x)):
    frame.GetXaxis().SetBinLabel(abin+1 , names[abin])

frame.GetXaxis().LabelsOption('v')
frame.GetXaxis().SetLabelSize(0.03)

c2 = ROOT.TCanvas("Nuisance parameters zoom", "Nuisance parameters zoom", 1200, 500)
c2.cd()
frame2 = frame.Clone()
frame2.GetXaxis().SetLabelSize(0.02)
frame2.GetYaxis().SetRangeUser(-0.05, 0.05)
frame2.Draw()
graph2 = eg.Clone()
graph2.SetMarkerStyle(20)
graph2.SetMarkerSize(1.3)
graph2.Draw("samePx")
zero.Draw('same')

c.SaveAs('%s/syst_pull_afterFit.pdf' % args.output_dir)
c2.SaveAs('%s/syst_pull_zoom_afterFit.pdf' % args.output_dir)
