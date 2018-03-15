import ROOT
from array import array

ROOT.gROOT.SetBatch(1)

from rootutils import *
from statutils import *

import style

# Gauginos labels
n1_text = '#tilde{#chi} #kern[-0.8]{#lower[0.8]{#scale[0.6]{1}}} #kern[-1.8]{#lower[-0.6]{#scale[0.6]{0}}}'
n2_text = '#tilde{#chi} #kern[-0.8]{#lower[0.8]{#scale[0.6]{2}}} #kern[-1.8]{#lower[-0.6]{#scale[0.6]{0}}}'
n3_text = '#tilde{#chi} #kern[-0.8]{#lower[0.8]{#scale[0.6]{3}}} #kern[-1.8]{#lower[-0.6]{#scale[0.6]{0}}}'
c1_text = '#tilde{#chi} #kern[-0.8]{#lower[0.8]{#scale[0.6]{1}}} #kern[-1.8]{#lower[-0.6]{#scale[0.6]{#pm}}}'
mn1_text = 'm_{#tilde{#chi} #kern[-0.8]{#lower[0.8]{#scale[0.6]{1}}} #kern[-1.41]{#lower[-0.6]{#scale[0.6]{0}}}}'

# Grid plot size
glmin = 1200
glmax = 2400 #2400
n1min = 147
n1max = 2400 #2400


def draw_box(x, y, size=1, color='blue'):
    y1 = y
    y2 = y + size
    x1 = x
    x2 = x + size

    box = ROOT.TBox(x1, y1, x2, y2)
    box.SetFillColor(get_color(color))
    ROOT.SetOwnership(box, False)
    box.Draw()


def draw_boxlegend(x, y, color, text):

    box = ROOT.TBox(x, y+2, x+30, y+28)
    box.SetFillColor(get_color(color))

    label = ROOT.TLatex(x+40, y, text)
    label.SetTextSize(0.025)

    ROOT.SetOwnership(box, False)
    ROOT.SetOwnership(label, False)

    box.Draw()
    label.Draw()


def draw_boxpie(m3, mu, *brs):

    y1 = mu
    y2 = mu + 20

    colors = ['purple', 'blue', 'green', 'orange', 'pink']

    x2 = m3
    for i, br in enumerate(brs):
        x1 = x2 + 0.001
        x2 = x1 + round(br*25,1)

        box = ROOT.TBox(x1, y1, x2, y2)
        box.SetFillColor(get_color(colors[i]))
        ROOT.SetOwnership(box, False)
        box.Draw()


def draw_grid_frame(xsize=800, ysize=600, xmin=glmin, xmax=glmax, ymin=n1min, ymax=n1max):

    canvas = ROOT.TCanvas('', '', xsize, ysize)
    canvas.SetTickx(0)
    canvas.SetTicky(0)

    ROOT.SetOwnership(canvas, False)

    nx = (xmax - xmin) / 25
    ny = (ymax - ymin) / 25

    dx = 25
    dy = 25

    frame = ROOT.TH2F('h2', 'h2', nx, xmin, xmax, ny, ymin, ymax)
    ROOT.SetOwnership(frame, False)
    frame.SetTitle('')

    canvas.SetTicks()
    canvas.SetLeftMargin  (0.10)
    canvas.SetBottomMargin(0.09)
    canvas.SetRightMargin (0.05)
    canvas.SetTopMargin   (0.05)

    frame.SetLabelOffset(0.012, "X") 
    frame.SetLabelOffset(0.012, "Y") 
    frame.SetXTitle('m_{#tilde{g}} [GeV]')
    frame.SetYTitle('%s [GeV]' % mn1_text)
    frame.GetXaxis().SetTitleSize(0.035)
    frame.GetYaxis().SetTitleSize(0.035)
    frame.GetXaxis().SetLabelSize(0.035)
    frame.GetYaxis().SetLabelSize(0.035)
    frame.GetZaxis().SetLabelSize(0.02)
    frame.GetXaxis().SetTitleOffset(1.2)
    frame.GetYaxis().SetTitleOffset(1.4)

    frame.GetXaxis().SetNdivisions(520)
    frame.GetYaxis().SetNdivisions(510)

    frame.Draw("hist")
    ROOT.gROOT.ForceStyle()

    fl = ROOT.TLine(xmin, xmin, xmax, xmax)
    ROOT.SetOwnership(fl, False)
    fl.SetLineStyle(2)
    fl.SetLineColor(ROOT.kGray+2)
    fl.Draw()

    flabel = ROOT.TLatex(xmax-420, ymax-350, '%s > m_{#tilde{g}} forbidden' % mn1_text)
    ROOT.SetOwnership(flabel, False)
    flabel.SetTextSize(0.025)
    flabel.SetTextColor(ROOT.kGray+2)
    flabel.SetTextAngle(20)
    flabel.Draw()

    canvas.RedrawAxis()

    return canvas


