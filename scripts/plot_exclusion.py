#! /usr/bin/env python2.7

import os
import sys
import math
import argparse
import subprocess
from array import array
from functools import partial

import ROOT

import style
import miniutils
import regions
from utils import mkdirp
from rootutils import set_default_style, set_atlas_style, get_color
from drawutils import draw_grid_frame
from signalgrid import grid_m3_mu

ROOT.gROOT.SetBatch(1)
ROOT.gSystem.Load('%s/lib/libSusyFitter.so' % os.getenv('HISTFITTER'))
ROOT.gInterpreter.ProcessLine('#include "{0}/src/DrawUtils.h" '.format(os.getenv('HISTFITTER')))
ROOT.gInterpreter.ProcessLine('#include "{0}/src/StatTools.h" '.format(os.getenv('HISTFITTER')))

def mirror_borders(histo):

    hist = histo.Clone()
    numx = hist.GetNbinsX()
    numy = hist.GetNbinsY()

    val = 0
    # corner points
    hist.SetBinContent(0,0,hist.GetBinContent(1,1))
    hist.SetBinContent(numx+1,numy+1,hist.GetBinContent(numx,numy))
    hist.SetBinContent(numx+1,0,hist.GetBinContent(numx,1))
    hist.SetBinContent(0,numy+1,hist.GetBinContent(1,numy))

    for i in xrange(1, numx+1):
        hist.SetBinContent(i,0,    hist.GetBinContent(i,1))
        hist.SetBinContent(i,numy+1, hist.GetBinContent(i,numy))

    for i in xrange(1, numy+1):
        hist.SetBinContent(0,i,      hist.GetBinContent(1,i))
        hist.SetBinContent(numx+1,i, hist.GetBinContent(numx,i))

    return hist

def add_borders(histo, name, title):

    hist = histo.Clone()
    nbinsx = hist.GetNbinsX()
    nbinsy = hist.GetNbinsY()

    xbinwidth = (hist.GetXaxis().GetBinCenter(nbinsx) - hist.GetXaxis().GetBinCenter(1)) / float(nbinsx-1)
    ybinwidth = (hist.GetYaxis().GetBinCenter(nbinsy) - hist.GetYaxis().GetBinCenter(1)) / float(nbinsy-1)

    xmin = hist.GetXaxis().GetBinCenter(0) - xbinwidth/2.
    xmax = hist.GetXaxis().GetBinCenter(nbinsx+1) + xbinwidth/2.
    ymin = hist.GetYaxis().GetBinCenter(0) - ybinwidth/2.
    ymax = hist.GetYaxis().GetBinCenter(nbinsy+1) + ybinwidth/2.

    hist2 = ROOT.TH2F(name, title, nbinsx+2, xmin, xmax, nbinsy+2, ymin, ymax)

    for ibin1 in xrange(hist.GetNbinsX()+2):
        for ibin2 in xrange(hist.GetNbinsY()+2):
            hist2.SetBinContent(ibin1+1, ibin2+1, hist.GetBinContent(ibin1,ibin2))

    return hist2

def set_borders(histo, val):

    hist = histo.Clone()
    numx = hist.GetNbinsX()
    numy = hist.GetNbinsY()

    for i in xrange(numx+2):
        hist.SetBinContent(i,0,val)
        hist.SetBinContent(i,numy+1,val)

    for i in xrange(numy+2):
        hist.SetBinContent(0,i,val)
        hist.SetBinContent(numx+1,i,val)

    histCopy = hist.Clone()
    return histCopy


def fix_and_set_borders(hist, name, title, val):

    hist0 = hist.Clone()

    hist0c = mirror_borders(hist0).Clone()    # mirror values of border bins into overflow bins

    hist1 = add_borders(hist0c, "hist1", "hist1").Clone()
    # add new border of bins around original histogram,
    # ... so 'overflow' bins become normal bins
    hist1c = set_borders(hist1, val).Clone()
    # set overflow bins to value 1

    histX = add_borders(hist1c, "histX", "histX").Clone()
    # add new border of bins around original histogram,
    # ... so 'overflow' bins become normal bins

    hist3 = histX.Clone()
    hist3.SetName(name)
    hist3.SetTitle(name)

    return hist3 # this can be used for filled contour histograms


