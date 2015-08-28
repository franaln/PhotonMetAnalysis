# single photon analysis
# mini utils

import os
import ROOT
from rootutils import RootFile, Value, histogram, histogram_equal_to
from binning import bins
from xs import gg_xs, ewk_xs
from xs_dict import xs_dict
import samples

SpDir    = '~/eos/atlas/user/f/falonso/Susy/sp'
MiniDir  = '/raid/falonso/mini2/'
TruthDir =  '/afs/cern.ch/work/f/falonso/Susy/Run2/PhotonMetNtuple/output_truth_final/'
version = 2
lumi_data = 84.97


def split_cut(s):
    s = s.strip()
    for op in ['==', '>=', '<=', '>', '<']:
        if op in s:
            var, value = s.split(op)
            break

    return (var, op, value)


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
    
    # lines = open(XS_FILE).read().split('\n')

    # for line in lines:
    #     if not line or line.startswith('#'):
    #         continue

    #     if line.startswith(did):

    #         did, name, xs, kfact, eff, relunc = line.split()

    #         return float(xs)*float(kfact)*float(eff)


def get_signal_xs(sample):

    if 'GGM_M3' in sample:
        m3 = int(sample.split('_')[3])
        mu = int(sample.split('_')[4])

        xs = gg_xs.get((m3, mu), None)

        return xs

    else:
        mu = int(sample.split('_')[2])

        xs = ewk_xs.get(mu, None)

        return xs

            
def get_sumw(sample):

    path = os.path.join(MiniDir, sample)

    sumw = 0
    for fpath in os.listdir(path):

        with RootFile(os.path.join(path, fpath)) as f:
            try:
                tmp = f.Get('events')
                sumw += tmp.GetBinContent(3) # bin 3 is the initial sumw
            except:
                continue

    return sumw


def get_lumi_weight(sample, lumi):

    sumw = get_sumw(sample)

    if 'mc15_13TeV' in sample:

        did = sample.split('.')[3]

        xs = get_xs(did)

        weight = (lumi * xs) / sumw

    elif 'GGM' in sample:

        weight = (get_signal_xs(sample) * lumi) / 1000.

    return weight




def get_datasets(name):

    try:
        slist = getattr(samples, name)
    except:
        return []

    flist = []
    for s in slist:
        flist.append('user.falonso.%s.mini_v%s_output.root' % ('.'.join(s.split('.')[0:3]), version))

    return flist
    

#---------------
# get_histogram
#---------------
def get_histogram(sample, variable='cuts', region='SR', selection='', syst='Nom',
                  rootfile=None, scale=True, remove_var=False, truth=False, lumi=None):


    ds = get_datasets(sample)

    if not ds:
        return _get_histogram(sample, variable, region, selection, syst, 
                              rootfile, scale, remove_var, truth, lumi)

    hist = None
    for s in ds:

        if not os.path.exists(os.path.join(MiniDir, s)):
            print 'File doesn\'t exist:', s
            continue

        h = _get_histogram(s, variable, region, selection, syst, 
                           rootfile, scale, remove_var, truth, lumi)
        
        if hist is None:
            hist = h.Clone()
        else:
            hist.Add(h, 1)

    return hist