def grid_histogram(name):

    gl_bins = (glmax - glmin) / 50 #25
    n1_bins = (n1max - n1min) / 50 #25

    hist = ROOT.TH2F(name, name, gl_bins, glmin, glmax, n1_bins, n1min, n1max)

    hist.SetDirectory(0)
    ROOT.SetOwnership(hist, False)

    return hist


def draw_ratio_lines(xmin, xmax):

    line0 = ROOT.TLine(xmin, 1., xmax, 1.)
    line1 = ROOT.TLine(xmin, 0.5,xmax, 0.5)
    line2 = ROOT.TLine(xmin, 1.5,xmax, 1.5)
    line3 = ROOT.TLine(xmin, 2.0,xmax, 2.0)
    
    ROOT.SetOwnership(line0, False)
    ROOT.SetOwnership(line1, False)
    ROOT.SetOwnership(line2, False)
    ROOT.SetOwnership(line3, False)

    line0.SetLineWidth(1)
    line0.SetLineStyle(2)
    line1.SetLineStyle(3)
    line2.SetLineStyle(3)
    line3.SetLineStyle(3)

    line0.Draw()
    line1.Draw()
    line2.Draw()
    line3.Draw()

def save_with_mathtext(can, outname):
    can.Print(plotname+'.eps')
    cmd = 'eps2eps {plotname}.eps {plotname}_.eps && epstopdf {plotname}_.eps --outfile {plotname}.pdf && rm {plotname}.eps {plotname}_.eps'.format(plotname=outname)
    os.system(cmd)