def get_hist(file_name, hist_name):

    file_ = ROOT.TFile(file_name)
    hist = file_.Get(hist_name).Clone()
    hist.SetName(hist_name)
    hist.SetTitle(hist_name)
    hist.SetDirectory(0)

    file_.Close()

    return hist


def return_contour95(histo_name, file_name):

    file_ = ROOT.TFile(file_name)
    histo = file_.Get(histo_name)

    histo.SetName(histo_name)
    histo.SetTitle(histo_name)

    histo = fix_and_set_borders(histo, histo_name, histo_name, 0).Clone()

    histo.SetDirectory(0)
    ROOT.SetOwnership(histo, False)

    histo.SetContour(1)
    histo.SetContourLevel(0, ROOT.TMath.NormQuantile(1-0.05))
    histo.SetLineWidth(2)
    histo.SetLineStyle(1)

    return histo


def convert_hist_to_graph(hist):

    canvas = ROOT.TCanvas()
    hist.Draw("CONT List")
    canvas.Update()
    contours = ROOT.TObjArray(ROOT.gROOT.GetListOfSpecials().FindObject("contours"))

    lcontour1 = contours.At(0)
    graph = lcontour1.First()

    graph.SetLineColor(hist.GetLineColor())
    graph.SetLineWidth(hist.GetLineWidth())
    graph.SetLineStyle(hist.GetLineStyle())

    return graph.Clone()



