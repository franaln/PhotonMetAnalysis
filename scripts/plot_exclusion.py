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
from rootutils import *
from drawutils import *
from signalgrid import mg_gg_grid

ROOT.gROOT.SetBatch(1)
ROOT.gSystem.Load('%s/lib/libSusyFitter.so' % os.getenv('HISTFITTER'))
ROOT.gInterpreter.ProcessLine('#include "{0}/src/DrawUtils.h" '.format(os.getenv('HISTFITTER')))
ROOT.gInterpreter.ProcessLine('#include "{0}/src/StatTools.h" '.format(os.getenv('HISTFITTER')))


def plot_exclusion(path, region, outdir):

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
    graph_obs = return_contour95('sigp1clsf', file_name)
    if sig_xs_syst:
        graph_obs_dn  = return_contour95('sigp1clsf', file_name_low)
        graph_obs_up = return_contour95('sigp1clsf', file_name_high)

    graph_exp_nom = return_contour95('sigp1expclsf', file_name)
    graph_exp_dn  = return_contour95('sigclsu1s',    file_name)
    graph_exp_up  = return_contour95('sigclsd1s',    file_name)

    graph_exp, graph_exp_shade = make_exclusion_band(graph_exp_nom, graph_exp_dn, graph_exp_up)


    # Style
    c_yellow = ROOT.TColor.GetColor('#ffe938')
    c_red    = ROOT.TColor.GetColor('#aa0000')
    c_blue   = ROOT.TColor.GetColor('#28373c')

    ## expected 
    set_style(graph_exp,       color=c_blue, lwidth=2)
    set_style(graph_exp_shade, color=c_yellow, fstyle=1001)

    ## observed
    set_style(graph_obs, color=c_red, lwidth=3)
    if sig_xs_syst:
        set_style(graph_obs_dn, color=c_red, lwidth=2)
        set_style(graph_obs_up, color=c_red, lwidth=2)


    frame = draw_grid_frame(xmin=1340, xmax=2550, ymin=147, ymax=2550) 

    # Create the text in the plot
    # DATA info
    leg1 = ROOT.TLatex()
    leg1.SetNDC()
    leg1.SetTextSize(0.035)
    leg1.SetTextColor(1)
    # if args.datalabel is not None:
    #     leg1.DrawLatex(0.15, 0.7, args.datalabel)
    # else:
    #     leg1.DrawLatex(0.15, 0.7, style.data_label)

    # if style.atlas_label:
    #     leg1.SetTextSize(0.04)
    #     leg1.DrawLatex(1810, 230, style.atlas_label)

    # Signal Regions label
    leg3 = ROOT.TLatex()
    leg3.SetNDC()
    leg3.SetTextSize(0.035)
    leg3.SetTextColor(1)
    leg3.SetTextFont(42)

    # region_text = region
    # if 'SRL,SRH' in region_text or 'SRiL,SRiH' in region_text:
    #     region_text = region_text = 'SR_{L} and SR_{H}'
    # elif 'SRL' in region_text or 'SRiL' in region_text:
    #     region_text = 'SR_{L}'
    # elif 'SRH' in region_text or 'SRiH' in region_text:
    #     region_text = 'SR_{H}'

    # leg3.DrawLatex(0.15, 0.63, region_text)

    # Legend
    leg  = ROOT.TLegend(0.15, 0.77, 0.6, 0.92)
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

    leg2 = ROOT.TLatex()
    leg2.SetNDC()
    leg2.SetTextSize(0.03)
    leg2.SetTextColor(1)
    leg2.DrawLatex(0.17, 0.75, "All limits at 95% CL")


    # # Load ICHEP
    # f = ROOT.TFile.Open(os.environ['SUSY_ANALYSIS'] + '/data/limit_run2_gln1_ichep2016.root')
    # limit_ichep    = f.Get('clsf_obs')
    # leg.AddEntry(limit_ichep, 'Observed limit, ATLAS 13 TeV 13.3 fb^{-1} (ICHEP 2016)', 'F')


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
    ## expected
    graph_exp.Draw("same l")
    graph_exp_shade.Draw("same f")

    ## observed
    if not args.onlyexp:
        graph_obs.Draw('same l')
        if sig_xs_syst:
            graph_obs_dn.Draw("same l")
            graph_obs_up.Draw("same l")


    # # plot Run 1 limit
    # # if ',' in region:
    # limit_ichep.SetLineWidth(2)
    # limit_ichep.SetLineColor(get_color('#b9b7b7'))
    # limit_ichep.SetFillColor(get_color('#c6c4c4'))
    # limit_ichep.Draw('f same')
    # limit_ichep.Draw('l same')


    # Redraw axis and update frame
    frame.RedrawAxis()
    ROOT.gPad.Update()


    output_tag = ''

    if args.obscls or args.expcls:

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


        lp.SetTextSize(0.02)
        lp.SetTextColor(ROOT.kGray+3)
        lp.DrawLatex(1260, 1950, "#bullet     Current grid")
        lp.SetTextColor(ROOT.kRed-4)
        lp.DrawLatex(1260, 1850, "#times    Extension")
    

    frame.SaveAs(path+'/limit_plot_%s%s.pdf' % (region.replace(',', '_'), output_tag))


    # Save contours
    outname = path + '/limit_contour_%s' % region.replace(',', '_') + '.root'

    outfile = ROOT.TFile(outname, 'recreate')
    outfile.cd()

    ## observed
    graph_obs.Write('cls_obs')
    if sig_xs_syst:
        graph_obs_up.Write("cls_obs_up")
        graph_obs_dn.Write("cls_obs_dn")

    ## expected
    graph_exp_nom.Write('cls_exp')
    if sig_xs_syst:
        graph_exp_dn.Write('cls_exp_dn')
        graph_exp_up.Write('cls_exp_up')

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

    print 'Combining SRs: %s' % args.region
    print 'Input paths:'
    for ip in inpaths:
        print ip
    print 'Output path:'
    print outpath

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

        if sig_xs_syst:
            lines_nom = open(path+'/Output_fixSigXSecNominal_hypotest__1_harvest_list').read().split('\n')
            lines_dn  = open(path+'/Output_fixSigXSecDown_hypotest__1_harvest_list').read().split('\n')
            lines_up  = open(path+'/Output_fixSigXSecUp_hypotest__1_harvest_list').read().split('\n')
        else:
            lines_nom = open(path+'/Output_hypotest__1_harvest_list').read().split('\n')

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

                print 'copying list for (%i, %i) %s CLs = %.6f' % (m3, mu, region, cls)
                    
            else:

                if cls < cls_dict[(m3, mu)]:

                    print 'changing list for (%i, %i) %s CLs = %.6f (old = %.6f)' % (m3, mu, region, cls, cls_dict[(m3, mu)]) 
                    
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

        format = "hypo_GGM_GG_bhmix_%f_%f"
        interpretation = "m3:mu"

        outputfile = ROOT.CollectAndWriteHypoTestResults(inputfile, format, interpretation, '1', True, output_dir)

        os.system('GenerateTreeDescriptionFromJSON.py -f %s -o %s' % (jsonfile,listfile))

    else:
        for syst in ['Nominal', 'Up', 'Down']:

            inputfile  = path + '/Output_fixSigXSec%s_hypotest.root' % syst
            output_dir = path

            jsonfile = inputfile.replace('hypotest.root', 'hypotest__1_harvest_list.json')
            listfile = jsonfile.replace('.json', '')

            format = "hypo_GGM_GG_bhmix_%f_%f"
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
    newfile = ROOT.TFile(textfile+'_masses.root', "recreate");
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
            mgl[0], mn1[0] = mg_gg_grid[(int(row.m3), int(row.mu))]
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

    # get the harvested tree
    tree = harvesttree(textfile)

    hack_tree(textfile, tree)

    f = ROOT.TFile(textfile+'_masses.root')
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
    print '             plot_exclusion.py --combine [output path] [input path 1] [input path 2] ...'
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
    last_path = args.paths[-1]

    global sig_xs_syst
    sig_xs_syst = False
    if os.path.exists('%s/Output_fixSigXSecNominal_hypotest.root' % last_path):
        sig_xs_syst = True

    if os.path.exists('%s/Output_fixSigXSecNominal_hypotest__1_harvest_list' % last_path):
        sig_xs_syst = True


    # Combine hypotest files in one: take last path as output
    if args.combine:
        outpath = args.paths[0]
        inpaths = args.paths[1:]

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

        create_listfiles(args.paths[0], args.region)

    if args.cont:
        if len(args.paths) > 1:
            parser.print_usage()
            sys.exit()

        create_contourhists(args.paths[0], args.region)

    if args.plot:
        plot_exclusion(args.paths[0], args.region, args.output)