def fix_output_name(name):
    name = name.replace(':', '_').replace('[','').replace(']', '').replace('(', '').replace(')','')
    return name 


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
            big_label=False,
            extensions=['pdf',],
            region_line=None):

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

    if not logy:
        logy = False
    else:
        logy = conf.logy

    logx = conf.logx

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
        cup.SetLeftMargin(cup.GetLeftMargin())
        cup.SetTickx()
        cup.SetTicky()
        cdown.SetTickx()
        cdown.SetTicky()
        cdown.SetRightMargin(0.05)
        cdown.SetTopMargin(0.0054)
        cdown.SetLeftMargin(cdown.GetLeftMargin())
        cdown.SetBottomMargin(cdown.GetBottomMargin()*1.1)
        cdown.SetFillColor(ROOT.kWhite)
        cup.Draw()
        cdown.Draw()

        if logy and conf.logy:
            cup.SetLogy()
        if logx:
            cup.SetLogx()
            cdown.SetLogx()

        cup.SetTopMargin(0.08)
        cdown.SetBottomMargin(0.35)

        up_size = calc_size(cup)
        dn_size = calc_size(cdown)

    else:
        if logy: ## conf.logy:
            can.SetLogy()
        if logx:
            can.SetLogx()

        can.SetTicks(1, 1)
        can.SetLeftMargin(0.12)
        can.SetBottomMargin(0.1)
        can.SetRightMargin(0.04)
        can.SetTopMargin(0.04)
        
        up_size = calc_size(can)
        dn_size = calc_size(can) 

    if big_label:
        up_size *= 1.2
        dn_size *= 1.2 

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

    # bkg stack
    if bkg:
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

        sm_total = sm_stack.GetStack().Last().Clone('sm_total')
        sm_total_stat = sm_total.Clone()

        # sm_total = None
        # for h in bkg.itervalues():
        #     if sm_total is None:
        #         sm_total = h.Clone('sm_total')
        #     else:
        #         sm_total.Add(h, 1)


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
            

    # legend
    legxmin, legxmax = 0.6, 0.88
    legymin, legymax = 0.6, 0.88
    if do_ratio:
        legymin = 0.64
        legymax = 0.88

        if legpos == 'left' or legpos == 'top':
            legxmin = 0.20
            legxmax = 0.53
        elif legpos == 'right':
            legxmin = 0.53
            legxmax = 0.92
    else:
        legymin = 0.80
        legymax = 0.94

        if legpos == 'left' or legpos == 'top':
            legxmin = 0.15
            legxmax = 0.53
        elif legpos == 'right':
            legxmin = 0.65
            legxmax = 0.92

    legend1 = legend(legxmin, legymin, legxmax, legymax, columns=2)
    legend1.SetTextFont(42)
    legend1.SetTextSize(legend1.GetTextSize()*0.8)
    if signal:
        if legpos == 'top':
            if data:
                legend2 = legend(legxmax+0.02, legymin+0.1, legxmax+0.39, legymax)
            else:
                legend2 = legend(legxmax+0.02, legymin, legxmax+0.39, legymax)
        else:
            if data:
                legend2 = legend(legxmin-0.01, legymin-.15, legxmax-0.01, legymin -.01)
            else:
                legend2 = legend(legxmin-0.01, legymin-.20, legxmax-0.01, legymin -.01)

        legend2.SetTextFont(42)
        legend2.SetTextSize(legend1.GetTextSize())

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

    if logy:
        chist.SetMinimum(0.01)

        ymax = chist.GetMaximum()
        if 'dphi' in variable:
            chist.SetMaximum(ymax*1000)
        else:
            chist.SetMaximum(ymax*100)
    else:
        if data:
            ymax = max(chist.GetMaximum(), data.GetMaximum())
        elif signal:
            tmpmax = chist.GetMaximum()
            for hsig in signal.itervalues():
                tmpmax = max(tmpmax, hsig.GetMaximum())
            ymax = tmpmax
        else:
            ymax = chist.GetMaximum()

        chist.SetMaximum(ymax*1.4)


    if big_label:
        y_offset = 1.1
        x_offset = 1.
    else:
        y_offset = 0.9
        x_offset = 1.

    # x-axis
    if do_ratio:
        chist.GetXaxis().SetLabelSize(0.)
        chist.GetXaxis().SetTitleSize(0.)
    else:
        chist.GetXaxis().SetTitle(xtitle)
        chist.GetXaxis().SetTitleOffset(x_offset)
        chist.GetXaxis().SetLabelSize(up_size)
        chist.GetXaxis().SetTitleSize(up_size)
 
    # y-axis
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
    chist.GetYaxis().SetLabelSize(up_size)
    chist.GetYaxis().SetTitleSize(up_size)
    chist.GetYaxis().SetTitleOffset(y_offset)

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

        if legpos == 'top' and signal:
            t.DrawLatex(0.58, 0.66, data_label)
        else:
            if legpos == 'right':
                t.DrawLatex(0.19, 0.76, data_label)
            else:
                t.DrawLatex(0.60, 0.76, data_label)

    # Region line
    # if region_line is not None:
        
        # xline = float(region_line)
                
    # l = ROOT.TLine(200, 0.01, 200, data.GetMaximum())
    # l.SetLineWidth(2)
    # l.SetLineStyle(2)
    # l.Draw()

    # l2 = ROOT.TArrow(200, data.GetMaximum(), 240, data.GetMaximum())
    # l2.SetLineWidth(2)
    # l2.SetLineStyle(2)
    # l2.Draw()


    ratio_ylabel_size = dn_size
    ratio_ytitle_size = dn_size
    
    ratio_xlabel_size = dn_size
    ratio_xtitle_size = dn_size
    
    if do_ratio and data and bkg and ratio_type == 'significance':

        ratio = data.Clone()

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
        if conf.xmin is not None and conf.xmax is not None:
            ratio.GetXaxis().SetRangeUser(conf.xmin, conf.xmax)
        ratio.GetXaxis().SetLabelSize(ratio_xlabel_size)
        ratio.GetXaxis().SetTitleSize(ratio_xtitle_size)
        ratio.GetXaxis().SetTitleOffset(x_offset)
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
            
            try:
                ratio_y   = y/sm_y
                ratio_eyl = eyl/sm_y
                ratio_eyh = eyh/sm_y
            except:
                ratio_y   = 0.
                ratio_eyl = 0.
                ratio_eyh = 0.

            ratio.SetPoint(b, x, ratio_y)
            ratio.SetPointError(b, exl, exh, ratio_eyl, ratio_eyh)

        # remove the point from the plot if zero
        # for b in xrange(ratio.GetNbinsX()):
        #     if ratio.GetBinContent(b+1) < 0.00001:
        #         ratio.SetBinContent(b+1, -1)

        #ratio = make_poisson_cl_errors(ratio)
        set_style(ratio, msize=1, lwidth=2, color=ROOT.kBlack)

        cdown.cd()
        if conf.xmin is not None and conf.xmax is not None:
            frame = cdown.DrawFrame(conf.xmin, 0., conf.xmax, 2.2)
        else:
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
        frame.GetXaxis().SetTitleOffset(1.1)
        frame.GetXaxis().SetLabelOffset(0.03)
        frame.GetXaxis().SetTickLength(0.06)

        if conf.xmin is not None and conf.xmax is not None:
            ratio.GetXaxis().SetRangeUser(conf.xmin, conf.xmax)

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

        for b in xrange(1,sm_total.GetNbinsX()+1):

            x    = sm_total.GetBinCenter(b)
            xerr = 0.5*sm_total.GetBinWidth(b)

            sm_y = sm_total.GetBinContent(b)

            sm_stat_high = sm_total_stat.GetBinError(b)
            sm_stat_low  = sm_total_stat.GetBinError(b)

            try:
                stat_low  = sm_stat_low/sm_y
            except ZeroDivisionError:
                stat_low = 0.0

            try:
                stat_high = sm_stat_high/sm_y
            except ZeroDivisionError:
                stat_high = 0.0

            err_band_stat.SetPoint(b-1, x, 1.)
            err_band_stat.SetPointError(b-1, xerr, xerr, stat_low, stat_high)


        err_band_stat.SetLineWidth(2)
        err_band_stat.SetMarkerSize(0)
        err_band_stat.SetFillStyle(sm_total_style)
        err_band_stat.SetLineColor(sm_total_color)
        err_band_stat.SetFillColor(sm_total_color)

        if conf.xmin is not None and conf.xmax is not None:
            xmin, xmax = conf.xmin, conf.xmax
        else:
            firstbin = hist.GetXaxis().GetFirst()
            lastbin  = hist.GetXaxis().GetLast()
            xmax     = hist.GetXaxis().GetBinUpEdge(lastbin)
            xmin     = hist.GetXaxis().GetBinLowEdge(firstbin)

        draw_ratio_lines(xmin, xmax)
        err_band_stat.Draw('P2same')
        ratio.Draw('P0Z')


    # S/B significance as a function of cut in plotted variable
    elif do_ratio and signal and bkg:
        cdown.cd()

        names = []
        ratio_z = []
        for name in signal.iterkeys():
            names.append(name)
            ratio_z.append(histogram_equal_to(sm_total))

        # remove the point from the plot if zero
        max_bins = ratio_z[0].GetNbinsX()
        for bx in xrange(1, max_bins+1):

            imin = bx
            imax = max_bins

            b = sm_total.Integral(imin, imax)

            for i, name in enumerate(names):

                s = signal[name].Integral(imin, imax)

                z = get_significance(s, b, 0.3)

                ratio_z[i].SetBinContent(bx, z)

        for i, name in enumerate(names):
            set_style(ratio_z[i], msize=1.2, lwidth=2, lstyle=2, color=style.colors_dict[name])


        # x-axis
        ratio_z[0].GetXaxis().SetTitle(xtitle)
        if conf.xmin is not None and conf.xmax is not None:
            ratio_z[0].GetXaxis().SetRangeUser(conf.xmin, conf.xmax)
        ratio_z[0].GetXaxis().SetLabelSize(ratio_xlabel_size)
        ratio_z[0].GetXaxis().SetTitleSize(ratio_xtitle_size)
        ratio_z[0].GetXaxis().SetTitleOffset(x_offset)
        ratio_z[0].GetXaxis().SetLabelOffset(0.03)
        ratio_z[0].GetXaxis().SetTickLength(0.06)

        # if ratio_z[0].GetXaxis().GetXmax() < 5.:
        #     ratio_z[0].GetXaxis().SetNdivisions(512)
        # else:
        #     ratio_z[0].GetXaxis().SetNdivisions(508)

        # y-axis
        cdown.SetGridy()
        ratio_z[0].GetYaxis().SetTitle('Significance')
        ratio_z[0].GetYaxis().SetLabelSize(ratio_ylabel_size)
        ratio_z[0].GetYaxis().SetTitleSize(ratio_ytitle_size)
        ratio_z[0].GetYaxis().SetNdivisions(508)
        ratio_z[0].GetYaxis().SetTitleOffset(y_offset*0.4)
        ratio_z[0].GetYaxis().SetLabelOffset(0.01)

        zmax = 0
        for ratio in ratio_z:
            if ratio.GetMaximum() > zmax:
                zmax = ratio.GetMaximum()

        ratio_z[0].GetYaxis().SetRangeUser(0, zmax+0.5)
        ratio_z[0].Draw()
        for ratio in ratio_z[1:]:
            ratio.Draw('same')


    # Save plot
    output_name = fix_output_name(plotname)
    for ext in extensions:
        can.SaveAs(output_name+'.'+ext)