def plot_exclusion(path, region, outdir):

    #set_default_style()
    set_atlas_style()

    ROOT.gStyle.SetLegendFont(42)

    # input files
    if sig_xs_syst:
        file_name      = path + '/Output_fixSigXSecNominal_hypotest__1_harvest_list.root'
        file_name_high = path + '/Output_fixSigXSecUp_hypotest__1_harvest_list.root'
        file_name_low  = path + '/Output_fixSigXSecDown_hypotest__1_harvest_list.root'
    else:
        file_name      = path + '/Output_hypotest__1_harvest_list.root'

    # Get histograms
    ## obs CLs (Nominal, Low, High)
    sigp1clsf = return_contour95('sigp1clsf', file_name)
    if sig_xs_syst:
        sigp1clsfLow  = return_contour95('sigp1clsf', file_name_low)
        sigp1clsfHigh = return_contour95('sigp1clsf', file_name_high)

        sigp1clsfLow.SetName('sigp1clsfLow')
        sigp1clsfLow.SetTitle('sigp1clsfLow')

        sigp1clsfHigh.SetName('sigp1clsfHigh')
        sigp1clsfHigh.SetTitle('sigp1clsfHigh')

    sigp1expclsf  = return_contour95('sigp1expclsf', file_name)
    sigclsu1s     = return_contour95('sigclsu1s',    file_name)
    sigclsd1s     = return_contour95('sigclsd1s',    file_name)

    graph_sigp1clsf = convert_hist_to_graph(sigp1clsf)
    if sig_xs_syst:
        graph_sigp1clsfLow  = convert_hist_to_graph(sigp1clsfLow)
        graph_sigp1clsfHigh = convert_hist_to_graph(sigp1clsfHigh)

    graph_sigp1expclsf = convert_hist_to_graph(sigp1expclsf)
    graph_sigclsu1s = convert_hist_to_graph(sigclsu1s)
    graph_sigclsd1s = convert_hist_to_graph(sigclsd1s)

    # Colours
    c_yellow = ROOT.TColor.GetColor('#ffe938')
    c_red    = ROOT.TColor.GetColor('#aa0000')
    c_blue   = ROOT.TColor.GetColor('#28373c')


    frame = draw_grid_frame(xmin=1146, xmax=2550, ymin=147, ymax=2550) 

    # Create the text in the plot
    # DATA info
    leg1 = ROOT.TLatex()
    leg1.SetNDC()
    leg1.SetTextSize(0.035)
    leg1.SetTextColor(1)
    if args.datalabel is not None:
        leg1.DrawLatex(0.15, 0.7, args.datalabel)
    else:
        leg1.DrawLatex(0.15, 0.7, style.data_label)

    # if style.atlas_label:
    #     leg1.SetTextSize(0.04)
    #     leg1.DrawLatex(1810, 230, style.atlas_label)

    # Signal Regions label
    leg3 = ROOT.TLatex()
    leg3.SetNDC()
    leg3.SetTextSize(0.035)
    leg3.SetTextColor(1)
    leg3.SetTextFont(42)

    region_text = region
    if 'SRL,SRH' in region_text or 'SRiL,SRiH' in region_text:
        region_text = region_text = 'SR_{L} and SR_{H}'
    elif 'SRL' in region_text or 'SRiL' in region_text:
        region_text = 'SR_{L}'
    elif 'SRH' in region_text or 'SRiH' in region_text:
        region_text = 'SR_{H}'

    leg3.DrawLatex(0.15, 0.63, region_text)

    # Legend
    leg  = ROOT.TLegend(0.15, 0.77, 0.49, 0.92)
    leg.SetFillColor(0)
    leg.SetBorderSize(0)

    # extra text
    leg4 = ROOT.TLatex()
    leg4.SetNDC()
    leg4.SetTextSize(0.03)
    leg4.SetTextColor(1)
    leg4.SetTextAngle(90)

    if (args.obscls or args.expcls or args.bestsr):

        leg4.SetTextColor(ROOT.kGray+2)

        textx = 0.98
        texty = 0.12

        if args.obscls:
            leg4.DrawLatex(textx, texty, 'Numbers give observed CL_{s} values')
        elif args.expcls:
            leg4.DrawLatex(textx, texty, 'Numbers give expected CL_{s} values')
        elif args.bestsr:
            leg4.DrawLatex(textx, texty, 'Labels indicate best-expected SR')

    # leg2 = ROOT.TLatex()
    # leg2.SetNDC()
    # leg2.SetTextSize(0.03)
    # leg2.SetTextColor(1)
    # leg2.DrawLatex(0.17, 0.75, "All limits at 95% CL")

    graph_sigp1clsf.SetFillColor(ROOT.kWhite)
    graph_sigp1clsf.SetFillStyle(3003)
    graph_sigp1clsf.SetLineColor(c_red)
    graph_sigp1clsf.SetLineStyle(1)
    graph_sigp1clsf.SetLineWidth(3)

    if sig_xs_syst:
        graph_sigp1clsfHigh.SetFillColor(ROOT.kWhite)
        graph_sigp1clsfHigh.SetFillStyle(3003)
        graph_sigp1clsfHigh.SetLineColor(c_red)
        graph_sigp1clsfHigh.SetLineStyle(3)
        graph_sigp1clsfHigh.SetLineWidth(2)
        
        graph_sigp1clsfLow.SetFillColor(ROOT.kWhite)
        graph_sigp1clsfLow.SetFillStyle(3003)
        graph_sigp1clsfLow.SetLineColor(c_red)
        graph_sigp1clsfLow.SetLineStyle(3)
        graph_sigp1clsfLow.SetLineWidth(2)

    sigp1expclsf.SetLineColor(c_blue)
    sigp1expclsf.SetLineStyle(1)
    sigp1expclsf.SetLineWidth(2)

    sigp1clsf.SetLineWidth(3)
    sigclsu1s.SetFillColor(ROOT.kWhite)
    sigclsd1s.SetFillColor(c_yellow)

    graph_sigp1expclsf.SetFillColor(c_yellow)
    graph_sigp1expclsf.SetFillStyle(1001)
    graph_sigp1expclsf.SetLineColor(c_blue)
    graph_sigp1expclsf.SetLineStyle(7)
    graph_sigp1expclsf.SetLineWidth(2)

    # Load run 1 limit
    # if ',' in region:
    #     f = ROOT.TFile.Open(os.environ['SUSY_ANALYSIS'] + '/results/limit_run1_gln1.root')
    #     limit_run1    = f.Get('clsf_obs')
    #     leg.AddEntry(limit_run1, 'ATLAS 8 TeV, 20.3 fb^{-1}', 'F')


    if not args.onlyexp:
        obs_entry = leg.AddEntry(graph_sigp1clsf, "Observed limit (#pm1 #sigma^{SUSY}_{theory})", "LF")
    leg.AddEntry(graph_sigp1expclsf, "Expected limit (#pm1 #sigma_{exp})", "LF")
    
    leg.Draw()

    if not args.onlyexp and sig_xs_syst:
        ROOT.gPad.Update()
    
        n_rows = leg.GetNRows()

        x1 = 0.15
        y1 = 0.77
        x2 = 0.49
        y2 = 0.92
        margin = leg.GetMargin() * (x2-x1)
        boxw = margin*0.35
        yspace = (y2-y1) / n_rows

        xsym = x1 + margin/2.
        ysym = y2 - 0.5*yspace - yspace * (n_rows-2)
        dy = 0.015

        line = ROOT.TLine()
        ROOT.SetOwnership(line, False)
        line.SetLineColor(obs_entry.GetLineColor())
        line.SetLineWidth(2)
        line.SetLineStyle(3)
        line.DrawLineNDC(xsym-boxw, ysym+dy, xsym+boxw, ysym+dy)
        line.DrawLineNDC(xsym-boxw, ysym-dy, xsym+boxw, ysym-dy)


    # Plot
    sigclsd1s.Draw("same cont0")
    sigclsu1s.Draw("same cont0")

    graph_sigp1expclsf.Draw("same l")

    if not args.onlyexp:
        graph_sigp1clsf.Draw('same l')
        if sig_xs_syst:
            graph_sigp1clsfHigh.Draw("same l")
            graph_sigp1clsfLow.Draw("same l")

    # plot Run 1 limit
    # if ',' in region:
    #     limit_run1.SetLineWidth(2)
    #     limit_run1.SetLineColor(get_color('#b9b7b7'))
    #     limit_run1.SetFillColor(get_color('#c6c4c4'))
    #     limit_run1.Draw('f same')
    #     limit_run1.Draw('l same')


    # Redraw axis and update frame
    frame.RedrawAxis()
    ROOT.gPad.Update()


    output_tag = ''

    if args.obscls or args.expcls:
        # if sig_xs_syst:
        #     file_name    = '%s/Output_fixSigXSecNominal_hypotest__1_harvest_list.root' % path
        # else:
        #     file_name    = '%s/Output_hypotest__1_harvest_list.root' % path

        l_region = ROOT.TLatex()
        l_region.SetTextSize(0.014)
        l_region.SetTextColor(ROOT.kGray+2)

        if sig_xs_syst:
            tree_file = '%s/Output_fixSigXSecNominal_hypotest__1_harvest_list_hack.root' % path
        else:
            tree_file = '%s/Output_hypotest__1_harvest_list_hack.root' % path

        if args.obscls:
            cls_dict = get_cls_values(tree_file, False)
            output_tag = '_obscls'
        if args.expcls:
            cls_dict = get_cls_values(tree_file, True)
            output_tag = '_expcls'

        for (mgl, mn1), cls in cls_dict.iteritems():
            l_region.DrawLatex(mgl, mn1, "%.3f" % cls)

    elif args.bestsr:

        output_tag = '_bestsr'

        region_events = dict()
        dict_events = dict()
        
        for sel in region.split(','):
            if sig_xs_syst:
                tree_file = '%s/Output_%s_fixSigXSecNominal_hypotest__1_harvest_list_hack.root' % (path, sel)
            else:
                tree_file = '%s/Output_%s_hypotest__1_harvest_list_hack.root' % (path, sel)

            dict_events = get_cls_values(tree_file, exp=True)
            region_events[sel] = dict_events

        l_tot = ROOT.TLatex()
        l_tot.SetTextSize(0.016)
        l_tot.SetTextColor(ROOT.kGray+3)

        for mgl, mn1 in dict_events.iterkeys():

            binCLs = 100.
            best_region_string = ''
            for r in region_events.iterkeys():
                if region_events[r][(mgl, mn1)] < binCLs:
                    binCLs = region_events[r][(mgl, mn1)]
                    best_region_string = r
                    print mgl, mn1, r, binCLs

            l_tot.DrawLatex(mgl, mn1, "%s" % best_region_string[-1])


    elif args.points:

        lp = ROOT.TLatex()
        lp.SetTextSize(0.016)
        lp.SetTextColor(ROOT.kGray+3)

        for (m3, mu), (mgl, mn1) in grid_m3_mu.iteritems():
            if m3 > 2000:
                lp.SetTextColor(ROOT.kRed-4)
                lp.DrawLatex(mgl, mn1, "#times")
            else:
                lp.SetTextColor(ROOT.kGray+3)
                lp.DrawLatex(mgl, mn1, "#bullet")


    frame.SaveAs(path+'/limitPlot_%s%s.pdf' % (region.replace(',', '_'), output_tag))


    # Save contours
    outname = path + '/limit_contour_%s' % region.replace(',', '_') + '.root'

    outfile = ROOT.TFile(outname, 'recreate')
    outfile.cd()

    ## observed
    graph_sigp1clsf.Write('clsf_obs')
    if sig_xs_syst:
        graph_sigp1clsfHigh.Write("clsf_obs_up")
        graph_sigp1clsfLow.Write("clsf_obs_dn")

    ## expected
    graph_sigp1expclsf.Write('clsf_exp')
    if sig_xs_syst:
        graph_sigclsd1s = convert_hist_to_graph(sigclsd1s)
        graph_sigclsu1s = convert_hist_to_graph(sigclsu1s)

        graph_sigclsd1s.Write('clsf_exp_dn')
        graph_sigclsu1s.Write('clsf_exp_up')

    outfile.Close()