def _get_histogram(sample, variable='cuts', region='SR', selection='', syst='Nom', 
                   rootfile=None, scale=True, remove_var=False, truth=False, lumi=None):

    # strong+ewk
    if 'GGM_M3_mu_total' in sample:
        
        strong_sample = sample.replace('_total', '')

        mu = sample.split('_')[5]
        
        if mu in strong_ewk_fix:
            mu = strong_ewk_fix[mu]
        ewk_sample = 'GGM_mu_%s' % mu

        h_strong = _get_histogram(strong_sample, variable, region, selection, syst, rootfile, scale, remove_var, truth)
        h_ewk    = _get_histogram(ewk_sample,    variable, region, selection, syst, rootfile, scale, remove_var, truth)
        
        h_sum = h_strong + h_ewk

        return h_sum

    # if EWK fix intermidiate points. TODO: interpolate between near points
    if 'GGM_mu' in sample:
        mu = sample.split('_')[2] 
        if mu in strong_ewk_fix:
            sample = 'GGM_mu_%s' % strong_ewk_fix[mu]


    if syst == 'Nom': # or any([s in syst for s in syst_nom]):
        tree = ROOT.TChain('mini')
    else:
        tree = ROOT.TChain('mini_'+syst)
        
    if rootfile is not None:
        tree.Add(rootfile)
    elif truth:
        if sample in ['efake', 'jfake', 'data']:
            return None
        else:
            tree.Add('%s/mc15_13TeV.*.%s.mini.root' % (TruthDir, sample))
    else:
        ds_dir = os.path.join(MiniDir, sample)
        tree.Add('%s/*.root' % ds_dir)


    if '[' in variable and ']' in variable:
        binning = bins.get(variable[:variable.index('[')], None)
    else:
        binning = bins.get(variable, None)

    if binning is None:
        try:
            binning = bins.get(variable.split('_')[1], None)
        except:
            binning = None

    if binning is None:
        raise Exception('Not bins configured for this variable %s' % variable)

    try:
        name = sample.split('.')[3]
    except:
        name = sample
    hname = 'h%s%s_%s_obs_%s' % (name, systname, region, variable)

    htemp  = ROOT.TH1F(hname, hname, *binning)
    htemp.Sumw2()

    # remove variable from selection if n-1
    if remove_var and variable in selection and not variable == 'cuts':
        if 'ph_pt' in variable:
            pass
        else:
            selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == variable ])

    # MC xs weight (temp)
    if lumi is None:
        lumi = lumi_data

    w_str = ''
    if 'mc15' in sample or 'GGM' in sample:
        lumi_weight = get_lumi_weight(sample, lumi)
        w_str = '%s' % lumi_weight

   
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
        integral = htemp.IntegralAndError(1, hist.GetNbinsX(), error)
        
        hist.SetBinContent(1, integral)
        hist.SetBinError(1, error)
    else:
        tree.Project(hname, variable, varexp)
        hist = htemp.Clone()

    htemp.Delete()

    return hist


#------------
# get_events
#------------
def get_events(sample, region='SR', selection='', syst='Nom', rootfile=None, scale=True, truth=False, lumi=None):

    hist = get_histogram(sample, 'cuts', region, selection, syst, rootfile, scale, truth, lumi)

    mean = hist.GetBinContent(1)
    error = hist.GetBinError(1)

    hist.Delete()

    return Value(mean, error)


#-------------
# get_cutflow
#-------------
def get_cutflow(sample='', selection=''):

    ds = get_datasets(sample)

    if not ds:
        return _get_cutflow(sample, selection)

    hist = None
    for s in ds:

        if not os.path.exists(os.path.join(MiniDir, s)):
            print 'file doesn\'t exist:', s
            continue

        h = _get_cutflow(s, selection)
        
        if hist is None:
            hist = h.Clone()
        else:
            hist.Add(h, 1)

    return hist

def _get_cutflow(sample='', selection='', syst='Nom', rootfile=None, scale=True, preselection=False):

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

    if syst == 'Nom' or any([s in syst for s in syst_nom]):
        tree = ROOT.TChain('mini')
    else:
        tree = ROOT.TChain('mini_'+syst)

    if rootfile is not None:
        tree.Add(rootfile)
    elif 'GGM' in sample:
        tree.Add('%s/mc15_13TeV.*.%s.mini.root' % (TruthDir, sample))
    else:
        ds_dir = os.path.join(MiniDir, sample)
        tree.Add('%s/*.root' % ds_dir)


    cuts = [ split_cut(cut) for cut in selection.split('&&') ]

    cutflow = ROOT.TH1F('cutflow', 'cutflow', len(cuts), 0.5, len(cuts)+0.5)

    for i, cut in enumerate(cuts):
        cutflow.GetXaxis().SetBinLabel(i+1, cut[0])

    if 'mc15_13TeV' in sample or 'GGM' in sample:
        weight = get_lumi_weight(sample, lumi)

    for event in tree:

        for i, (varname, op, cutstr) in enumerate(cuts):

            cut = num(cutstr)

            if '[]' in varname:
                varname = varname.replace('[]', '')

            if varname == 'met_et':
                varname = 'met_truth_et'

            if varname == '(el_n+mu_n)':
                value = getattr(tree, 'el_n') + getattr(tree, 'mu_n')
            elif '[' in varname:
                idx = varname.find('[')
                value = getattr(tree, varname[:idx])
                value = value[int(varname[idx+1])]
            else:
                value = getattr(tree, varname)

            if check_cut(value, op, cut):
                cutflow.Fill(i+1, weight)
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

