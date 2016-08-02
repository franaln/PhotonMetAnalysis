# lib for plots

import ROOT
ROOT.gROOT.SetBatch(1)

from collections import OrderedDict

from rootutils import *
from statutils import *


# config
import style


def calc_poisson_cl_lower(q, obs):
    """
    Calculate lower confidence limit
    e.g. to calculate the 68% lower limit for 2 observed events:
    calcPoissonCLLower(0.68, 2.)
    """
    ll = 0.
    if obs >= 0.:
        a = (1. - q) / 2. # = 0.025 for 95% confidence interval
        ll = ROOT.TMath.ChisquareQuantile(a, 2.*obs) / 2.

    return ll

def calc_poisson_cl_upper(q, obs):
    """
    Calculate upper confidence limit
    e.g. to calculate the 68% upper limit for 2 observed events:
    calcPoissonCLUpper(0.68, 2.)
    """
    ul = 0.
    if obs >= 0. :
        a = 1. - (1. - q) / 2. # = 0.025 for 95% confidence interval
        ul = ROOT.TMath.ChisquareQuantile(a, 2.* (obs + 1.)) / 2.

    return ul

def make_poisson_cl_errors(hist):

    x_val  = array('f')
    y_val = array('f')
    x_errU = array('f')
    x_errL = array('f')
    y_errU = array('f')
    y_errL = array('f')

    for b in xrange(1, hist.GetNbinsX()+1):
        binEntries = hist.GetBinContent(b)
        if binEntries > 0.:
            binErrUp   = calc_poisson_cl_upper(0.68, binEntries) - binEntries
            binErrLow  = binEntries - calc_poisson_cl_lower(0.68, binEntries)
            x_val.append(hist.GetXaxis().GetBinCenter(b))
            y_val.append(binEntries)
            y_errU.append(binErrUp)
            y_errL.append(binErrLow)
            x_errU.append(hist.GetXaxis().GetBinWidth(b)/2.)
            x_errL.append(hist.GetXaxis().GetBinWidth(b)/2.) 

    if len(x_val) > 0:
        data_graph = ROOT.TGraphAsymmErrors(len(x_val), x_val, y_val, x_errL, x_errU, y_errL, y_errU)
        return data_graph
    else:
        return ROOT.TGraph()