def get_cls_values(file_name, exp):

    import math
    file_ = ROOT.TFile(file_name)
    tree = file_.Get('tree')

    cls_dict = dict()
    for row in tree:

        if exp:
            cls_dict[(row.mgl, row.mn1)] = row.CLsexp
        else:
            cls_dict[(row.mgl, row.mn1)] = row.CLs

    file_.Close()

    return cls_dict


def combine_hypotest_files(inpaths, outpath):

    regions = args.region.split(',')

    #create new files (best expected)
    mkdirp(outpath)

    # Combine text files
    # description = "expectedUpperLimitMinus1Sig/F:upperLimitEstimatedError/F:fitstatus/F:p0d2s/F:p0u2s/F:seed/F:CLsexp/F:sigma1/F:failedfit/F:expectedUpperLimitPlus2Sig/F:nofit/F:nexp/F:sigma0/F:clsd2s/F:m3/F:expectedUpperLimit/F:failedstatus/F:xsec/F:covqual/F:upperLimit/F:p0d1s/F:clsd1s/F:failedp0/F:failedcov/F:p0exp/F:p1/F:p0u1s/F:excludedXsec/F:p0/F:clsu1s/F:clsu2s/F:expectedUpperLimitMinus2Sig/F:expectedUpperLimitPlus1Sig/F:mu/F:mode/F:fID/C:dodgycov/F:CLs/F"

    new_lines_nom = dict()
    new_lines_dn  = dict()
    new_lines_up  = dict()

    cls_dict = dict()

    for i, path in enumerate(inpaths):

        region = regions[i]

        lines_nom = open(path+'/Output_hypotest__1_harvest_list').read().split('\n')
        if sig_xs_syst:
            lines_nom = open(path+'/Output_fixSigXSecNominal_hypotest__1_harvest_list').read().split('\n')
            lines_dn = open(path+'/Output_fixSigXSecDown_hypotest__1_harvest_list').read().split('\n')
            lines_up = open(path+'/Output_fixSigXSecUp_hypotest__1_harvest_list').read().split('\n')

        for jline, line in enumerate(lines_nom):

            if not line:
                continue

            vals = line.split()

            m3 = int(float(vals[14]))
            mu = int(float(vals[33]))
            #cls = float(vals[-1]) # observed CLs
            cls = float(vals[6]) # expected CLs

            if (m3, mu) not in cls_dict:
                cls_dict[(m3, mu)] = cls

                new_lines_nom[(m3, mu)] = line
                if sig_xs_syst:
                    new_lines_dn[(m3, mu)] = lines_dn[jline]
                    new_lines_up[(m3, mu)] = lines_up[jline]

                print 'copying list for (%i, %i) %s CLs = %.3f' % (m3, mu, region, cls)
                    
            else:

                if cls < cls_dict[(m3, mu)]:

                    print 'changing list for (%i, %i) %s CLs = %.3f (old = %.3f)' % (m3, mu, region, cls, cls_dict[(m3, mu)]) 
                    
                    cls_dict[(m3, mu)] = cls

                    new_lines_nom[(m3, mu)] = line
                    if sig_xs_syst:
                        new_lines_dn[(m3, mu)] = lines_dn[jline]
                        new_lines_up[(m3, mu)] = lines_up[jline]



    # Save new list
    if sig_xs_syst:
        with open(outpath+'/Output_fixSigXSecNominal_hypotest__1_harvest_list', 'w') as f:
            for line in new_lines_nom.itervalues():
                f.write(line+'\n')

        with open(outpath+'/Output_fixSigXSecDown_hypotest__1_harvest_list', 'w') as f:
            for line in new_lines_dn.itervalues():
                f.write(line+'\n')

        with open(outpath+'/Output_fixSigXSecUp_hypotest__1_harvest_list', 'w') as f:
            for line in new_lines_up.itervalues():
                f.write(line+'\n')
    else:
        with open(outpath+'/Output_hypotest__1_harvest_list', 'w') as f:
            for line in new_lines_nom.itervalues():
                f.write(line+'\n')


