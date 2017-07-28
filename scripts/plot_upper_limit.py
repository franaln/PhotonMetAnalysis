#! /usr/bin/env python

import os
import ROOT
import argparse

ROOT.gROOT.SetBatch(1)
ROOT.gSystem.Load('%s/lib/libSusyFitter.so' % os.getenv('HISTFITTER'))
ROOT.gInterpreter.ProcessLine('#include "{0}/src/DrawUtils.h" '.format(os.getenv('HISTFITTER')))
ROOT.gInterpreter.ProcessLine('#include "{0}/src/StatTools.h" '.format(os.getenv('HISTFITTER')))

parser = argparse.ArgumentParser(description='plot independent upper limit')

parser.add_argument('-i', dest='input_file', help='Input file with HypoTest result', required=True)
parser.add_argument('-r', dest='result_name', default='result_mu_SIG', help='Result name')
parser.add_argument('-o', dest='output_name', help='Output name')

args = parser.parse_args()

f1 = ROOT.TFile.Open(args.input_file)

hti_result = f1.Get(args.result_name)

calctype = 0 # toys
npoints = hti_result.ArraySize()

plot = ROOT.RooStats.HypoTestInverterPlot("HTI_Result_Plot", '', hti_result);

c_sig = ROOT.TCanvas()
c_sig.SetLogy(False)

plot.Draw("CLb 2CL")

pave = c_sig.GetPrimitive("TPave")
pave.SetLineColor(0)
pave.SetBorderSize(0)
pave.SetFillColor(0)
c_sig.Update()

c_sig.SaveAs(args.output_name)
