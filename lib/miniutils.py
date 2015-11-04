# single photon analysis
# mini utils

import os
import re
import ROOT
from rootutils import RootFile, Value, histogram, histogram_equal_to
from binning import get_binning
from xs import gg_xs, ewk_xs
from xs_dict import xs_dict
import samples

MiniDir  = '/raid/falonso/mini2/'
TruthDir =  '/afs/cern.ch/work/f/falonso/Susy/Run2/PhotonMetNtuple/output_truth_final/'
version = '3c'
version_25ns = '5c'
lumi_data = 84.97
lumi_data_25ns = 1714.32 #1253.92

#cpp_code = open('/afs/cern.ch/user/f/falonso/work/Susy/Run2/PhotonMetAnalysis/lib/loop.cxx').read()
#ROOT.gInterpreter.Declare(cpp_code)

def split_cut(s):
    s = s.strip()
    for op in ['==', '>=', '<=', '>', '<']:
        if op in s:
            var, value = s.split(op)
            break

    return (var.strip(), op, value.strip())


def check_cut(value, op, cut):
    if op == '==':
        return (value == cut)
    elif op == '>=':
        return (value >= cut)
    elif op == '<=':
        return (value <= cut)
    elif op == '>':
        return (value > cut)
    elif op == '<':
        return (value < cut)


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def get_xs(did):
    return xs_dict.get(int(did), 0.0)
    

def get_signal_xs(sample):

    if 'GGM_M3' in sample:
        l = re.findall(ur'[\w.]*.GGM_M3_mu_(\d*)_(\d*).[\w.]*', sample)[0]
        m3, mu = int(l[0]), int(l[1])
        xs = gg_xs.get(m3, None)
        return xs

    else:
        mu = int(sample.split('_')[2])
        xs = ewk_xs.get(mu, None)
        return xs

            
def get_sumw(sample):

    path = os.path.join(MiniDir, sample)

    sumw = 0
    with RootFile(path) as f:
        try:
            tmp = f.Get('events')
            sumw = tmp.GetBinContent(3) # bin 3 is the initial sumw
        except:
            pass

    return sumw


def get_lumi_weight(sample, lumi):

    lumi = float(lumi)

    if 'ttbarg' in sample:
        total = 200000
        xs = 0.76
        return (lumi * xs) / total

    if 'mc15_13tev' in sample.lower():

        sumw = get_sumw(sample)
    
        did = sample.split('.')[1]
        if 'ggm' in sample.lower():
            xs = get_signal_xs(sample)
        else:
            xs = get_xs(did)

        weight = (lumi * xs) / sumw

    elif 'ggm' in sample.lower():

        weight = (get_signal_xs(sample) * lumi) / 1000.

    return weight


def get_datasets(name):

    if 'GGM_M3_mu' in name:
        allsig = getattr(samples, 'signal')
        for s in allsig:
            if name in s:
                slist = [s,]
                break
    else:
        try:
            slist = getattr(samples, name)
        except:
            return [] 

    flist = []
    for s in slist:
        if '_25ns' in name:
            if 'periodE' in name:
                flist.append('25ns/%s.mini_v%s_output.root' % ('.'.join(s.split('.')[0:3]), '6c'))
            else:
                flist.append('25ns/%s.mini_v%s_output.root' % ('.'.join(s.split('.')[0:3]), version_25ns))
        else:
            flist.append('50ns/%s.mini_v%s_output.root' % ('.'.join(s.split('.')[0:3]), version))
            
    return flist
    

#---------------
# get_histogram
#---------------
def get_histogram(sample, variable='cuts', region='SR', selection='', syst='Nom',
                  rootfile=None, scale=True, remove_var=False, truth=False, lumi=None,
                  binning=None):

    ds = get_datasets(sample)

    if not ds:
        return _get_histogram(sample, variable, region, selection, syst, 
                              rootfile, scale, remove_var, truth, lumi, binning)

    hist = None
    for s in ds:

        if not os.path.exists(os.path.join(MiniDir, s)):
            print 'file doesn\'t exist:', s
            continue

        h = _get_histogram(s, variable, region, selection, syst, 
                           rootfile, scale, remove_var, truth, lumi, binning)

        if hist is None:
            hist = h.Clone()
        else:
            hist.Add(h, 1)
            
    return hist