def create_listfiles(path, region):

    print 'creating lists for %s' % path

    if not sig_xs_syst:

        inputfile  = path + '/Output_hypotest.root'
        output_dir = path

        jsonfile = inputfile.replace('hypotest.root', 'hypotest__1_harvest_list.json')
        listfile = jsonfile.replace('.json', '')

        format = "hypo_GGM_M3_mu_%f_%f"
        interpretation = "m3:mu"

        outputfile = ROOT.CollectAndWriteHypoTestResults(inputfile, format, interpretation, '1', True, output_dir)

        os.system('GenerateTreeDescriptionFromJSON.py -f %s -o %s' % (jsonfile,listfile))

    else:
        for syst in ['Nominal', 'Up', 'Down']:

            inputfile  = path + '/Output_fixSigXSec%s_hypotest.root' % syst
            output_dir = path

            jsonfile = inputfile.replace('hypotest.root', 'hypotest__1_harvest_list.json')
            listfile = jsonfile.replace('.json', '')

            format = "hypo_GGM_M3_mu_%f_%f"
            interpretation = "m3:mu"

            outputfile = ROOT.CollectAndWriteHypoTestResults(inputfile, format, interpretation, '1', True, output_dir)

            os.system('GenerateTreeDescriptionFromJSON.py -f %s -o %s' % (jsonfile,listfile))


