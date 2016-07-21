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
from rootutils import set_default_style, set_atlas_style, legend, get_color
from drawutils import draw_grid_frame
from mass_dict import mass_dict



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


def add_theory_band(leg, entry):

    nRows = leg.GetNRows();
    if nRows < 1:
        return
    
    if leg.GetNColumns() != 1:
        return

    ROOT.gPad.Update()
    x1 = leg.GetX1NDC()
    y1 = leg.GetY1NDC()
    x2 = leg.GetX2NDC()
    y2 = leg.GetY2NDC()
    margin = leg.GetMargin()*(x2-x1)
    boxw = margin*0.35
    yspace = (y2-y1)/nRows

    xsym = x1 + margin/2.
    ysym = y2 - 0.5*yspace
    dy = 0.015

    entries = leg.GetListOfPrimitives()
    for ientry in xrange(entries.GetSize()):
        if entries.At(ientry) == entry:
            break
        ysym -= yspace
    
    line = ROOT.TLine()
    line.SetLineColor(entry.GetLineColor())
    line.SetLineWidth(2)
    line.SetLineStyle(3)
    line.DrawLineNDC(xsym-boxw, ysym+dy, xsym+boxw, ysym+dy)
    line.DrawLineNDC(xsym-boxw, ysym-dy, xsym+boxw, ysym-dy)


