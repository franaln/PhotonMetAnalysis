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
parser.add_argument('-i', dest='input_file', required=True, help='Input file (with workspace or fit)')
parser.add_argument('-w', dest='workspace_name', default='w', help='Workspace name')
parser.add_argument('-f', dest='fit_name', help='Fit name')
parser.add_argument('-o', dest='output_file', required=True, help='Output file')

args = parser.parse_args()

if args.fit_name is not None:
    infile = ROOT.TFile.Open(args.input_file)
    
    result = infile.Get(args.fit_name)
else:

    w = ROOT.Util.GetWorkspaceFromFile(args.input_file, args.workspace_name) 

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
counter_gamma = -1
for i in xrange(np_size):

    np = np_list[i]

    name = np.GetName()
    
    if 'VR' in name or 'CR' in name:
        continue

    val = np.getVal()
    val_up = np.getErrorHi()
    val_dn = np.getErrorLo() 

    if name.startswith('gamma_') or name.startswith('mu_'):
        val -= 1.

        if counter_gamma < 0:
            counter_gamma = counter

    if name in systdict_root:
        names.append(systdict_root[name])
    elif name.startswith('gamma_shape'):
        name = name.replace('_obs_cuts_bin_0', '').replace('gamma_shape_', '')

        _, _, sample, region = name.split('_')
        if sample == 'efake':
            sample = 'e#rightarrow#gamma fakes'
        elif sample == 'jfake':
            sample = 'j#rightarrow#gamma fakes'

        #names.append('%s stat. (%s)' % (sample, region))
        names.append('%s stat.' % (sample))

    elif name.startswith('gamma_stat'):
        name = name.replace('_cuts_bin_0', '').replace('gamma_stat_', '')
        names.append('MC stat. (%s)' % name)
        #names.append('MC stat.')
    else:
        names.append(name)

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
c.SetRightMargin(0.06)
c.SetLeftMargin(0.06)

frame = ROOT.TH2D('frame_', '', len(y), -0.5, len(y)-0.5, 5, -1.5, 1.5)
frame.SetYTitle('#alpha parameters after fit')
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

# Draw an axis on the right side
axis = ROOT.TGaxis(len(y)-0.5, -1.5, len(y)-0.5, 1.5, -0.5, 2.5, 510, "+L")
axis.SetLabelFont(42)
axis.SetTitleFont(42)
axis.SetTitle('#gamma/#mu parameters after fit')
axis.SetTitleOffset(0.7)
axis.Draw()
frame.GetYaxis().SetLabelSize(axis.GetLabelSize())


pg = ROOT.TLine(counter_gamma-0.5, -1.5, counter_gamma-0.5, 1.5)
pg.SetLineStyle(3)
pg.Draw('same')

c.SaveAs(args.output_file)