def create_contourhists(path, region):

    print 'creating contours for %s' % path

    if not sig_xs_syst:

        inputfile  = path + '/Output_hypotest__1_harvest_list'

        template2D = ROOT.TH2D("template2D", "template2D", max_x-min_x, min_x, max_x, max_y-min_y, min_y, max_y)

        create_histograms(path, inputfile, template2D)

    else:
        for syst in ['Nominal', 'Up', 'Down']:

            inputfile  = path + '/Output_fixSigXSec%s_hypotest__1_harvest_list' % syst

            template2D = ROOT.TH2D("template2D", "template2D", max_x-min_x, min_x, max_x, max_y-min_y, min_y, max_y)
            
            create_histograms(path, inputfile, template2D)


def hack_tree(textfile, tree):

    # save original tree
    file_ = ROOT.TFile(textfile+'_orig.root', "recreate");
    origtree = tree.CloneTree()
    file_.Write()
    file_.Close()

    # create and save new tree with masses
    newfile = ROOT.TFile(textfile+'_hack.root', "recreate");
    newtree = tree.CloneTree(0) # Do no copy the data yet

    mgl = array('i', [0]) 
    mn1 = array('i', [0]) 

    newtree.Branch('mgl', mgl, 'mgl/I')
    newtree.Branch('mn1', mn1, 'mn1/I')

    for row in tree:

        # if row.CLs == 0 or row.CLsexp == 0:
        #     print 'weird point: (%s, %s), %.2f, %.2f, %.2f' % (row.m3, row.mu, row.CLs, row.CLsexp, row.clsu1s)
        #     #continue
        try:
            mgl[0], mn1[0] = mass_dict[(int(row.m3), int(row.mu))]
        except:
            continue

        newtree.Fill()
    
    newfile.Write()

    return