def plot_exclusion(path, region, outdir, sig_xs_syst):

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
    sigp1clsf     = return_contour95('sigp1clsf', file_name)
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

    # Colours
    c_yellow = ROOT.TColor.GetColor('#ffe938')
    c_red    = ROOT.TColor.GetColor('#aa0000')
    c_blue   = ROOT.TColor.GetColor('#28373c')

    frame = draw_grid_frame() 

    # Create the text in the plot
    # DATA info
    leg1 = ROOT.TLatex()
    leg1.SetTextSize(0.03)
    leg1.SetTextColor(1)
    leg1.DrawLatex(1200, 1550, style.data_label)

    # Region
    leg3 = ROOT.TLatex()
    leg3.SetTextAlign(11)
    leg3.SetTextSize(0.035)
    leg3.SetTextColor(1)
    leg3.SetTextFont(42)

    region_text = region

    if 'SRL,SRH' in region_text:
        region_text = region_text = 'SR_{L} and SR_{H}'
    elif 'SRL' in region_text:
        region_text = 'SR_{L}'
    elif 'SRH' in region_text:
        region_text = 'SR_{H}'
    elif 'SRiL,SRiH' in region_text:
        region_text = region_text = 'SR^{incl}_{L} and SR^{incl}_{H}'
    elif 'SRiL' in region_text:
        region_text = 'SR^{incl}_{L}'
    elif 'SRiH' in region_text:
        region_text = 'SR^{incl}_{H}'

    leg3.DrawLatex(1200, 1400, region_text)

    # Legend
    leg  = ROOT.TLegend(0.15, 0.79, 0.52, 0.90)
    leg.SetFillColor(0)
    leg.SetBorderSize(0)

    # extra text
    leg4 = ROOT.TLatex()
    leg4.SetNDC()
    leg4.SetTextSize(0.03)
    leg4.SetTextColor(1)
    leg4.SetTextAngle(90)

    if (args.obsCLs or args.expCLs or args.bestSR):

        leg4.SetTextColor(ROOT.kGray+2)

        textx = 0.98
        texty = 0.15

        if args.obsCLs:
            leg4.DrawLatex(textx, texty, 'Numbers give observed CL_{s} values')
        elif args.expCLs:
            leg4.DrawLatex(textx, texty, 'Numbers give expected CL_{s} values')
        elif args.bestSR:
            leg4.DrawLatex(textx, texty, 'Numbers give the best SR')
        elif args.nEvts:
            leg4.DrawLatex(textx, texty, '# events')

    # leg2 = ROOT.TLatex()
    # leg2.SetNDC()
    # leg2.SetTextSize(0.03)
    # leg2.SetTextColor(1)
    # leg2.DrawLatex(0.17, 0.75, "All limits at 95% CL")

    # leg2.AppendPad()
    # leg4.AppendPad()

    graph_sigp1clsf     = convert_hist_to_graph(sigp1clsf)

    graph_sigp1clsf.SetFillColor(ROOT.kWhite)
    graph_sigp1clsf.SetFillStyle(3003)
    graph_sigp1clsf.SetLineColor(c_red)
    graph_sigp1clsf.SetLineStyle(1)
    graph_sigp1clsf.SetLineWidth(3)

    if sig_xs_syst:
        graph_sigp1clsfLow  = convert_hist_to_graph(sigp1clsfLow)
        graph_sigp1clsfHigh = convert_hist_to_graph(sigp1clsfHigh)

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

    graph_sigp1expclsf = convert_hist_to_graph(sigp1expclsf)
    graph_sigp1expclsf.SetFillColor(c_yellow)
    graph_sigp1expclsf.SetFillStyle(1001)
    graph_sigp1expclsf.SetLineColor(c_blue)
    graph_sigp1expclsf.SetLineStyle(7)
    graph_sigp1expclsf.SetLineWidth(2)

    # Load run 1 limit
    # if ',' in region:
    #     f = ROOT.TFile.Open(os.environ['SUSY_ANALYSIS'] + '/results/limit_run1_gln1.root')
    #     limit_run1    = f.Get('clsf_obs')

    #     leg.AddEntry(limit_run1, 'Run 1 observed limit', 'F') # (#sqrt{s} = 8 TeV, 20.3 fb^{-1})', 'F')


    obs_entry = leg.AddEntry(graph_sigp1clsf, "Observed limit (#pm1 #sigma^{SUSY}_{theory})", "LF")
    #add_theory_band(leg, obs_entry)
    leg.AddEntry(graph_sigp1expclsf, "Expected limit (#pm1 #sigma_{exp})", "LF")
    leg.Draw('same')


    # Plot
    sigclsd1s.Draw("same cont0")
    sigclsu1s.Draw("same cont0")
    graph_sigp1expclsf.Draw("same l")

    graph_sigp1clsf.Draw('same l')
    if sig_xs_syst:
        graph_sigp1clsfHigh.Draw("same l")
        graph_sigp1clsfLow.Draw("same l")

    # plot Run 1 limit
    # if ',' in region:
    #     color_run1 = get_color('#878383')

    #     limit_run1.SetLineWidth(2)
    #     limit_run1.SetLineColor(color_run1)
    #     limit_run1.SetFillColor(color_run1)
    #     limit_run1.Draw('f same')


    # Redraw axis and update frame
    frame.RedrawAxis()

    if args.obsCLs or args.expCLs:

        file_name    = '%s/Output_fixSigXSecNominal_hypotest__1_harvest_list.root' % path

        l_region = ROOT.TLatex()
        l_region.SetTextSize(0.014)
        l_region.SetTextColor(ROOT.kGray+2)

        finalStr = ''
        dict_events = dict()
        if args.obsCLs:
            dict_events = get_cls_values(region, file_name, 'p1clsf', False)
            finalStr = 'obsCLs'
        if args.expCLs:
            dict_events = get_cls_values(region, file_name, 'sigp1expclsf', True)
            finalStr = 'expCLs'

        for m3, mu in dict_events.keys():

            mgl, mn1 = mass_dict[(m3, mu)]
            cls = dict_events[(m3, mu)]

            l_region.DrawLatex(mgl, mn1, "%.3f" % cls)

        frame.Update()
        #frame.SaveAs(outdir+'limitPlot_%s_%s.eps' % (region.replace(',', '_'), finalStr))
        frame.SaveAs(path+'/limitPlot_%s_%s.pdf' % (region.replace(',', '_'), finalStr))

    elif args.xsUL:

        from upperlimit import upperlimit

        from SUSY_GGM_M3_mu_mc12points import pointdict

        l_region = ROOT.TLatex()
        l_region.SetTextSize(0.016)
        l_region.SetTextColor(ROOT.kGray+3)

        for m3, mu in pointdict.itervalues():

            if mu == 150:
                continue

            xsul = upperlimit.get((m3, mu)) * xsect_dict.get(m3) * 1000 # in fb
            
            mgl, mn1 = mass_dict[(m3, mu)]
            l_region.DrawLatex(mgl, mn1, "%.2f" % xsul)

        frame.Update()
        frame.SaveAs(path+'/limitPlot_%s_xsul.pdf' % region.replace(',', '_'))

    elif args.bestSR:

        finalStr = ''
        region_events = dict()
        dict_events = dict()

        for sel in region.split(','):
            file_name = '%s/Output_%s_fixSigXSecNominal_hypotest__1_harvest_list.root' % (path, sel)

            dict_events = get_cls_values(sel, file_name, 'sigp1clsf', True)
            region_events[sel] = dict_events

        l_tot = ROOT.TLatex()
        l_tot.SetTextSize(0.016)
        l_tot.SetTextColor(ROOT.kGray+3)

        for m3, mu in dict_events.keys():

            binCLs = 100.
            best_region_string = ''
            for r in region_events.keys():
                if region_events[r][(m3, mu)] < binCLs:
                    binCLs = region_events[r][(m3, mu)]
                    best_region_string = r

            l_tot.DrawLatex(m3, mu, "%s" % best_region_string[-1])

        frame.Update()
        frame.SaveAs(path+'/limitPlot_%s_BestSR.pdf' % region.replace(',', '_'))

    elif args.nEvts:

        finalStr = ''
        region_events = dict()
        region_cls = dict()

        for sel in region.split(','):

            dict_events = get_truth_events(sel)
            region_events[sel] = dict_events

            file_name = '%s/Output_%s_fixSigXSecNominal_hypotest__1_harvest_list.root' % (path, sel)

            dict_cls = get_cls_values(sel, file_name, 'sigp1clsf', True)
            region_cls[sel] = dict_cls

        l_tot = ROOT.TLatex()
        l_tot.SetTextSize(0.016)
        l_tot.SetTextColor(ROOT.kGray+3)

        for sig in dict_events.keys():

            m3, mu = (sig[0], sig[1])
            
            cls = 1000.
            best_region_string = ''
            for r in region_cls.keys():
                if region_cls[r][sig] < cls:
                    cls = region_cls[r][sig]
                    best_region_string = r

            evts = region_events[best_region_string][sig]

            mgl, mn1 = mass_dict[(m3, mu)]

            l_tot.DrawLatex(mgl, mn1, "%s" % evts)

        frame.Update()
        #frame.SaveAs(outdir+'limitPlot_%s_nEvts.eps' % region.replace(',', '_'))
        frame.SaveAs(path+'/limitPlot_%s_nEvts.pdf' % region.replace(',', '_'))

    else:
        frame.SaveAs(path+'/limitPlot_%s.pdf' % region.replace(',', '_'))

    if args.save is not None:
        outfile = ROOT.TFile(args.save, 'recreate')
        outfile.cd()

        # observed
        graph_sigp1clsf.Write('clsf_obs')

        if sig_xs_syst:
            graph_sigp1clsfHigh.Write("clsf_obs_up")
            graph_sigp1clsfLow.Write("clsf_obs_dn")

        # expected
        graph_sigp1expclsf.Write('clsf_exp')
    
        if sig_xs_syst:
            graph_sigclsd1s = convert_hist_to_graph(sigclsd1s)
            graph_sigclsu1s = convert_hist_to_graph(sigclsu1s)

            graph_sigclsd1s.Write('clsf_exp_dn')
            graph_sigclsu1s.Write('clsf_exp_up')

        outfile.Close()


