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
parser.add_argument('-l', dest='lumi_fb', type=float, help='Lumi in fb-1')
parser.add_argument('-o', dest='output_name', help='Output name')

args = parser.parse_args()

f1 = ROOT.TFile.Open(args.input_file)

hti_result = f1.Get(args.result_name)

calctype = 0 # toys
npoints = hti_result.ArraySize()
ntoys = hti_result.GetResult(0).GetNullDistribution().GetSize()

# UL plot
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

# UL Table
ul_obs = hti_result.UpperLimit()
ul_xsec = ul_obs / args.lumi_fb

# get the expected upper limit and one scan point up and down to calculate the error on upper limit
ul_exp    = hti_result.GetExpectedUpperLimit(0)
ul_exp_up = hti_result.GetExpectedUpperLimit(1) 
ul_exp_dn = hti_result.GetExpectedUpperLimit(-1)

if ul_exp > ul_exp_up or ul_exp < ul_exp_dn:
    print "ul_exp = ", ul_exp , " ul_exp_up = ", ul_exp_up, " ul_exp_dn = ", ul_exp_dn

ul_exp_err_up = hti_result.GetExpectedUpperLimit(1) - ul_exp
ul_exp_err_dn = ul_exp - hti_result.GetExpectedUpperLimit(-1)


#find the CLB values at indexes above and below observed CLs p-value
clb_up = 0.
clb_dn = 0.
mu_up = 0.
mu_dn = 0.
index_up = 0
index_found = False
for iresult in xrange(npoints):

    xval = hti_result.GetXValue(iresult) 
    yval = hti_result.GetYValue(iresult)

    if xval > ul_obs and not index_found:
        index_up = iresult
        clb_up = hti_result.CLb(iresult)
        mu_up = xval
        if iresult > 0:
            clb_dn = hti_result.CLb(iresult-1)
            mu_dn = hti_result.GetXValue(iresult-1)
            index_found = True



# interpolate (linear) the value of CLB to be exactly above upperlimit p-val
try:
    alpha_clb = (clb_up - clb_dn) / (mu_up - mu_dn)
    beta_clb = clb_up - alpha_clb * mu_up
    # CLB is taken as the point on the CLB curve for the same poi value, as the observed upperlimit
    clb = alpha_clb * ul_obs + beta_clb
except ZeroDivisionError:
    print "WARNING ZeroDivisionError while calculating CLb. Setting CLb=0."
    clb = 0.0


print 'npoints   = %i'   % npoints
print 'ntoys     = %i'   % ntoys
print 'ul_xsec   = %.5f' % ul_xsec
print 'ul_obs    = %.5f' % ul_obs
print 'ul_exp    = %.5f' % ul_exp
print 'ul_exp_dn = %.5f' % ul_exp_dn
print 'ul_exp_up = %.5f' % ul_exp_up
print 'CLb       = %.5f' % clb

with open(args.output_name+'.txt', 'w+') as f:

    f.write('npoints   = %i\n'   % npoints)
    f.write('ntoys     = %i\n'   % ntoys)
    f.write('ul_xsec   = %.5f\n' % ul_xsec)
    f.write('ul_obs    = %.5f\n' % ul_obs)
    f.write('ul_exp    = %.5f\n' % ul_exp)
    f.write('ul_exp_dn = %.5f\n' % ul_exp_dn)
    f.write('ul_exp_up = %.5f\n' % ul_exp_up)
    f.write('CLb       = %.5f\n' % clb)

