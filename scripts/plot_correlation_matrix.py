import os
from array import array
import argparse

import ROOT
ROOT.gROOT.SetBatch(1)

ROOT.gSystem.Load('%s/lib/libSusyFitter.so' % os.getenv('HISTFITTER'))
ROOT.gInterpreter.ProcessLine('#include "{0}/src/Utils.h" '.format(os.getenv('HISTFITTER')))
ROOT.gROOT.Reset()

from rootutils import set_style, set_atlas_style
from systable import systdict_root as systdict

parser = argparse.ArgumentParser(description='')
parser.add_argument('-w', dest='workspace_file', required=True, help='Workspace file')
parser.add_argument('-o', dest='output', required=True, help='Output file')

args = parser.parse_args()

filename = args.workspace_file

workspacename = 'w'

w = ROOT.Util.GetWorkspaceFromFile(filename, workspacename)

r_fit = w.genobj("RooExpandedFitResult_afterFit")

#h_corr = ROOT.Util.PlotCorrelationMatrix(r_fit, 'PhotonMetAnalysis', True)

num_pars = r_fit.floatParsFinal().getSize()

h_corr = r_fit.correlationHist("h_corr")

# Cleanup corrMattrix from rows and columns with content less then corrThres
rm_idx = []
corr_thresh = [0.01,0.1,0.2] 
nbins = h_corr.GetNbinsX();
index_x = 0
index_y = 0
fill_hist_y = False
fill_hist_x = False

# Look for rows and columns indices to remove
for ix in xrange(1, nbins+1):
    thresh_counter = 0

    for iy in xrange(1, nbins+1):
        if ix ==((nbins+1)-iy):
            continue

        if (abs(h_corr.GetBinContent(ix,iy)) >= corr_thresh[1]):
            thresh_counter += 1
    
    if thresh_counter == 0:
        rm_idx.append(ix)
      

nrm_idx = len(rm_idx)
new_size = num_pars-nrm_idx

h_corr_reduced = ROOT.TH2D("h_corr_reduced","h_corr_reduced",new_size,0,new_size,new_size,0,new_size);

# Copy original matrix to the new without empty rows and columns
for ix in xrange(1, nbins+1):
    index_y = 0
    fill_hist_x = False
    for iy in xrange(1, nbins+1):
        fill_hist_y = True
        for irm in xrange(nrm_idx):
            if ( ix == rm_idx[irm] or iy == ((nbins+1)-rm_idx[irm]) ):
                fill_hist_y = False
          
        if fill_hist_y:
            cont = h_corr.GetBinContent(ix,iy)
            h_corr_reduced.Fill(index_x, index_y, round(cont, 2))
            index_y += 1
            if index_x==0:
                label = h_corr.GetYaxis().GetBinLabel(iy)

                if label.startswith('gamma'):
                    label = 'MC stat.'
            
                if label in systdict and systdict[label]:
                    label = systdict[label]

                h_corr_reduced.GetYaxis().SetBinLabel(index_y, label)
            fill_hist_x = True
          
        
    if fill_hist_x:
        index_x += 1
        label = h_corr.GetXaxis().GetBinLabel(ix)
        if label.startswith('gamma'):
            label = 'MC stat.'
        if label in systdict and systdict[label]:
            label = systdict[label]
        h_corr_reduced.GetXaxis().SetBinLabel(index_x, label)
        
      
h_corr = h_corr_reduced
num_pars = new_size;


# Plot
canName = "c_corrMatrix_%s" %  r_fit.GetName()
c_corr = ROOT.TCanvas(canName,canName,600,600)

c_corr.SetLeftMargin(0.18)
c_corr.SetRightMargin(0.13)
c_corr.SetBottomMargin(0.18)

set_atlas_style()

s = array('d', [0.00, 0.25, 0.50, 0.75, 1.00])

# r = array('d', [ 20./255, 112./255, 204./255, 112./255,  20./255])
# g = array('d', [ 79./255, 142./255, 204./255, 142./255,  79./255])
# b = array('d', [235./255, 168./255, 102./255, 168./255, 235./255])

r = array('d', [ 20./255, 100./255, 179./255, 100./255,  20./255])
g = array('d', [ 79./255, 148./255, 217./255, 148./255,  79./255])
b = array('d', [235./255, 187./255, 140./255, 187./255, 235./255])

ROOT.TColor.CreateGradientColorTable(len(s), s, r, g, b, 999)
ROOT.gStyle.SetNumberContours(999)

h_corr.SetMarkerSize(1.45)
h_corr.SetMarkerColor(ROOT.kWhite)
ROOT.gStyle.SetPaintTextFormat("4.2f")

if(num_pars<5):
    h_corr.SetMarkerSize(1.4);
elif(num_pars<10):
    h_corr.SetMarkerSize(1.1);
elif(num_pars<20):
    h_corr.SetMarkerSize(0.85);
elif(num_pars<40):
    h_corr.SetMarkerSize(0.5);
else:
    h_corr.SetMarkerSize(0.25);

if   num_pars<5:    labelSize = 0.05
elif num_pars<10:   labelSize = 0.04
elif num_pars<20:   labelSize = 0.028
elif num_pars<40:   labelSize = 0.02
else:               labelSize = 0.015

h_corr.GetXaxis().SetLabelSize(labelSize)
h_corr.GetYaxis().SetLabelSize(labelSize)
h_corr.GetXaxis().LabelsOption("v")

h_corr.SetContour(999)
h_corr.GetZaxis().SetRangeUser(-1, 1)
h_corr.GetZaxis().SetLabelSize(labelSize)
h_corr.GetZaxis().SetLabelOffset(0.01)

set_style(h_corr)

h_corr.Draw("colz");
h_corr.Draw("textsame");

c_corr.SaveAs(args.output)