def get_truth_events(sel):

    if '2' in sel:
        selection = getattr(regions, 'SR_2')
    elif '3' in sel:
        selection = getattr(regions, 'SR_3')
    else:
        return {}

    # get_events = partial(miniutils.get_events, selection=selection, truth=True)

    dict_names = dict()

    from SUSY_GGM_M3_mu_mc12points import pointdict

    for pm3, pmu in pointdict.itervalues():

        if pmu == 175:
            continue

        evts = miniutils.get_events('GGM_M3_mu_all_%i_%i' % (pm3, pmu), selection, truth=True)

        dict_names[(pm3, pmu)] = round(evts.mean, 2)

    return dict_names


def get_cls_values(sel, file_name, histo_name, input_is_significance):

    import math
    file_significance = ROOT.TFile(file_name)
    histo_sig = file_significance.Get(histo_name).Clone()

    dict_names = dict()

    from SUSY_GGM_M3_mu_mc12points import pointdict
    for pm3, pmu in pointdict.itervalues():

        if pmu == 175:
            continue

        mgl, mn1 = mass_dict[(pm3, pmu)]

        bin_x = histo_sig.GetXaxis().FindBin(mgl)
        bin_y = histo_sig.GetYaxis().FindBin(mn1)

        bin_ = histo_sig.GetBin(bin_x, bin_y, 0)

        if input_is_significance: #--- Convert from significance to CLs
            dict_names[(pm3, pmu)] = 1 - ROOT.TMath.Freq(histo_sig.GetBinContent(bin_))
        else: #--- Read directly CLs
            dict_names[(pm3, pmu)] = histo_sig.GetBinContent(bin_)

    #--- Check if there are any errors: 0 or 0.5
    for m3, mu in dict_names.iterkeys():
        step = 0
        while (dict_names[(m3, mu)] == 0. or dict_names[(m3, mu)] == 0.5):
            shiftX = 0
            shiftY = 0
            if step == 0:
                shiftY = 5
            elif step == 1:
                shiftY = 10
            elif step == 2:
                shiftY = -5
            elif step == 3:
                shiftY = -10
            elif step == 4:
                shiftY = -15
            elif step == 5:
                shiftX = 5
            elif step == 6:
                shiftX = 10
            elif step == 7:
                shiftX = -5
            elif step == 8:
                shiftX = -10
            elif step == 9:
                shiftX = -5
                shiftY = -5
            elif step == 10:
                shiftX = -10
                shiftY = -10
            else:
                break

            mgl, mn1 = mass_dict[(pm3, pmu)]

            bin_x = histo_sig.GetXaxis().FindBin(mgl) + shiftX
            bin_y = histo_sig.GetYaxis().FindBin(mn1) + shiftY

            bin_ = histo_sig.GetBin(bin_x, bin_y, 0)

            if input_is_significance:
                dict_names[(m3,mu)] = 1 - ROOT.TMath.Freq(histo_sig.GetBinContent(bin_))
            else:
                dict_names[(m3, mu)] = histo_sig.GetBinContent(bin_)

            step += 1

    histo_sig.Delete()
    file_significance.Close()

    return dict_names