def do_plot_2d(plotname, variable, hist, logx=False, logy=False, logz=False,
               zmin=None, zmax=None, xmin=None, xmax=None, ymin=None, ymax=None,
               drawopts='colz', text=None, extensions=['pdf',]):

    if 'text' in drawopts:
        for bx in xrange(hist.GetNbinsX()):
            for by in xrange(hist.GetNbinsY()):
                content = hist.GetBinContent(bx+1, by+1)
                hist.SetBinContent(bx+1, by+1, round(content, 2))

    varx, vary = variable.split(':')

    confx, confy = style.get_plotconf(variable)

    xtitle = confx.xtitle
    ytitle = confy.xtitle

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

    if xmin is not None and xmax is not None:
        hist.GetXaxis().SetRangeUser(xmin, xmax)
    if ymin is not None and ymax is not None:
        hist.GetYaxis().SetRangeUser(ymin, ymax)

    if zmin is not None and zmax is not None:
        hist.SetContour(999)
        hist.GetZaxis().SetRangeUser(zmin, zmax)
        hist.Draw(drawopts)
    else:
        hist.Draw(drawopts)

    if text is not None:
        
        tx, ty, ttext = text

        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextSize(0.035)
        l.SetTextFont(42)
        l.SetTextColor(ROOT.kBlack)
        l.DrawLatex(tx, ty, ttext)

    outname = fix_output_name(plotname)

    can.RedrawAxis()
    can.Update()

    for ext in extensions:
        can.SaveAs(outname+'.'+ext)
        