def triwsmooth(tree, varstr, name, title, cutstr, inputHist):

    if tree is None:
        return 0

    ntotal = tree.GetEntries("1")
    nselect = tree.GetEntries(cutstr)

    print "Plotting", varstr, "with selection", cutstr, "." 
    print "Selected", nselect, "out of", ntotal, "entries. Fraction =", float(nselect)/ntotal

    tree.Draw(varstr, cutstr, "goff")
    nrows = tree.GetSelectedRows()
    v1 = tree.GetV1()
    v2 = tree.GetV2()
    v3 = tree.GetV3()

    if nselect == 0:
        return 0;

    gr = ROOT.TGraph2D(nrows, v3, v2, v1)

    gr.SetName(name) 
    gr.SetTitle(title) 
    gr.Draw("TRIW")

    if inputHist is not None:
        gr.SetHistogram(inputHist)
    
    foo = gr.GetHistogram()
    hist = foo.Clone()

    # for some reason this doesn't work in cint?
    hist.SetName(name)
    hist.SetTitle(title)

    return hist


def create_histograms(path, textfile, input_hist):

    sys.path.append(path)
    from summary_harvest_tree_description import harvesttree

    xystr = 'mn1:mgl'
    #xystr = 'mu:m3'

    # get the harvested tree
    tree = harvesttree(textfile)

    hack_tree(textfile, tree)

    f = ROOT.TFile(textfile+'_hack.root')
    tree = f.Get('tree')

    if tree == 0:
        print "Cannot open list file. Exit."
        return

    # store histograms to output file
    outfile = textfile + '.root'

    print "Histograms being written to : ", outfile

    output = ROOT.TFile.Open(outfile, "RECREATE")
    output.cd()

    clonehclPmin2 = input_hist.Clone()
    hist = ROOT.DrawUtil.triwsmooth(tree, 'p1:'+xystr, "hclPmin2" , "Observed CLsplusb", "p1>=0 && p1<=1", clonehclPmin2)

    if hist != 0:
        hist.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    clonesigp1 = input_hist.Clone()
    sigp1 = ROOT.DrawUtil.triwsmooth(tree, 'StatTools::GetSigma(p1):'+xystr, "sigp1" , "One-sided significance of CLsplusb", "(p1>=0 && p1<=1)", clonesigp1)

    if sigp1 != 0:
        sigp1.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    # cls:clsexp:clsu1s:clsd1s
    clonep1clsf = input_hist.Clone()
    p1clsf = ROOT.DrawUtil.triwsmooth(tree, 'CLs:'+xystr, "p1clsf" , "Observed CLs", "p1>=0 && p1<=1", clonep1clsf)

    if p1clsf != 0:
        p1clsf.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    clonesigp1clsf = input_hist.Clone()
    sigp1clsf = ROOT.DrawUtil.triwsmooth(tree, 'StatTools::GetSigma(CLs):'+xystr, "sigp1clsf" , "One-sided significalce of observed CLs", "p1>=0 && p1<=1", clonesigp1clsf)

    if sigp1clsf != 0:
        sigp1clsf.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    clonesigp1expclsf = input_hist.Clone()
    sigp1expclsf = ROOT.DrawUtil.triwsmooth(tree, 'StatTools::GetSigma(CLsexp):'+xystr, "sigp1expclsf" , "One-sided significalce of expected CLs", "p1>=0 && p1<=1", clonesigp1expclsf)

    if sigp1expclsf != 0:
        sigp1expclsf.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    clonesigclsu1s = input_hist.Clone();
    sigclsu1s = ROOT.DrawUtil.triwsmooth(tree, 'StatTools::GetSigma(clsu1s):'+xystr, "sigclsu1s" , "One-sided significalce of expected CLs (+1 sigma)", "clsu1s>=0", clonesigclsu1s)

    if sigclsu1s != 0:
        sigclsu1s.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    clonesigclsd1s = input_hist.Clone()
    sigclsd1s = ROOT.DrawUtil.triwsmooth(tree , 'StatTools::GetSigma(clsd1s):'+xystr, "sigclsd1s" , "One-sided significalce of expected CLs (-1 sigma)", "clsd1s>=0", clonesigclsd1s)

    if sigclsd1s != 0:
        sigclsd1s.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    # # upper limit * cross section plots
    # cloneupperlimit = input_hist.Clone()
    # UpperLimit = ROOT.DrawUtil.triwsmooth(tree, 'upperLimit:'+xystr, "upperLimit" , "upperlimit", "1", cloneupperlimit)

    # if UpperLimit != 0:
    #     UpperLimit.Write()
    # else:
    #     print "Cannot make smoothed significance histogram. Exit."

    # clonexsec = input_hist.Clone()
    # xsec = ROOT.DrawUtil.triwsmooth(tree, 'xsec:'+xystr, "xsec" , "xsec","1", clonexsec)

    # if xsec != 0:
    #     xsec.Write()
    # else:
    #     print "Cannot make smoothed significance histogram. Exit."

    # cloneexcludedXsec = input_hist.Clone()
    # excludedXsec = ROOT.DrawUtil.triwsmooth(tree, 'excludedXsec:'+xystr, "excludedXsec" , "excludedXsec", "1", cloneexcludedXsec)

    # if excludedXsec != 0:
    #     excludedXsec.Write()
    # else:
    #     print "Cannot make smoothed significance histogram. Exit."

    output.Close()

    return outfile