def _get_histogram(sample, variable='cuts', region='SR', selection='', syst='Nom', 
                   rootfile=None, scale=True, remove_var=False, truth=False, lumi=None, 
                   binning=None):


    # sum strong+ewk contributions
    if 'GGM_M3_mu_total' in sample:
        strong_sample = sample.replace('_total', '')

        mu = sample.split('_')[5]
        ewk_sample = 'GGM_mu_%s' % mu

        h_strong = _get_cutflow(strong_sample, selection) 
        h_ewk    = _get_cutflow(ewk_sample, selection) 
        
        h_sum = h_strong + h_ewk

        return h_sum

    if ':' in variable:
        varx, vary = variable.split(':')

    tree = ROOT.TChain('mini')

    if rootfile is not None:
        tree.Add(rootfile)
    elif truth:
        if sample in ['efake', 'jfake', 'data']:
            return None
        else:
            tree.Add('%s/mc15_13TeV.*_%s.mini.root' % (TruthDir, sample))
    else:
        path = os.path.join(MiniDir, sample)
        tree.Add(path)

    systname = syst

    if binning is None:
        binning = get_binning(variable)

    try:
        name = sample.split('.')[1]
    except:
        name = sample

    hname = 'h%s%s_%s_obs_%s' % (name, systname, region, variable.replace(':', '_'))

    if ':' in variable:
        htemp = ROOT.TH2F(hname, hname, *binning)
        htemp.Sumw2()
    else:
        htemp  = ROOT.TH1F(hname, hname, *binning)
        htemp.Sumw2()

    # remove variable from selection if n-1
    if remove_var and variable in selection and not variable == 'cuts':
        
        if ':' in variable:
            selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == varx ])
            selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == vary ])
        else:
            selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == variable ])

        if variable == 'jet_n':
            selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == 'rt4' ])


    # fix selection for extrapolated ttbarg
    if 'ttbarg' in sample:
        selection = selection.replace('jet_pt[]', 'jet1_pt').replace('jet_pt[0]', 'jet1_pt').replace('jet_pt[1]', 'jet2_pt').replace('jet_pt[2]', 'jet2_pt').replace('dphi_jetmet_3j', 'dphi_jetmet')
        variable = variable.replace('jet_pt[]', 'jet1_pt').replace('jet_pt[0]', 'jet1_pt').replace('jet_pt[1]', 'jet2_pt')

    # MC xs weight (temp)
    if lumi is None or lumi == 'data':
        lumi = lumi_data
    elif lumi == 'data_25ns':
        lumi = lumi_data_25ns

    w_str = ''
    if 'mc15' in sample or 'ggm' in sample:
        lumi_weight = get_lumi_weight(sample, lumi)
        w_str = '%s' % lumi_weight

    if 'ttbarg' in sample:
        w_str += '*weight_13tev' 

    varexp = ''
    if selection and w_str:
        varexp = '(%s)*(%s)' % (selection, w_str)
    elif selection:
        varexp = selection
    elif scale:
        varexp = w_str

    if variable == 'cuts':
        tree.Project(hname, '1', varexp)

        hist = histogram_equal_to(htemp)
        error = ROOT.Double(0.0)
        integral = htemp.IntegralAndError(1, hist.GetNbinsX()+1, error)

        hist.SetBinContent(1, integral)
        hist.SetBinError(1, error)

    elif ':' in variable:
        tree.Project(hname, '%s:%s' % (vary, varx), varexp)
        hist = htemp.Clone()
    else:
        tree.Project(hname, variable, varexp)
        hist = htemp.Clone()

    htemp.Delete()

    return hist


#------------
# get_events
#------------
def get_events(sample, region='SR', selection='', syst='Nom', rootfile=None, scale=True, truth=False, lumi=None):
    
    hist = get_histogram(sample, 'cuts', region, selection, syst, rootfile, scale, False, truth, lumi)

    mean = hist.GetBinContent(1)
    error = hist.GetBinError(1)

    hist.Delete()

    return Value(mean, error)


#-------------
# get_cutflow
#-------------
def get_cutflow(sample='', selection='', scale=True, lumi=None):

    ds = get_datasets(sample)

    if not ds:
        return _get_cutflow(sample, selection, scale, lumi)

    hist = None
    for s in ds:

        if not os.path.exists(os.path.join(MiniDir, s)):
            print 'file doesn\'t exist:', s
            continue

        h = _get_cutflow(s, selection, scale, lumi)

        if hist is None:
            hist = h.Clone()
        else:
            hist.Add(h, 1)

    return hist