def combine_hypotest_file(inpaths, outpath):

    print 'Combine the following path into this:', outpath
    for i in inpaths:
        print i

    mkdirp(outpath)

    new_rootfile = ROOT.TFile(outpath, 'recreate')

    kovw = ROOT.TObject.kOverwrite

    regions = args.region.split(',')

    counter = 1
    for i, path in enumerate(inpaths):

        region = regions[i]

        os.system('cp %s %s' % (path, outpath))

        old_rootfile = ROOT.TFile(path)

        for keyold in old_rootfile.GetListOfKeys():

            if not 'hypo' in keyold.GetName():
                continue

            old_rootfile.cd()
            hypo_obj = old_rootfile.Get(keyold.GetName()).Clone()
            fit_obj  = old_rootfile.Get(keyold.GetName().replace('hypo','fitTo')).Clone()

            if counter == 1:
                print 'Copying the first time %s: %.4f' % (hypo_obj.GetName(), hypo_obj.CLs(0))
                new_rootfile.cd()
                hypo_obj.Write(keyold.GetName(), kovw)
                fit_obj.Write(keyold.GetName().replace('hypo','fitTo'), kovw)

            else:
                hypo_obj_new = new_rootfile.Get(keyold.GetName()).Clone()
                fit_obj_new  = new_rootfile.Get(keyold.GetName().replace('hypo','fitTo')).Clone()

                if (hypo_obj_new.CLs(0) > hypo_obj.CLs(0)):
                    print 'Substitution %s -- Old: %.4f New %s: %.4f' % (hypo_obj.GetName(), hypo_obj.CLs(0), hypo_obj_new.CLs(0))
                    new_rootfile.cd()
                    hypo_obj.Write(keyold.GetName(), kovw)
                    fit_obj.Write(keyold.GetName().replace('hypo','fitTo'), kovw)

                hypo_obj_new.Delete()
                fit_obj_new.Delete()

            hypo_obj.Delete()
            fit_obj.Delete()

        counter += 1
        old_rootfile.Close()

    new_rootfile.Close()