def do_plot_cmp(plotname, 
                variable, 
                histograms,
                do_ratio=True, 
                ratio_type='ratio',
                ratio_cmp=None,
                ratio_text='Ratio',
                normalize=False,
                logy=True,
                conf=None,
                text='',
                extensions=['pdf',]):
    

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

    if conf is not None:
        pass
    elif variable not in style.plots_conf:
        vartmp = variable[:variable.find('[')]
        conf = style.plots_conf.get(vartmp, style.plots_conf['default'])
    else:
        conf = style.plots_conf.get(variable, style.plots_conf['default'])

    xtitle, ytitle, legpos = conf.xtitle, conf.ytitle, conf.legpos

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

        can.SetTicks()
        can.SetLeftMargin(0.15)
        can.SetBottomMargin(0.1)
        up_size = calc_size(can)
        dn_size = calc_size(can) 


    # add entries to legend
    if do_ratio:
        legymin = 0.60
        legymax = 0.88

        if legpos == 'left':
            legxmin1 = 0.20
            legxmax1 = 0.53
            legxmin2 = 0.55
            legxmax2 = 0.88
        elif legpos == 'right' or legpos == 'top':
            legxmin1 = 0.55
            legxmax1 = 0.88
            legxmin2 = 0.20
            legxmax2 = 0.53
    else:
        legymin = 0.70
        legymax = 0.88

        if legpos == 'left':
            legxmin1 = 0.20
            legxmax1 = 0.53
            legxmin2 = 0.65
            legxmax2 = 0.88
        elif legpos == 'right' or legpos == 'top':
            legxmin2 = 0.20
            legxmax2 = 0.53
            legxmin1 = 0.65
            legxmax1 = 0.88

    if len(histograms) > 5:
        legend1 = legend(legxmin1, legymin, legxmax1, legymax, columns=2)
    else:
        legend1 = legend(legxmin1, legymin, legxmax1, legymax)

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
        chist.SetMinimum(0.01)
    elif chist.GetMaximum() > 100:
        chist.SetMinimum(0.01)
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
    

    if histograms[0][0].lower() == 'data':
        chist.Draw()
    else:
        chist.Draw('hist')
    for (name, hist) in histograms[1:]:
        hist.Draw('hist same')

    if do_ratio:
        cup.RedrawAxis()
    else:
        can.RedrawAxis()


    if text:
        ltext = ROOT.TLatex(0.1, 0.95, text)
        ROOT.SetOwnership(ltext, False)
        ltext.SetNDC()
        ltext.SetTextSize(0.03)
        ltext.SetTextFont(42)
        ltext.SetTextColor(ROOT.kBlack)
        ltext.Draw() 

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

            if ratio_cmp is not None:
                ratio_cmp = ratio_cmp.split(',')
                
                for cmp_str in ratio_cmp:
                    
                    nom, oth = [ int(s)-1 for s in cmp_str.split('-') ]
                    
                    ratio = histograms[oth][1].Clone()
                    ratio.Divide(histograms[nom][1])
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
        if conf.xmin is not None and conf.xmax is not None:
            ratios[0].GetXaxis().SetRangeUser(conf.xmin, conf.xmax)
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
            ratios[0].GetYaxis().SetTitle(ratio_text)
        ratios[0].GetYaxis().CenterTitle()
        ratios[0].GetYaxis().SetLabelSize(ratio_ylabel_size)
        ratios[0].GetYaxis().SetTitleSize(ratio_ytitle_size)
        ratios[0].GetYaxis().SetRangeUser(0, 2.2)
        ratios[0].GetYaxis().SetNdivisions(504)
        ratios[0].GetYaxis().SetTitleOffset(0.3)
        ratios[0].GetYaxis().SetLabelOffset(0.01)

        firstbin = ratios[0].GetXaxis().GetFirst()
        lastbin  = ratios[0].GetXaxis().GetLast()
        xmax     = ratios[0].GetXaxis().GetBinUpEdge(lastbin)
        xmin     = ratios[0].GetXaxis().GetBinLowEdge(firstbin)


        ratios[0].Draw('hist')

        draw_ratio_lines(xmin, xmax)

        for ratio in ratios:
            ratio.Draw('hist same')
            

    for ext in extensions:
        outputname = plotname.replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace(' ', '').replace(',', '')
        can.Print(outputname+'.'+ext)