def _get_cutflow(sample='', selection='', scale=True, lumi=None):

    if not selection:
        return None

    # sum strong+ewk contributions
    if 'GGM_M3_mu_total' in sample:
        strong_sample = sample.replace('_total', '')

        mu = sample.split('_')[5]
        ewk_sample = 'GGM_mu_%s' % mu

        h_strong = _get_cutflow(strong_sample, selection) 
        h_ewk    = _get_cutflow(ewk_sample, selection) 
        
        h_sum = h_strong + h_ewk

        return h_sum

    # if preselection:
    #     h_preselection = get_preselection_cutflow(sample, tag)

    #if syst == 'Nom' or any([s in syst for s in syst_nom]):
    tree = ROOT.TChain('mini')
    #else:
    #    tree = ROOT.TChain('mini_'+syst)

    # if rootfile is not None:
    #     tree.Add(rootfile)
    # elif 'GGM' in sample:
    #     tree.Add('%s/mc15_13TeV.*.%s.mini.root' % (TruthDir, sample))
    #else:
    path = os.path.join(MiniDir, sample)
    tree.Add(path) 

    cuts = [ split_cut(cut) for cut in selection.split('&&') ]

    cutflow = ROOT.TH1F('cutflow', 'cutflow', len(cuts)+1, 0.5, len(cuts)+1.5)

    cutflow.GetXaxis().SetBinLabel(1, 'No Cut')
    for i, cut in enumerate(cuts):
        cutflow.GetXaxis().SetBinLabel(i+2, cut[0])


    if lumi is None:
        lumi = lumi_data

    if 'mc15_13TeV' in sample or 'GGM' in sample:
        weight = get_lumi_weight(sample, lumi)

    if not scale:
        weight = 1

    for event in tree:

        cutflow.Fill(1, weight)

        for i, (varname, op, cutstr) in enumerate(cuts):

            cut = num(cutstr)

            if '[]' in varname:
                varname = varname.replace('[]', '')

            # if varname == 'met_et':
            #     varname = 'met_truth_et'

            if varname == '(el_n+mu_n)':
                value = getattr(event, 'el_n') + getattr(event, 'mu_n')
            elif '[' in varname:
                idx = varname.find('[')
                value = getattr(event, varname[:idx])
                value = value[int(varname[idx+1])]
            else:
                value = getattr(event, varname)


            if check_cut(value, op, cut):
                cutflow.Fill(i+2, weight)
            else:
                break

    # if preselection:
    #     h_preselection.Scale(w)

    #     pre_cuts = h_preselection.GetNbinsX()
    #     new_h = Hist('cutflow', len(cuts)+pre_cuts, 0.5, len(cuts)+pre_cuts+0.5)

    #     for b in xrange(pre_cuts):
    #         new_h.SetBinContent(b+1, h_preselection.GetBinContent(b+1))
    #         new_h.GetXaxis().SetBinLabel(b+1, h_preselection.GetXaxis().GetBinLabel(b+1))
        
    #     for b in xrange(len(cuts)):
    #         new_h.SetBinContent(pre_cuts+b+1, cutflow.GetBinContent(b+1))
    #         new_h.GetXaxis().SetBinLabel(pre_cuts+b+1, cutflow.GetXaxis().GetBinLabel(b+1))

    #     cutflow = new_h

    return cutflow



    
def _get_histogram_loop(sample, variable='cuts', region='SR', selection='', syst='Nom', 
                        rootfile=None, scale=True, remove_var=False, truth=False, lumi=None):

    # if syst == 'Nom': # or any([s in syst for s in syst_nom]):
    #     tree = ROOT.TChain('mini')
    # else:
    #     tree = ROOT.TChain('mini_'+syst)

    # if rootfile is not None:
    #     tree.Add(rootfile)
    # elif truth:
    #     if sample in ['efake', 'jfake', 'data']:
    #         return None
    #     else:
    #         tree.Add('%s/mc15_13TeV.*_%s.mini.root' % (TruthDir, sample))
    # else:
    ds_dir = os.path.join(MiniDir, sample)
    #tree.Add('%s/*.root' % ds_dir)
    path = '%s/*.root' % ds_dir

    systname = syst

    binning = get_binning(variable)

    try:
        name = sample.split('.')[3]
    except:
        name = sample
    hname = 'h%s%s_%s_obs_%s' % (name, systname, region, variable)

    htemp  = ROOT.TH1F(hname, hname, *binning)
    htemp.Sumw2()

    # remove variable from selection if n-1
    if remove_var and variable in selection and not variable == 'cuts':
        selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == variable ])

    # fix selection for extrapolated ttbarg
    if 'ttbarg' in sample:
        selection = selection.replace('jet_pt[]', 'jet1_pt').replace('jet_pt[0]', 'jet1_pt').replace('jet_pt[1]', 'jet2_pt').replace('ph_pt[0]', 'ph_pt').replace('jet_pt[2]', 'jet3_pt')

    cuts = [ split_cut(cut) for cut in selection.split('&&') ]

    # MC xs weight (temp)
    if lumi is None:
        lumi = lumi_data

    if 'mc15' in sample or 'ggm' in sample:
        weight = get_lumi_weight(sample, lumi)
    else:
        weight = 1

    htemp = ROOT.get_histogram_loop(htemp, path, variable, selection, weight)

    # if variable == 'cuts':

    #     hist = histogram_equal_to(htemp)
    #     error = ROOT.Double(0.0)
    #     integral = htemp.IntegralAndError(1, hist.GetNbinsX(), error)
        
    #     hist.SetBinContent(1, integral)
    #     hist.SetBinError(1, error)
    # else:
    hist = htemp.Clone()

    htemp.Delete()

    return hist

    