def do_plot(plotname, 
            variable, 
            data={}, bkg={}, signal={}, 
            do_bkg_total=True, 
            do_ratio=True, 
            region_name='',
            ratio_type='', 
            normalize=False,
            do_fit=False,
            logy=True,
            publish=False,
            ):

    if data is None:
        data = {}
    if signal is None:
        signal = {}
    if bkg is None:
        bkg = {}


    labels_dict = style.labels_dict
    atlas_label = style.atlas_label
    data_label  = style.data_label

    if variable not in style.plots_conf:
        vartmp = variable[:variable.find('[')]
        conf = style.plots_conf.get(vartmp, style.plots_conf['default'])
    else:
        conf = style.plots_conf.get(variable, style.plots_conf['default'])

    xtitle, ytitle, legpos = conf.xtitle, conf.ytitle, conf.legpos

    can = canvas(plotname, plotname, 800, 800)
    can.cd()

    def calc_size(pad):
        pad_width = pad.XtoPixel(pad.GetX2())
        pad_height = pad.YtoPixel(pad.GetY1())

        if pad_width < pad_height:
            tsize = 28.6 / pad_width
        else:
            tsize = 28.6 / pad_height
        return tsize

    if do_ratio:

        cup   = ROOT.TPad("u", "u", 0., 0.305, 0.99, 1)
        cdown = ROOT.TPad("d", "d", 0., 0.01, 0.99, 0.295)
        cup.SetRightMargin(0.05)
        cup.SetBottomMargin(0.005)
        cup.SetLeftMargin(cup.GetLeftMargin()*0.9)
        cup.SetTickx()
        cup.SetTicky()
        cdown.SetTickx()
        cdown.SetTicky()
        cdown.SetRightMargin(0.05)
        cdown.SetTopMargin(0.0054)
        cdown.SetLeftMargin(cdown.GetLeftMargin()*0.9)
        cdown.SetFillColor(ROOT.kWhite)
        cup.Draw()
        cdown.Draw()

        if logy and conf.logy:
            cup.SetLogy()

        cup.SetTopMargin(0.08)
        cdown.SetBottomMargin(0.3)

        up_size = calc_size(cup)
        dn_size = calc_size(cdown)

    else:
        if logy and conf.logy:
            can.SetLogy()

        can.SetLeftMargin(0.15)
        up_size = calc_size(can)
        dn_size = calc_size(can) 


    # configure histograms
    if data:
        set_style(data, msize=1, lwidth=2, color=ROOT.kBlack)

    if bkg:
        for name, hist in bkg.iteritems():
            set_style(hist, color=style.colors_dict[name], fill=True)
            hist.SetLineColor(ROOT.kBlack)

    if signal:
        for sig, hist in signal.iteritems():
            set_style(hist, msize=1.2, lwidth=2, lstyle=2, color=style.colors_dict[sig])

    if bkg:

        # create SM stack
        sm_stack = ROOT.THStack()

        def _compare(a, b):
            amax = a.GetMaximum()
            bmax = b.GetMaximum()
            return cmp(int(amax), int(bmax))

        for hist in sorted(bkg.itervalues(), _compare):
            sm_stack.Add(hist)

        # Total background
        sm_total = None
        sm_totalerr = None
        sm_total_style = 3354
        sm_total_color = ROOT.kGray+3
        
        sm_stat_color = ROOT.kGray+1
        sm_syst_color = ROOT.kGray+3

        sm_total = None
        for h in bkg.itervalues():
            if sm_total is None:
                sm_total = histogram_equal_to(h)
            sm_total += h

        sm_total_stat = sm_total.Clone()

        if sm_total is not None:
            sm_total.SetLineWidth(2)
            sm_total.SetLineColor(sm_total_color)
            sm_total.SetFillColor(0)
            sm_total.SetMarkerSize(0)
            
            sm_total_stat.SetFillColor(sm_total_color)
            sm_total_stat.SetLineColor(sm_total_color)
            sm_total_stat.SetFillStyle(sm_total_style)
            sm_total_stat.SetLineWidth(2)
            sm_total_stat.SetMarkerSize(0)
            

    # add entries to legend
    if do_ratio:
        legymin = 0.64
        legymax = 0.88

        if legpos == 'left':
            legxmin = 0.20
            legxmax = 0.53
        elif legpos == 'right':
            legxmin = 0.53
            legxmax = 0.92
    else:
        legymin = 0.80
        legymax = 0.94

        if legpos == 'left':
            legxmin = 0.20
            legxmax = 0.53
        elif legpos == 'right':
            legxmin = 0.65
            legxmax = 0.92

    legend1 = legend(legxmin, legymin, legxmax, legymax, columns=2)
    legend1.SetTextFont(42)
    legend1.SetTextSize(legend1.GetTextSize()*0.8)
    if signal:
        legend2 = legend(legxmin-0.01, legymin-.15, legxmax-0.01, legymin -.01)
        legend2.SetTextFont(42)


    if bkg:
        for name, hist in bkg.iteritems():
            legend1.AddEntry(hist, labels_dict[name], 'f')

        if do_bkg_total and sm_total is not None:
            legend1.AddEntry(sm_total_stat, "SM Total", 'f')
        #legend1.AddEntry(sm_total_all, "stat #oplus syst", 'f')
    
    if data:
        legend1.AddEntry(data, labels_dict['data'], 'pl')

    # we don't want to plot signals in Control Regions
    if 'CR' in region_name:
        signal = {}

    if signal:
        for name, hist in signal.iteritems():
            legend2.AddEntry(hist, labels_dict[name], 'f')

    if do_ratio:
        cup.cd()

    # first histogram to configure (ROOT de mierda)
    if bkg:
        sm_stack.Draw('hist')
        chist = sm_stack
    elif data:
        chist = data
    else:
        for name, hist in signal.iteritems():
            break
        chist = signal[name]

    if conf.xmin is not None and conf.xmax is not None:
        chist.GetXaxis().SetRangeUser(conf.xmin, conf.xmax)

    if chist.GetXaxis().GetXmax() < 5.:
        chist.GetXaxis().SetNdivisions(512)
    else:
        chist.GetXaxis().SetNdivisions(508)

    if do_ratio:
        cup.RedrawAxis()
    else:
        can.RedrawAxis()

    if logy and conf.logy:
        chist.SetMinimum(0.01)

    if logy and conf.logy:
        if 'dphi' in variable: ## or 'phi' in variable or 'eta' or variable:
            chist.SetMaximum(chist.GetMaximum()*100000)
        else:

            ymax = chist.GetMaximum()
            for hist in signal.itervalues():
                if hist.GetMaximum() < ymax:
                    ymax = hist.GetMaximum()

            chist.SetMaximum(ymax*1000)
    else:
        chist.SetMaximum(chist.GetMaximum()*2)

    chist.GetXaxis().SetTitle(xtitle)
    chist.GetXaxis().SetTitleOffset(1.4)
    chist.GetXaxis().SetLabelSize(0.)

    if do_ratio:
        chist.GetXaxis().SetLabelSize(0.)
        chist.GetXaxis().SetTitleSize(0.)
    else:
        chist.GetXaxis().SetLabelSize(up_size)
        chist.GetXaxis().SetTitleSize(up_size)
    chist.GetYaxis().SetLabelSize(up_size)
    chist.GetYaxis().SetTitleSize(up_size)
 
    if 'BIN' in ytitle:
        if bkg:
            width = sm_total.GetBinWidth(1)
        else:
            width = chist.GetBinWidth(1)

        if width > 10:
            ytitle = ytitle.replace('BIN', '{:.0f}'.format(width))
        else:
            ytitle = ytitle.replace('BIN', '{:.2f}'.format(width))

    chist.GetYaxis().SetTitle(ytitle)
    chist.GetYaxis().SetTitleOffset(1.1)

    if data:
        data_graph = make_poisson_cl_errors(data)
        set_style(data_graph, msize=1, lwidth=2, color=ROOT.kBlack)
        data_graph.Draw('P0Z')

    if bkg and sm_total is not None:
        sm_total.Draw("histsame")
        sm_total_stat.Draw("E2same][")

    for h in signal.itervalues():
        h.Draw('histsame')

    if data:
        data_graph.Draw('P0Z') 

    if do_ratio:
        cup.RedrawAxis()
    else:
        can.RedrawAxis()

    legend1.Draw()
    if signal:
        legend2.Draw()

    # ATLAS/data labels
    if data:
        text = style.data_label
        t = ROOT.TLatex(0, 0, text)
        t.SetNDC()
        t.SetTextFont(42)
        t.SetTextSize(0.045)
        t.SetTextColor(ROOT.kBlack)

        if legpos == 'right':
            if publish:
                t.DrawLatex(0.19, 0.84, atlas_label)
            t.DrawLatex(0.19, 0.75, data_label)
        else:
            if publish:
                t.DrawLatex(0.60, 0.84, atlas_label)
            t.DrawLatex(0.60, 0.75, data_label)

    if 'SR' in region_name:
        
        li = ROOT.TLine()
        li.SetLineStyle(2)
        li.SetLineWidth(2)
        li.SetLineColor(ROOT.kBlack)

        ar = ROOT.TArrow(0, 0, 0, 0, 0.008, "|>")
        ar.SetLineWidth(2)
        ar.SetLineColor(ROOT.kBlack)

        rl = ROOT.TLatex()
        rl.SetTextSize(0.038)
        rl.SetTextColor(ROOT.kBlack)

        if variable == 'met_et' and region_name.endswith('L'):
            li.DrawLine(200, 0, 200, 50)
            ar.DrawArrow(200, 10, 225, 10)
            rl.DrawLatex(240, 9, 'SR_{L}')
        elif variable == 'met_et' and region_name.endswith('H'):
            li.DrawLine(400, 0, 400, 100)
            ar.DrawArrow(400, 4, 425, 4)
            rl.DrawLatex(435, 3.5, 'SR_{H}')
        
        if variable == 'meff' and region_name.endswith('L'):
            li.DrawLine(2000, 0, 2000, 70)
            ar.DrawArrow(2000, 10, 2150, 10)
            rl.DrawLatex(2080, 17, 'SR_{L}')
        elif variable == 'meff' and region_name.endswith('H'):
            li.DrawLine(2000, 0, 2000, 70)
            ar.DrawArrow(2000, 6, 2075, 6)
            rl.DrawLatex(2100, 5.5, 'SR_{H}')

    # # else:
    # if '_L' in region_name:
    #     text = region_name.replace('_L', '_{L}')
    # elif '_H' in region_name:
    #     text = region_name.replace('_H', '_{H}')
    
    # t = ROOT.TLatex(0, 0, text)
    # t.SetNDC()
    # t.SetTextColor(ROOT.kBlack)
    # t.SetTextFont(42)
    # t.SetTextSize(0.04)
    # if legpos == 'right':
    #     t.DrawLatex(0.20, 0.64, text)
    # else:
    #     t.DrawLatex(0.6, 0.64, text)

    ratio_ylabel_size = dn_size
    ratio_ytitle_size = dn_size
    
    ratio_xlabel_size = dn_size
    ratio_xtitle_size = dn_size
    
    if do_ratio and data and bkg and ratio_type == 'significance':

        ratio = histogram_equal_to(data)

        cdown.cd()
        ratio.SetTitle('')
        ratio.SetStats(0)
        ratio.SetMarkerStyle(20)
        ratio.SetMarkerSize(1)
        ratio.SetLineWidth(2)
        ratio.SetLineColor(ROOT.kBlack)
        ratio.SetMarkerColor(ROOT.kBlack)
        ratio.SetFillColor(ROOT.kGray)

        # x axis
        ratio.GetXaxis().SetTitle(xtitle)
        if xmin is not None and xmax is not None:
            ratio.GetXaxis().SetRangeUser(xmin, xmax)
        ratio.GetXaxis().SetLabelSize(ratio_xlabel_size)
        ratio.GetXaxis().SetTitleSize(ratio_xtitle_size)
        ratio.GetXaxis().SetTitleOffset(1.2)
        ratio.GetXaxis().SetLabelOffset(0.03)
        ratio.GetXaxis().SetTickLength(0.06)

        if ratio.GetXaxis().GetXmax() < 5.:
            ratio.GetXaxis().SetNdivisions(512)
        else:
            ratio.GetXaxis().SetNdivisions(508)

        # y axis
        ratio.GetYaxis().SetTitle('Significance')
        ratio.GetYaxis().SetLabelSize(ratio_ylabel_size)
        ratio.GetYaxis().SetTitleSize(ratio_ytitle_size)
        ratio.GetYaxis().SetRangeUser(-5, 5)
        ratio.GetYaxis().SetNdivisions(504)
        ratio.GetYaxis().SetTitleOffset(0.5)
        ratio.GetYaxis().SetLabelOffset(0.01)

        for bx in xrange(ratio.GetNbinsX()):

            obs = data.GetBinContent(bx+1)

            if model is None:
                exp = sm_total.GetBinContent(bx+1)
            else:
                x = ratio.GetBinCenter(bx+1)
                if x < model.GetXmin() or x > model.GetXmax():
                    exp = obs
                else:
                    exp = model.Eval(x)
                
            z = poisson_significance(obs, exp)
            ratio.SetBinContent(bx+1, z)

        ratio.Draw('e0')

        firstbin = ratio.GetXaxis().GetFirst()
        lastbin  = ratio.GetXaxis().GetLast()
        xmax     = ratio.GetXaxis().GetBinUpEdge(lastbin)
        xmin     = ratio.GetXaxis().GetBinLowEdge(firstbin)

        lines = [None, None, None]

        lines[0] = ROOT.TLine(xmin,  0., xmax,  0.)
        lines[1] = ROOT.TLine(xmin, -3., xmax, -3.)
        lines[2] = ROOT.TLine(xmin,  3., xmax,  3.)

        lines[0].SetLineWidth(1)
        lines[0].SetLineStyle(2)
        lines[1].SetLineStyle(3)
        lines[2].SetLineStyle(3)

        lines[0].Draw()
        lines[1].Draw()
        lines[2].Draw()
        ratio.Draw('e0 same')

        ratio.GetYaxis().SetLabelSize(0.)

        x = xmin - ratio.GetBinWidth(1) 
        t = ROOT.TLatex()
        t.SetTextSize(0.12)
        t.SetTextAlign(32)
        t.SetTextAngle(0);

        y = ratio.GetYaxis().GetBinCenter(3)
        t.DrawLatex(x, y+0.5, '3')

        y = ratio.GetYaxis().GetBinCenter(-3)
        t.DrawLatex(x, y+0.5, '-3')


    elif do_ratio and data and bkg:

        ratio = data_graph.Clone()
        for b in xrange(ratio.GetN()):
            x = ROOT.Double(0.)
            y = ROOT.Double(0.)
            ratio.GetPoint(b, x, y)

            sm_y = sm_total.GetBinContent(sm_total.FindBin(x))

            exl = ratio.GetErrorXlow(b)
            exh = ratio.GetErrorXhigh(b)

            eyl = ratio.GetErrorYlow(b)
            eyh = ratio.GetErrorYhigh(b)
            
            ratio_y   = y/sm_y
            ratio_eyl = eyl/sm_y
            ratio_eyh = eyh/sm_y

            ratio.SetPoint(b, x, ratio_y)
            ratio.SetPointError(b, exl, exh, ratio_eyl, ratio_eyh)


        # remove the point from the plot if zero
        # for b in xrange(ratio.GetNbinsX()):
        #     if ratio.GetBinContent(b+1) < 0.00001:
        #         ratio.SetBinContent(b+1, -1)

        #ratio = make_poisson_cl_errors(ratio)
        set_style(ratio, msize=1, lwidth=2, color=ROOT.kBlack)

        cdown.cd()
        frame = cdown.DrawFrame(chist.GetXaxis().GetXmin(), 0., chist.GetXaxis().GetXmax(), 2.2)

        ratio.SetTitle('')
        ratio.SetMarkerStyle(20)
        ratio.SetMarkerSize(1)
        ratio.SetLineWidth(2)
        ratio.SetLineColor(ROOT.kBlack)
        ratio.SetMarkerColor(ROOT.kBlack)

        # x axis
        frame.GetXaxis().SetTitle(xtitle)
        frame.GetXaxis().SetLabelSize(ratio_xlabel_size)
        frame.GetXaxis().SetTitleSize(ratio_xtitle_size)
        frame.GetXaxis().SetTitleOffset(1.)
        frame.GetXaxis().SetLabelOffset(0.03)
        frame.GetXaxis().SetTickLength(0.06)

        if frame.GetXaxis().GetXmax() < 5.:
            frame.GetXaxis().SetNdivisions(512)
        else:
            frame.GetXaxis().SetNdivisions(508)

        # y axis
        frame.GetYaxis().SetTitle('Data / SM')
        frame.GetYaxis().CenterTitle()
        frame.GetYaxis().SetLabelSize(ratio_ylabel_size)
        frame.GetYaxis().SetTitleSize(ratio_ytitle_size)
        frame.GetYaxis().SetRangeUser(0, 2.2)
        frame.GetYaxis().SetNdivisions(504)
        frame.GetYaxis().SetTitleOffset(0.35)
        frame.GetYaxis().SetLabelOffset(0.01)

        err_band_stat = ROOT.TGraphAsymmErrors(sm_total.GetNbinsX())

        for bin_ in xrange(sm_total.GetNbinsX()):

            x    = sm_total.GetBinCenter(bin_+1)
            xerr = sm_total.GetBinWidth(bin_+1)/2

            sm_y     = sm_total.GetBinContent(bin_+1)

            sm_stat_high = sm_total_stat.GetBinError(bin_+1)
            sm_stat_low  = sm_total_stat.GetBinError(bin_+1)

            try:
                stat_low  = sm_stat_low/sm_y
            except ZeroDivisionError:
                stat_low = 0.0

            try:
                stat_high = sm_stat_high/sm_y
            except ZeroDivisionError:
                stat_high = 0.0

            err_band_stat.SetPoint(bin_, x, 1.)
            err_band_stat.SetPointError(bin_, xerr, xerr, stat_low, stat_high)


        err_band_stat.SetLineWidth(2)
        err_band_stat.SetMarkerSize(0)
        err_band_stat.SetFillStyle(sm_total_style)
        err_band_stat.SetLineColor(sm_total_color)
        err_band_stat.SetFillColor(sm_total_color)

        # ratio.Draw('P0Z')
        err_band_stat.Draw('P2same')
        ratio.Draw('P0Z')

        firstbin = frame.GetXaxis().GetFirst()
        lastbin  = frame.GetXaxis().GetLast()
        xmax     = frame.GetXaxis().GetBinUpEdge(lastbin)
        xmin     = frame.GetXaxis().GetBinLowEdge(firstbin)

        lines = [
            ROOT.TLine(xmin, 1., xmax, 1.),
            ROOT.TLine(xmin, 0.5,xmax, 0.5),
            ROOT.TLine(xmin, 1.5,xmax, 1.5),
            ROOT.TLine(xmin, 2.0,xmax, 2.0),
            ]

        lines[0].SetLineWidth(1)
        lines[0].SetLineStyle(2)
        lines[1].SetLineStyle(3)
        lines[2].SetLineStyle(3)
        lines[3].SetLineStyle(3)

        for line in lines:
            line.Draw()

    elif do_ratio and signal and bkg:

        names = []
        ratio_z = []
        ratio_e = []
        for name in signal.iterkeys():
            names.append(name)
            ratio_z.append(histogram_equal_to(sm_total))
            ratio_e.append(histogram_equal_to(sm_total))

        # remove the point from the plot if zero
        max_bins = ratio_z[0].GetNbinsX()
        for bin_ in xrange(max_bins):

            if 'rt4' in variable or 'dphi_gamjet' in variable:
                imin = 1
                imax = bin_
            else:
                imin = bin_
                imax = max_bins

            b = sm_total.Integral(imin, imax)
            s0 = signal[name].Integral()

            for i, name in enumerate(names):

                s = signal[name].Integral(imin, imax)

                z = get_significance(s, b)
                eff = s/s0 if s0 > 0 else 0

                ratio_z[i].SetBinContent(bin_, z)
                ratio_e[i].SetBinContent(bin_, eff)

        for i, name in enumerate(names):
            set_style(ratio_z[i], msize=1.2, lwidth=2, lstyle=2, color=style.colors_dict[name])
            set_style(ratio_e[i], msize=1.2, lwidth=2, lstyle=3, color=style.colors_dict[name])


        cdown.cd()

        # x axis
        ratio_z[0].GetXaxis().SetTitle(xtitle)
        if xmin is not None and xmax is not None:
            ratio_z[0].GetXaxis().SetRangeUser(xmin, xmax)
        ratio_z[0].GetXaxis().SetLabelSize(ratio_xlabel_size)
        ratio_z[0].GetXaxis().SetTitleSize(ratio_xtitle_size)
        ratio_z[0].GetXaxis().SetTitleOffset(1.)
        ratio_z[0].GetXaxis().SetLabelOffset(0.03)
        ratio_z[0].GetXaxis().SetTickLength(0.06)

        if ratio_z[0].GetXaxis().GetXmax() < 5.:
            ratio_z[0].GetXaxis().SetNdivisions(512)
        else:
            ratio_z[0].GetXaxis().SetNdivisions(508)

        # y axis
        ratio_z[0].GetYaxis().SetTitle('Significance')
        ratio_z[0].GetYaxis().SetLabelSize(ratio_ylabel_size)
        ratio_z[0].GetYaxis().SetTitleSize(ratio_ytitle_size)
        ratio_z[0].GetYaxis().SetNdivisions(504)
        ratio_z[0].GetYaxis().SetTitleOffset(0.4)
        ratio_z[0].GetYaxis().SetLabelOffset(0.01)

        # ratio_z[0].GetYaxis().SetLabelOffset(99)
        # ratio_z[0].GetYaxis().SetLabelSize(0.)

        zmax = 0
        for ratio in ratio_z:
            if ratio.GetMaximum() > zmax:
                zmax = ratio.GetMaximum()

        ratio_z[0].GetYaxis().SetRangeUser(0, zmax)

        ratio_z[0].Draw()
        for ratio in ratio_z[1:]:
            ratio.Draw('same')

        # emax = 0
        # for ratio in ratio_e:
        #     if ratio.GetMaximum() > emax:
        #         emax = ratio.GetMaximum()

        # for ratio in ratio_e:
        #     ratio.Scale(zmax)
        #     ratio.Draw('same')

        # firstbin = ratio.GetXaxis().GetFirst()
        # lastbin  = ratio.GetXaxis().GetLast()
        # xmax     = ratio.GetXaxis().GetBinUpEdge(lastbin)
        # xmin     = ratio.GetXaxis().GetBinLowEdge(firstbin)

        # axis = ROOT.TGaxis(xmax, 0, xmax, zmax, 0, 1, 510, "+L")
        # axis.SetTitle("Efficiency")
        # axis.SetNdivisions(504)
        # axis.SetLabelSize(ratio_ylabel_size)
        # axis.SetTitleSize(ratio_ytitle_size)
        # axis.SetTitleFont(ratio_z[0].GetYaxis().GetTitleFont())
        # axis.Draw()

        # firstbin = ratio_z[0].GetXaxis().GetFirst()
        # lastbin  = ratio_z[0].GetXaxis().GetLast()
        # xmax     = ratio_z[0].GetXaxis().GetBinUpEdge(lastbin)
        # xmin     = ratio_z[0].GetXaxis().GetBinLowEdge(firstbin)

        # lines = [None, None, None, None, None]
        # lines[0] = ROOT.TLine(xmin, 1., xmax, 1.)
        # lines[1] = ROOT.TLine(xmin, 2., xmax, 2.)
        # lines[2] = ROOT.TLine(xmin, 3., xmax, 3.)
        # lines[3] = ROOT.TLine(xmin, 4., xmax, 4.)
        # lines[4] = ROOT.TLine(xmin, 5., xmax, 5.)

        # lines[0].SetLineStyle(2)
        # lines[1].SetLineStyle(2)
        # lines[2].SetLineStyle(2)
        # lines[3].SetLineStyle(2)
        # lines[4].SetLineStyle(2)

        # for line in lines:
        #     line.Draw()

        # x = ROOT.gPad.GetUxmin() - 0.1*ratio_z[0].GetXaxis().GetBinWidth(1);

        # t = ROOT.TLatex()
        # t.SetTextSize(0.10)
        # t.SetTextAlign(32)
        # t.SetTextAngle(0);
        # for i in xrange(5):
        #     y = ratio_z[0].GetYaxis().GetBinCenter(i+1)
        #     t.DrawLatex(x, y+0.5, '%s' % (i+1))



    # Save 
    # if publish:
    #     can.Print(plotname+'.tex')
    #     can.Print(plotname+'.eps')
    #     cmd = 'eps2eps {plotname}.eps {plotname}_.eps && epstopdf {plotname}_.eps --outfile {plotname}.pdf && rm {plotname}.eps {plotname}_.eps'.format(plotname=plotname)
    #     os.system(cmd)
    #     print '->', plotname+'.pdf'

    # else:
    can.Print(plotname+'.pdf')