## Limits
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

def return_contour95(hist_name, file_name):

    file_ = ROOT.TFile(file_name)
    hist  = file_.Get(hist_name)

    hist.SetName(hist_name)
    hist.SetTitle(hist_name)

    hist = fix_and_set_borders(hist, hist_name, hist_name, 0).Clone()

    hist.SetDirectory(0)
    ROOT.SetOwnership(hist, False)

    hist.SetContour(1)
    hist.SetContourLevel(0, ROOT.TMath.NormQuantile(1-0.05))
    hist.SetLineWidth(2)
    hist.SetLineStyle(1)

    return convert_hist_to_graph(hist)




def make_exclusion_band(g_nom, g_up, g_dn):
    '''
    g_nom:  TGraph contour for the nominal expected significance
    g_up :  TGraph contour for the +1sigma uncertainty expected significance
    g_dn :  TGraph contour for the -1sigma uncertainty expected significance
    '''

    nbins   = int(max(g_nom.GetN(), g_up.GetN(), g_dn.GetN()))
    n_nom   = int(g_nom.GetN())
    n_up    = int(g_up.GetN())
    n_dn    = int(g_dn.GetN())
    
    x_nom, y_nom  = [], []
    x_up, y_up    = [], []
    x_dn, y_dn    = [], []

    # fill nominal points
    for i in xrange(n_nom):
        x, y = ROOT.Double(0), ROOT.Double(0)
        g_nom.GetPoint(i, x, y)
        x_nom.append(x)
        y_nom.append(y)

    # check that nominal array has the required number of points
    if n_nom < nbins:
        for i in xrange(n_nom, nbins) :
            x_nom.append(x_nom[n_nom-1])
            y_nom.append(y_nom[n_nom-1])
    
    # fill the up-variation points
    for i in xrange(n_up) :
        x, y = ROOT.Double(0), ROOT.Double(0)
        g_up.GetPoint(i, x, y)
        x_up.append(x)
        y_up.append(y)

    # check that the up array has the required number of points
    if n_up < nbins:
        for i in xrange(n_up, nbins):
            x_up.append(x_up[n_up-1])
            y_up.append(y_up[n_up-1])
    
    # fill the down-variation points
    for i in xrange(n_dn):
        x, y = ROOT.Double(0), ROOT.Double(0)
        g_dn.GetPoint(i, x, y)
        x_dn.append(x)
        y_dn.append(y)

    # check that the down array has the required number of points
    if n_dn < nbins:
        for i in xrange(n_dn, nbins):
            x_dn.append(x_dn[n_dn-1])
            y_dn.append(y_dn[n_dn-1])

    # concatenate the up and down arrays to make a complete
    # array for a single TGraph for the outer bounds of the band
    x = x_up + x_dn
    y = y_up + y_dn

    # make the values into an array of doubles so that the
    # TGraph receives the Double_t* 
    x_nom_arr  = array('d', x_nom)
    y_nom_arr  = array('d', y_nom)
    x_arr      = array('d', x)
    y_arr      = array('d', y)

    gr       = ROOT.TGraph(nbins, x_nom_arr, y_nom_arr)
    gr_shade = ROOT.TGraph(nbins, x_arr, y_arr)
    
    for i in xrange(nbins):
        # set the points for the "upper semi-circle" of the band
        gr_shade.SetPoint(i, x_up[i], y_up[i])
        # set the points for the "lower semi-circle" of the band
        gr_shade.SetPoint(nbins+i, x_dn[nbins-i-1], y_dn[nbins-i-1])

    return gr, gr_shade