def print_common_usage():
    print ''
    print 'common usage:'
    print '             plot_exclusion.py --combine [path1] [path2] [output path]'
    print '             plot_exclusion.py --list --sr SR [path]'
    print '             plot_exclusion.py --cont --sr SR [path]'
    print '             plot_exclusion.py --plot --sr SR [path]'


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('paths', nargs='+', help='path to workspace')
    parser.add_argument("--sr", dest='region', help="Signal Region(s)")
    parser.add_argument('-o', '--output', default='.', help='Output directory for the plots')
    parser.add_argument('--combine', action='store_true', help='Combine hypotest files')
    parser.add_argument('--list', action="store_true", help='Produce lists')
    parser.add_argument('--cont', action="store_true", help='Produce contours')
    parser.add_argument('--plot', action="store_true", dest='plot', help='Produce plot')

    parser.add_argument('--onlyexp', action="store_true", help='only expected')
    parser.add_argument('--datalabel', help='only expected')

    # extra text
    parser.add_argument('--bestsr', action='store_true')
    parser.add_argument('--obscls', action='store_true')
    parser.add_argument('--expcls', action='store_true')
    parser.add_argument('--points', action='store_true')
    #parser.add_argument('--nEvts', action='store_true')
    #parser.add_argument('--xsUL', action='store_true')

    global args

    try:
        args = parser.parse_args()
    except:
        print_common_usage()
        raise

    if not (args.combine or args.list or args.cont or args.plot):
        print_common_usage()

    if not args.output.endswith('/'):
        args.output = args.output + '/'

    global min_x, max_x, min_y, max_y

    min_y = 147
    max_y = 2550
    min_x = 1146
    max_x = 2600

    set_default_style()

    # guess if signal xs up/down files exist
    first_path = args.paths[0]
    global sig_xs_syst
    sig_xs_syst = False
    if os.path.exists('%s/Output_fixSigXSecNominal_hypotest.root' % first_path):
        sig_xs_syst = True

    if os.path.exists('%s/Output_fixSigXSecNominal_hypotest__1_harvest_list' % first_path):
        sig_xs_syst = True



    # Combine hypotest files in one: take last path as output
    if args.combine:
        inpaths = args.paths[:-1]
        outpath = args.paths[-1]

        if len(args.region.split(',')) != len(inpaths):
            print 'error'
            sys.exit()

        combine_hypotest_files(inpaths, outpath)
        sys.exit()

    # Create input files
    if args.list:
        if len(args.paths) > 1:
            parser.print_usage()
            sys.exit()

        create_listfiles(first_path, args.region)

    if args.cont:
        if len(args.paths) > 1:
            parser.print_usage()
            sys.exit()

        create_contourhists(first_path, args.region)

    if args.plot:
        plot_exclusion(first_path, args.region, args.output)