def combine_hypotest_files(inpaths, outpath, sig_xs_syst):

    print 'Combine the following path into this:', outpath
    for i in inpaths:
        print i

    #create new files (best expected)
    mkdirp(outpath)

    if sig_xs_syst:
        new_rootfile_nom = ROOT.TFile(outpath + '/Output_fixSigXSecNominal_hypotest.root', 'recreate')
        new_rootfile_up  = ROOT.TFile(outpath + '/Output_fixSigXSecUp_hypotest.root', 'recreate')
        new_rootfile_dn  = ROOT.TFile(outpath + '/Output_fixSigXSecDown_hypotest.root', 'recreate')
    else:
        new_rootfile_nom = ROOT.TFile(outpath + '/Output_hypotest.root', 'recreate')

    kovw = ROOT.TObject.kOverwrite

    regions = args.region.split(',')

    counter = 1
    for i, path in enumerate(inpaths):

        region = regions[i]

        if sig_xs_syst:
            os.system('cp %s/Output_fixSigXSecNominal_hypotest.root %s/Output_%s_fixSigXSecNominal_hypotest.root' % (path, outpath, region))
            os.system('cp %s/Output_fixSigXSecUp_hypotest.root %s/Output_%s_fixSigXSecUp_hypotest.root' % (path, outpath, region))
            os.system('cp %s/Output_fixSigXSecDown_hypotest.root %s/Output_%s_fixSigXSecDown_hypotest.root' % (path, outpath, region))

            old_rootfile_nom = ROOT.TFile(path+'/Output_fixSigXSecNominal_hypotest.root')
            old_rootfile_up  = ROOT.TFile(path+'/Output_fixSigXSecUp_hypotest.root')
            old_rootfile_dn  = ROOT.TFile(path+'/Output_fixSigXSecDown_hypotest.root')

        else:
            os.system('cp %s/Output_hypotest.root %s/Output_%s_hypotest.root' % (path, outpath, region))

            old_rootfile_nom = ROOT.TFile(path+'/Output_hypotest.root')

        for keyold in old_rootfile_nom.GetListOfKeys():

            if not 'hypo' in keyold.GetName():
                continue

            old_rootfile_nom.cd()
            hypo_obj_nom = old_rootfile_nom.Get(keyold.GetName()).Clone()
            fit_obj_nom  = old_rootfile_nom.Get(keyold.GetName().replace('hypo','fitTo')).Clone()

            if sig_xs_syst:
                old_rootfile_up.cd()
                hypo_obj_up = old_rootfile_up.Get(keyold.GetName()).Clone()
                fit_obj_up  = old_rootfile_up.Get(keyold.GetName().replace('hypo','fitTo')).Clone()

                old_rootfile_dn.cd()
                hypo_obj_dn = old_rootfile_dn.Get(keyold.GetName()).Clone()
                fit_obj_dn  = old_rootfile_dn.Get(keyold.GetName().replace('hypo','fitTo')).Clone()

            if counter == 1:
                print 'Copying the first time %s: %.4f' % (hypo_obj_nom.GetName(), hypo_obj_nom.CLs(0))
                new_rootfile_nom.cd()
                hypo_obj_nom.Write(keyold.GetName(), kovw)
                fit_obj_nom.Write(keyold.GetName().replace('hypo','fitTo'), kovw)

                if sig_xs_syst:
                    new_rootfile_up.cd()
                    hypo_obj_up.Write(keyold.GetName(), kovw)
                    fit_obj_up.Write(keyold.GetName().replace('hypo','fitTo'), kovw)

                    new_rootfile_dn.cd()
                    hypo_obj_dn.Write(keyold.GetName(), kovw)
                    fit_obj_dn.Write(keyold.GetName().replace('hypo','fitTo'), kovw)
            else:
                hypo_obj_nom_new = new_rootfile_nom.Get(keyold.GetName()).Clone()
                fit_obj_nom_new  = new_rootfile_nom.Get(keyold.GetName().replace('hypo','fitTo')).Clone()

                if sig_xs_syst:
                    hypo_obj_up_new = new_rootfile_up.Get(keyold.GetName()).Clone()
                    fit_obj_up_new  = new_rootfile_up.Get(keyold.GetName().replace('hypo','fitTo')).Clone()

                    hypo_obj_dn_new = new_rootfile_dn.Get(keyold.GetName()).Clone()
                    fit_obj_dn_new  = new_rootfile_dn.Get(keyold.GetName().replace('hypo','fitTo')).Clone()

                if (hypo_obj_nom_new.CLs(0) > hypo_obj_nom.CLs(0)):
                    print 'Substitution %s -- Old: %.4f New: %.4f' % (hypo_obj_nom.GetName(), hypo_obj_nom_new.CLs(0), hypo_obj_nom.CLs(0))
                    new_rootfile_nom.cd()
                    hypo_obj_nom.Write(keyold.GetName(), kovw)
                    fit_obj_nom.Write(keyold.GetName().replace('hypo','fitTo'), kovw)

                    if sig_xs_syst:
                        new_rootfile_up.cd()
                        hypo_obj_up.Write(keyold.GetName(), kovw)
                        fit_obj_up.Write(keyold.GetName().replace('hypo','fitTo'), kovw)

                        new_rootfile_dn.cd()
                        hypo_obj_dn.Write(keyold.GetName(), kovw)
                        fit_obj_dn.Write(keyold.GetName().replace('hypo','fitTo'), kovw)

                hypo_obj_nom_new.Delete()
                fit_obj_nom_new.Delete()
                if sig_xs_syst:
                    hypo_obj_up_new.Delete()
                    fit_obj_up_new.Delete()
                    hypo_obj_dn_new.Delete()
                    fit_obj_dn_new.Delete()

            hypo_obj_nom.Delete()
            fit_obj_nom.Delete()
            if sig_xs_syst:
                hypo_obj_up.Delete()
                fit_obj_up.Delete()
                hypo_obj_dn.Delete()
                fit_obj_dn.Delete()

        counter += 1
        old_rootfile_nom.Close()
        if sig_xs_syst:
            old_rootfile_up.Close()
            old_rootfile_dn.Close()

    new_rootfile_nom.Close()
    if sig_xs_syst:
        new_rootfile_up.Close()
        new_rootfile_dn.Close()
        