def do_plot_2d(plotname, variable, hist, logx=False, logy=False, logz=False,
               zmin=None, zmax=None, options='colz', text=None):

    if 'text' in options:
        for bx in xrange(hist.GetNbinsX()):
            for by in xrange(hist.GetNbinsY()):
                content = hist.GetBinContent(bx+1, by+1)
                hist.SetBinContent(bx+1, by+1, round(content, 2))

    varx, vary = variable.split(':')

    if '[' in varx:
        vartmp = varx[:varx.find('[')]
        confx = style.plots_conf.get(vartmp)
    else:
        confx = style.plots_conf.get(varx)

    if '[' in vary:
        vartmp = vary[:vary.find('[')]
        confy = style.plots_conf.get(vartmp)
    else:
        confy = style.plots_conf.get(vary)

    xtitle = confx[0]
    ytitle = confy[0]

    hist.GetXaxis().SetTitle(xtitle)
    hist.GetYaxis().SetTitle(ytitle)

    hist.GetXaxis().SetLabelSize(0.04)
    hist.GetXaxis().SetTitleSize(0.04)
    hist.GetYaxis().SetLabelSize(0.04)
    hist.GetYaxis().SetTitleSize(0.04)
    hist.GetZaxis().SetLabelSize(0.04)

    hist.SetStats(0)
    hist.SetTitle('')
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleOffset(1.5)
    hist.GetZaxis().SetTitleOffset(1.2)


    can = canvas(plotname, plotname, 800, 800)
    can.cd()
    
    if logx:
        can.SetLogx()
    if logy:
        can.SetLogy()
    if logz:
        can.SetLogz()

    can.SetRightMargin(0.15)
    can.SetLeftMargin(0.14)
    can.SetBottomMargin(0.14)
    can.SetFillColor(ROOT.kWhite)

    if zmin is not None and zmax is not None:
        hist.SetContour(999)
        hist.GetZaxis().SetRangeUser(zmin, zmax)
        hist.Draw(options)
    else:
        hist.Draw(options)

    if text is not None:
        
        tx, ty, ttext = text

        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextSize(0.035)
        l.SetTextColor(ROOT.kBlack)
        l.DrawLatex(tx, ty, ttext)

    outname = plotname.replace(':', '_').replace('[','').replace(']', '')
    
    can.SaveAs(outname+'.pdf')


