#! /usr/bin/env python

import argparse
import ROOT
from miniutils import get_histogram, get_events
import regions as regions_
from rootutils import set_style, set_atlas_style, legend
from drawutils import do_plot_cmp

ROOT.gROOT.SetBatch(1)

parser = argparse.ArgumentParser(description='')

#parser.add_argument('-o', '--output', help='output file name', required=True)

parser.add_argument('-v', '--versions' , required=True)
parser.add_argument('-s', '--samples', required=True)

args = parser.parse_args()

regions  = [
    'CRQ',
    'CRW',
    'CRT',
    
    'SR',
    ]

colors = [
    'grey',
    'blue',
    'pink'
    ]

versions = args.versions.split(',')
samples = args.samples.split(',')

if not samples or not versions:
    parser.print_usage()
    sys.exit(1)



for region_number in ['L', 'H']:

    for sample in samples:

        histograms = []
        for ver in versions:
            histograms.append(ROOT.TH1F('h_v%s' % ver, 'h_v%s' % ver, len(regions), 0, len(regions)))

        for hist in histograms:
            hist.SetBinErrorOption(ROOT.TH1.kPoisson)

        for iregion, region in enumerate(regions):
        
            if sample == 'data' and region == 'SR':
                continue

            sel = getattr(regions_, region+'_'+region_number)
        
        
            histograms[0].GetXaxis().SetBinLabel(iregion+1, region)


            print region
            for idx, ver in enumerate(versions):
                evts = get_events(sample, selection=sel, version=ver)
                print ver, evts
                histograms[idx].SetBinContent(iregion+1, evts.mean)

                set_style(histograms[idx], msize=1, lwidth=2, color=colors[idx])


        # Plot
        c = ROOT.TCanvas()

        cup   = ROOT.TPad("u", "u", 0., 0.305, 0.99, 1)
        cdown = ROOT.TPad("d", "d", 0., 0.01, 0.99, 0.295)

        cup.SetLogy()
        
        cup.SetFillColor(0);
        cup.SetBorderMode(0);
        cup.SetBorderSize(2);
        cup.SetTicks()
        cup.SetTopMargin   ( 0.1 );
        cup.SetRightMargin ( 0.05 );
        cup.SetBottomMargin( 0.0025 );
        cup.SetLeftMargin( 0.10 );
        cup.SetFrameBorderMode(0);
        cup.SetFrameBorderMode(0);
        cup.Draw()

        cdown.SetTickx(1);
        cdown.SetTicky(1);
        cdown.SetTopMargin   ( 0.003 );
        cdown.SetRightMargin ( 0.05 );
        cdown.SetBottomMargin( 0.3 );
        cdown.SetLeftMargin( 0.10 );
        cdown.Draw()
    
        cup.cd()

        # add entries to legend
        legymin = 0.55
        legymax = 0.85
        
        legxmin = 0.55
        legxmax = 0.91

        legend1 = legend(legxmin, legymin, legxmax, legymax)

        for idx, ver in enumerate(versions):
            legend1.AddEntry(histograms[idx], 'v%s' % ver, 'l')

        histograms[0].GetYaxis().SetTitle("Number of events")
        histograms[0].GetYaxis().SetTitleSize(0.05)
        histograms[0].GetYaxis().SetTitleOffset(0.9)
        histograms[0].GetXaxis().SetLabelSize(0.06)
        histograms[0].GetYaxis().SetLabelSize(0.05)

        #histograms[0].SetMaximum(100000)
        #histograms[0].SetMinimum(0.05)
        

        histograms[0].Draw('hist')
        for hist in histograms[1:]:
            hist.Draw('histsame')

        legend1.Draw()

        cup.RedrawAxis()

        # Draw ratio 
        cdown.cd()

        ratios = []

        for hist in histograms[1:]:
            ratio = hist.Clone('ratio')
            ratio.Divide(histograms[0])
            
            for b in xrange(1,ratio.GetNbinsX()+1):
                if histograms[0].GetBinContent(b) == 0 and hist.GetBinContent(b) == 0:
                    ratio.SetBinContent(b, 1)
                    
            ratios.append(ratio.Clone())

        ratios[0].SetTitle('')
        ratios[0].SetStats(0)

        for b in xrange(1,histograms[0].GetNbinsX()+1):
            ratios[0].GetXaxis().SetBinLabel(b ,histograms[0].GetXaxis().GetBinLabel(b))

        for idx, ratio in enumerate(ratios):
            set_style(ratio, msize=1, lwidth=2, color=colors[idx+1])

        # x axis
        ratios[0].GetXaxis().SetLabelSize(0.1)
        ratios[0].GetXaxis().SetTitleSize(0.1)
        ratios[0].GetXaxis().SetTitleOffset(1.)
        ratios[0].GetXaxis().SetLabelOffset(0.03)
        ratios[0].GetXaxis().SetTickLength(0.06)

        # y axis
        ratios[0].GetYaxis().SetTitle('ratio')
        ratios[0].GetYaxis().SetLabelSize(0.1)
        ratios[0].GetYaxis().SetTitleSize(0.1)
        ratios[0].GetYaxis().SetRangeUser(0, 2.2)
        ratios[0].GetYaxis().SetNdivisions(504)
        ratios[0].GetYaxis().SetTitleOffset(0.3)
        ratios[0].GetYaxis().SetLabelOffset(0.01)
        ratios[0].GetYaxis().CenterTitle()
        
        for ratio in ratios:
            ratio.Draw('same')

        firstbin = ratios[0].GetXaxis().GetFirst()
        lastbin  = ratios[0].GetXaxis().GetLast()
        xmax     = ratios[0].GetXaxis().GetBinUpEdge(lastbin)
        xmin     = ratios[0].GetXaxis().GetBinLowEdge(firstbin)
        
        lines = [None, None, None,]
        lines[0] = ROOT.TLine(xmin, 1., xmax, 1.)
        lines[1] = ROOT.TLine(xmin, 0.5,xmax, 0.5)
        lines[2] = ROOT.TLine(xmin, 1.5,xmax, 1.5)
        
        lines[0].SetLineWidth(1)
        lines[0].SetLineStyle(2)
        lines[1].SetLineStyle(3)
        lines[2].SetLineStyle(3)
        
        for line in lines:
            line.Draw()

        c.Print('cmp_'+sample + '_' + region_number + '.pdf')