def create_listfiles(path, region, sig_xs_syst):

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


def create_contourhists(path, region, sig_xs_syst):

    print 'creating contours for %s' % path

    if not sig_xs_syst:

        inputfile  = path + '/Output_hypotest__1_harvest_list'

        template2D = None
        analysisName = 'GGM'
        template2D = ROOT.TH2D("template2D", "template2D", max_x-min_x, min_x, max_x, max_y-min_y, min_y, max_y)

        create_histograms(path, inputfile, template2D)

    else:
        for syst in ['Nominal', 'Up', 'Down']:

            inputfile  = path + '/Output_fixSigXSec%s_hypotest__1_harvest_list' % syst

            template2D = None
            analysisName = 'GGM'
            template2D = ROOT.TH2D("template2D", "template2D", max_x-min_x, min_x, max_x, max_y-min_y, min_y, max_y)
            
            create_histograms(path, inputfile, template2D)


def hack_tree(textfile, tree):

    newfile = ROOT.TFile(textfile+'_hack.root', "recreate");
    newtree = tree.CloneTree(0) # Do no copy the data yet

    mgl = array('i', [0]) 
    mn1 = array('i', [0]) 

    newtree.Branch('mgl', mgl, 'mgl/I')
    newtree.Branch('mn1', mn1, 'mn1/I')

    for row in tree:

        # if row.CLs == 0 or row.CLsexp == 0:
        #     print 'weird point: (%s, %s)' % (row.m3, row.mu)
        #     continue

        mgl[0], mn1[0] = mass_dict[(int(row.m3), int(row.mu))]

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
    hist = triwsmooth(tree, 'p1:'+xystr, "hclPmin2" , "Observed CLsplusb", "p1>=0 && p1<=1", clonehclPmin2)

    if hist != 0:
        hist.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    clonesigp1 = input_hist.Clone()
    sigp1 = triwsmooth(tree, 'StatTools::GetSigma(p1):'+xystr, "sigp1" , "One-sided significance of CLsplusb", "(p1>=0 && p1<=1)", clonesigp1)
    #sigp1 = triwsmooth(tree, 'TMath::NormQuantile(1-p1):'+xystr, "sigp1" , "One-sided significance of CLsplusb", "(p1>=0 && p1<=1)", clonesigp1)

    if sigp1 != 0:
        sigp1.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    # cls:clsexp:clsu1s:clsd1s
    clonep1clsf = input_hist.Clone()
    p1clsf = triwsmooth(tree, 'CLs:'+xystr, "p1clsf" , "Observed CLs", "p1>=0 && p1<=1", clonep1clsf)

    if p1clsf != 0:
        p1clsf.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    clonesigp1clsf = input_hist.Clone()
    sigp1clsf = triwsmooth(tree, 'StatTools::GetSigma(CLs):'+xystr, "sigp1clsf" , "One-sided significalce of observed CLs", "p1>=0 && p1<=1", clonesigp1clsf)
    #sigp1clsf = triwsmooth(tree, 'TMath::NormQuantile(1-CLs):'+xystr, "sigp1clsf" , "One-sided significalce of observed CLs", "p1>=0 && p1<=1", clonesigp1clsf)

    if sigp1clsf != 0:
        sigp1clsf.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    clonesigp1expclsf = input_hist.Clone()
    sigp1expclsf = triwsmooth(tree, 'StatTools::GetSigma(CLsexp):'+xystr, "sigp1expclsf" , "One-sided significalce of expected CLs", "p1>=0 && p1<=1", clonesigp1expclsf)
    #sigp1expclsf = triwsmooth(tree, 'TMath::NormQuantile(1-CLsexp):'+xystr, "sigp1expclsf" , "One-sided significalce of expected CLs", "p1>=0 && p1<=1", clonesigp1expclsf)
    if sigp1expclsf != 0:
        sigp1expclsf.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    clonesigclsu1s = input_hist.Clone();
    sigclsu1s = triwsmooth(tree, 'StatTools::GetSigma(clsu1s):'+xystr, "sigclsu1s" , "One-sided significalce of expected CLs (+1 sigma)", "clsu1s>=0", clonesigclsu1s)
    #sigclsu1s = triwsmooth(tree, 'TMath::NormQuantile(1-clsu1s):'+xystr, "sigclsu1s" , "One-sided significalce of expected CLs (+1 sigma)", "clsu1s>=0", clonesigclsu1s)

    if sigclsu1s != 0:
        sigclsu1s.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    clonesigclsd1s = input_hist.Clone()
    sigclsd1s = triwsmooth(tree , 'StatTools::GetSigma(clsd1s):'+xystr, "sigclsd1s" , "One-sided significalce of expected CLs (-1 sigma)", "clsd1s>=0", clonesigclsd1s)
    #sigclsd1s = triwsmooth(tree , 'TMath::NormQuantile(1-clsd1s):'+xystr, "sigclsd1s" , "One-sided significalce of expected CLs (-1 sigma)", "clsd1s>=0", clonesigclsd1s)

    if sigclsd1s != 0:
        sigclsd1s.Write()
    else:
        print "Cannot make smoothed significance histogram. Exit."

    # # upper limit * cross section plots
    # cloneupperlimit = input_hist.Clone()
    # UpperLimit = triwsmooth(tree, 'upperLimit:'+xystr, "upperLimit" , "upperlimit", "1", cloneupperlimit)

    # if UpperLimit != 0:
    #     UpperLimit.Write()
    # else:
    #     print "Cannot make smoothed significance histogram. Exit."

    # clonexsec = input_hist.Clone()
    # xsec = triwsmooth(tree, 'xsec:'+xystr, "xsec" , "xsec","1", clonexsec)

    # if xsec != 0:
    #     xsec.Write()
    # else:
    #     print "Cannot make smoothed significance histogram. Exit."

    # cloneexcludedXsec = input_hist.Clone()
    # excludedXsec = triwsmooth(tree, 'excludedXsec:'+xystr, "excludedXsec" , "excludedXsec", "1", cloneexcludedXsec)

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
    print '             plot_exclusion.py --contour --sr SR [path]'
    print '             plot_exclusion.py --plot --sr SR [path]'


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('paths', nargs='+', help='path to workspace')
    parser.add_argument("--sr", dest='region', help="Signal Region(s)")
    parser.add_argument('-o', '--output', default='.', help='Output directory for the plots')

    parser.add_argument('--combine', action='store_true', help='Combine hypotest files')

    parser.add_argument('--list', action="store_true", help='Produce the inputs for the plots')
    parser.add_argument('--contour', action="store_true", help='Produce the inputs for the plots')

    parser.add_argument('--plot', action="store_true", dest='plot', help='Make the plot')
    parser.add_argument('--save', help='Save limit contours graphs to rootfile')

    parser.add_argument('--nosigxs', dest='sig_xs_syst', action='store_false')

    # extra text
    parser.add_argument('--bestSR', action='store_true')
    parser.add_argument('--obsCLs', action='store_true')
    parser.add_argument('--expCLs', action='store_true')
    parser.add_argument('--nEvts', action='store_true')
    parser.add_argument('--xsUL', action='store_true')


    global args

    try:
        args = parser.parse_args()
    except:
        print_common_usage()
        raise

    if not (args.combine or args.list or args.contour or args.plot):
        print_common_usage()


    if not args.output.endswith('/'):
        args.output = args.output + '/'

    global min_x, max_x, min_y, max_y

    min_y = 147
    max_y = 2050
    min_x = 1146
    max_x = 2050

    set_default_style()

    # Combine hypotest files in one: take last path as output
    if args.combine:
        inpaths = args.paths[:-1]
        outpath = args.paths[-1]

        if len(args.region.split(',')) != len(inpaths):
            print 'error'
            sys.exit()

        combine_hypotest_files(inpaths, outpath, args.sig_xs_syst)
        sys.exit()

    # Create input files
    if args.list:

        if len(args.paths) > 1:
            parser.print_usage()
            sys.exit()

        create_listfiles(args.paths[0], args.region, args.sig_xs_syst)

    if args.contour:

        if len(args.paths) > 1:
            parser.print_usage()
            sys.exit()

        create_contourhists(args.paths[0], args.region, args.sig_xs_syst)

    if args.plot:
        plot_exclusion(args.paths[0], args.region, args.output, args.sig_xs_syst)