def do_plot_cmp(plotname, 
                variable, 
                histograms,
                do_ratio=True, 
                ratio_type='ratio',
                normalize=False,
                logy=True):
    

    if isinstance(histograms, dict):
        tmp = ()
        for name, hist in histograms:
            tmp.append((name, hist))

        histograms = tmp

    if normalize:
        hist0norm = histograms[0][1].Integral()
        for (name, hist) in histograms[1:]:
            try:
                hist.Scale(hist0norm/hist.Integral())
            except ZeroDivisionError:
                pass


    if variable not in style.plots_conf:
        vartmp = variable[:variable.find('[')]
        conf = style.plots_conf.get(vartmp, style.plots_conf['default'])
    else:
        conf = style.plots_conf.get(variable, style.plots_conf['default'])

    xtitle, ytitle, legpos = conf.xtitle, conf.ytitle, conf.legpos

    # if len(conf) > 4:
    #     xmin, xmax = conf[3], conf[4]
    # else:
    #     xmin, xmax = None, None

    can = canvas(plotname, plotname, 800, 800)
    can.cd()

    can.SetLeftMargin(0.2)

    def calc_size(pad):
        pad_width = pad.XtoPixel(pad.GetX2())
        pad_height = pad.YtoPixel(pad.GetY1())

        if pad_width < pad_height:
            tsize = 28.6 / pad_width
        else:
            tsize = 28.6 / pad_height
        return tsize

    if do_ratio:

        cup   = ROOT.TPad("u", "u", 0., 0.305, 0.99, 1)
        cdown = ROOT.TPad("d", "d", 0., 0.01, 0.99, 0.295)
        cup.SetRightMargin(0.05)
        cup.SetBottomMargin(0.005)

        cup.SetTickx()
        cup.SetTicky()
        cdown.SetTickx()
        cdown.SetTicky()
        cdown.SetRightMargin(0.05)
        cdown.SetBottomMargin(0.3)
        cdown.SetTopMargin(0.0054)
        cdown.SetFillColor(ROOT.kWhite)
        cup.Draw()
        cdown.Draw()

        if logy and conf.logy:
            cup.SetLogy()

        cup.SetTopMargin(0.08)
        cdown.SetBottomMargin(0.4)

        up_size = calc_size(cup)
        dn_size = calc_size(cdown)

    else:
        if logy and conf.logy:
            can.SetLogy()

        can.SetLeftMargin(0.15)
        up_size = calc_size(can)
        dn_size = calc_size(can) 

    # configure histograms
    # for (name, hist) in histograms:
    #     try:
    #         set_style(hist, color=colors_dict[name], fill=True)
    #         hist.SetLineColor(ROOT.kBlack)
    #     except:
    #         pass

    # add entries to legend
    if do_ratio:
        legymin = 0.60
        legymax = 0.88

        if legpos == 'left':
            legxmin = 0.20
            legxmax = 0.53
        elif legpos == 'right':
            legxmin = 0.55
            legxmax = 0.88
    else:
        legymin = 0.80
        legymax = 0.94

        if legpos == 'left':
            legxmin = 0.20
            legxmax = 0.53
        elif legpos == 'right':
            legxmin = 0.65
            legxmax = 0.92

    if len(histograms) > 5:
        legend1 = legend(legxmin, legymin, legxmax, legymax, columns=2)
    else:
        legend1 = legend(legxmin, legymin, legxmax, legymax)

    for (name, hist) in histograms:
        legend1.AddEntry(hist, style.labels_dict.get(name, name))

    if do_ratio:
        cup.cd()

    # first histogram to configure (ROOT de mierda)
    (cname, chist) = histograms[0]

    if conf.xmin is not None and conf.xmax is not None:
        chist.GetXaxis().SetRangeUser(conf.xmin, conf.xmax)

    if chist.GetXaxis().GetXmax() < 5.:
        chist.GetXaxis().SetNdivisions(512)
    else:
        chist.GetXaxis().SetNdivisions(508)

    if do_ratio:
        cup.RedrawAxis()
    else:
        can.RedrawAxis()

    if chist.GetMaximum() < 10:
        chist.SetMinimum(0.0001)
    else:
        chist.SetMinimum(0.01)

    if logy and conf.logy:
        if 'dphi' in variable:
            chist.SetMaximum(chist.GetMaximum()*100000)
        else:
            chist.SetMaximum(chist.GetMaximum()*100)
    else:
        chist.SetMaximum(chist.GetMaximum()*2)

    chist.GetXaxis().SetTitle(xtitle)
    chist.GetXaxis().SetTitleOffset(1.3)
    chist.GetXaxis().SetLabelSize(0.)

    chist.GetXaxis().SetLabelSize(up_size)
    chist.GetXaxis().SetTitleSize(up_size)
    chist.GetYaxis().SetLabelSize(up_size)
    chist.GetYaxis().SetTitleSize(up_size)
 
    if 'BIN' in ytitle:
        width = chist.GetBinWidth(1)

        if width > 10:
            ytitle = ytitle.replace('BIN', '{:.0f}'.format(width))
        else:
            ytitle = ytitle.replace('BIN', '{:.2f}'.format(width))

    chist.GetYaxis().SetTitle(ytitle)
    chist.GetYaxis().SetTitleOffset(1.)
    

    chist.Draw('hist')
    for (name, hist) in histograms[1:]:
        hist.Draw('hist same')

    if do_ratio:
        cup.RedrawAxis()
    else:
        can.RedrawAxis()

    legend1.Draw()

    ratio_ylabel_size = dn_size
    ratio_ytitle_size = dn_size
    
    ratio_xlabel_size = dn_size
    ratio_xtitle_size = dn_size
    
    if do_ratio and len(histograms) > 1:

        ratios = []
        if ratio_type == 'diff':

            reference = histograms[0][1]

            ratios = []
            for (name, hist) in histograms[1:]:

                ratio = hist.Clone()
                ratio.Add(reference, -1)
                ratio.Divide(reference)

                ratios.append(ratio)

        else:

            for (name, hist) in histograms[1:]:
                ratio = hist.Clone()
                ratio.Divide(histograms[0][1])

                ratios.append(ratio)

        cdown.cd()
        ratios[0].SetTitle('')
        ratios[0].SetStats(0)

        # x axis
        ratios[0].GetXaxis().SetTitle(xtitle)
        if xmin is not None and xmax is not None:
            ratios[0].GetXaxis().SetRangeUser(xmin, xmax)
        ratios[0].GetXaxis().SetLabelSize(ratio_xlabel_size)
        ratios[0].GetXaxis().SetTitleSize(ratio_xtitle_size)
        ratios[0].GetXaxis().SetTitleOffset(1.)
        ratios[0].GetXaxis().SetLabelOffset(0.03)
        ratios[0].GetXaxis().SetTickLength(0.06)

        if ratios[0].GetXaxis().GetXmax() < 5.:
            ratios[0].GetXaxis().SetNdivisions(512)
        else:
            ratios[0].GetXaxis().SetNdivisions(508)

        # y axis
        if ratio_type == 'diff':
            ratios[0].GetYaxis().SetTitle('Rel. diff.')
        else:
            ratios[0].GetYaxis().SetTitle('Ratio')
        ratios[0].GetYaxis().CenterTitle()
        ratios[0].GetYaxis().SetLabelSize(ratio_ylabel_size)
        ratios[0].GetYaxis().SetTitleSize(ratio_ytitle_size)
        ratios[0].GetYaxis().SetRangeUser(0, 2.2)
        ratios[0].GetYaxis().SetNdivisions(504)
        ratios[0].GetYaxis().SetTitleOffset(0.3)
        ratios[0].GetYaxis().SetLabelOffset(0.01)

        ratios[0].Draw()
        for ratio in ratios[1:]:
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


    can.Print(plotname+'.pdf')