# # plot some variables in CRQ

# ## MC photonjet
# selection =  'ph_n==1 && ph_pt[0]>145 && el_n+mu_n==0 && jet_n>2' # regions_.CRQ_L.replace('met_et<50', 'met_et<100')

# variables = ['ph_pt', 'jet_n', 'bjet_n', 'met_et', 'ht', 'meff', 'rt4', 'dphi_jetmet',]

# for variable in variables:

#     h_201    = get_histogram('photonjet', variable=variable, selection=selection, version='24', remove_var=True)
#     h_207    = get_histogram('photonjet', variable=variable, selection=selection, version='30', remove_var=True)
#     h_207b   = get_histogram('photonjet', variable=variable, selection=selection+tstcleaning, version='30', remove_var=True)

#     set_style(h_201, color=color_201)
#     set_style(h_207, color=color_207)
#     set_style(h_207b, color=color_207b)

#     histograms = (
#         ('20.1',                h_201), 
#         ('20.7',                h_207), 
#         ('20.7 (TST cleaning)', h_207b), 
#         )

#     do_plot_cmp('cmp_photonjet_201_vs_207_'+variable.replace('[', '').replace(']', ''), variable, histograms)


# ## Data
# selection = 'ph_n==1 && ph_pt[0]>145 && el_n+mu_n==0 && jet_n>2 && met_et<150'

# for variable in variables:

#     h_201    = get_histogram('data', variable=variable, selection=selection, version='24')
#     h_207    = get_histogram('data', variable=variable, selection=selection, version='30')
#     h_207b   = get_histogram('data', variable=variable, selection=selection+tstcleaning, version='30')

#     set_style(h_201, color=color_201)
#     set_style(h_207, color=color_207)
#     set_style(h_207b, color=color_207b)

#     histograms = (
#         ('20.1',                h_201), 
#         ('20.7',                h_207), 
#         ('20.7 (TST cleaning)', h_207b), 
#         )

#     do_plot_cmp('cmp_data_201_vs_207_'+variable.replace('[', '').replace(']', ''), variable, histograms)


