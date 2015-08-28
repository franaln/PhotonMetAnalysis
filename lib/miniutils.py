# single photon analysis
# mini utils

import os
import ROOT
from rootutils import RootFile, Value, histogram, histogram_equal_to
from binning import bins
from susy_GGM_M3_mu_mc15points import pointdict
from susy_GGM_mu_mc15points import pointdict as pointdict_ewk
from xs import gg_xs, ewk_xs
import samples

SpDir    = '~/eos/atlas/user/f/falonso/Susy/sp'
MiniDir  = '/raid/falonso/tmp/'
TruthDir =  '/afs/cern.ch/work/f/falonso/Susy/Run2/PhotonMetNtuple/output_truth_final/'

# njg    = Value(0.08567, 0.0002)
# njg_dn = Value(0.04567, 0.0002)
# njg_up = Value(0.12567, 0.0002)

LUMI = 84.97 #78.7
#LUMI = 5000.
XS_FILE = os.path.expanduser('~/work/Susy/Run2/PhotonMetAnalysis/lib/Backgrounds.txt')

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

strong_ewk_fix = {
    '838': '850',
    '883': '850', 
    '928': '950',
    '973': '950',
    '1017': '1050',
    '1062': '1050',
    '1106': '1150',
    '1149': '1150',

    '1036': '1050',
    '1123': '1150',
    '1209': '1250',
    '1292': '1250',
    '1375': '1350',
    '1459': '1450',
    '1540': '1550',
    '1623': '1650',
    '1700': '1650',
    '1788': '1750',
    }

def get_key(sample):

    # EWK
    if 'GGM_mu' in sample:
        gmu = int(sample.split('_')[2])

        for key, mu in pointdict_ewk.iteritems():
            if mu == gmu:
                return key
    
    # 
    if '_total_' in sample:
        gm3 = int(sample.split('_')[4])
        gmu = int(sample.split('_')[5])
    else:
        gm3 = int(sample.split('_')[3])
        gmu = int(sample.split('_')[4])

    for key, (m3, mu) in pointdict.iteritems():
        if m3 == gm3 and mu == gmu:
            return key
    return None


def get_xs(did):
    
    lines = open(XS_FILE).read().split('\n')

    for line in lines:
        if not line or line.startswith('#'):
            continue

        if line.startswith(did):

            did, name, xs, kfact, eff, relunc = line.split()

            return float(xs)*float(kfact)*float(eff)

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
            

def get_datasets(name):

    try:
        slist = getattr(samples, name)
    except:
        return []

    flist = []
    for s in slist:
        flist.append('user.falonso.%s.mini_output.root' % '.'.join(s.split('.')[0:3]))

    return flist
    

def get_histogram(sample, variable='cuts', region='SR', selection='', syst='Nom', 
                  rootfile=None, scale=True, remove_var=False, truth=False):


    ds = get_datasets(sample)

    if not ds:
        return get_histogram2(sample, variable, region, selection, syst, 
                              rootfile, scale, remove_var, truth)

    hist = None
    for s in ds:

        if not os.path.exists(os.path.join(MiniDir, s)):
            print 'error:', s
            continue

        h = get_histogram2(s, variable, region, selection, syst, 
                          rootfile, scale, remove_var, truth)
        
        if hist is None:
            hist = h.Clone()
        else:
            hist.Add(h, 1)

    return hist


def get_histogram2(sample, variable='cuts', region='SR', selection='', syst='Nom', 
                  rootfile=None, scale=True, remove_var=False, truth=False):

    # strong+ewk
    if 'GGM_M3_mu_total' in sample:
        
        strong_sample = sample.replace('_total', '')

        mu = sample.split('_')[5]
        
        if mu in strong_ewk_fix:
            mu = strong_ewk_fix[mu]
        ewk_sample = 'GGM_mu_%s' % mu

        h_strong = get_histogram2(strong_sample, variable, region, selection, syst, rootfile, scale, remove_var, truth)
        h_ewk    = get_histogram2(ewk_sample,    variable, region, selection, syst, rootfile, scale, remove_var, truth)
        
        h_sum = h_strong + h_ewk

        return h_sum

    # if EWK fix intermidiate points. TODO: interpolate between near points
    if 'GGM_mu' in sample:
        mu = sample.split('_')[2] 
        if mu in strong_ewk_fix:
            sample = 'GGM_mu_%s' % strong_ewk_fix[mu]


    #if syst == 'Nom' or any([s in syst for s in syst_nom]):
    tree = ROOT.TChain('mini')
    #else:
    #    tree = ROOT.TChain('mini_'+syst)
        
    if rootfile is not None:
        tree.Add(rootfile)
    elif truth:
        if sample in ['efake', 'jfake', 'data']:
            return None
        else:
            tree.Add('%s/mc15_13TeV.*.%s.mini.root' % (TruthDir, sample))
    else:

        ds_dir = os.path.join(MiniDir, sample)

        number_events = 0
        for fname in os.listdir(ds_dir):

            with RootFile(os.path.join(ds_dir, fname)) as f:
                try:
                    tmp = f.Get('number_events')
                    number_events += tmp.GetBinContent(2)
                except:
                    continue

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

    systname = syst
    # if 'UP' in syst:
    #     systname = systname.replace('UP', 'High')
    # elif 'DOWN' in syst:
    #     systname = systname.replace('DOWN', 'Low')
    # elif 'LOW' in syst:
    #     systname = systname.replace('LOW', 'Low')
    # elif 'Down' in syst:
    #     systname = systname.replace('Down', 'Low')
    # elif 'Up' in syst:
    #     systname = systname.replace('Up', 'High')

    try:
        name = sample.split('.')[3]
    except:
        name = sample
    hname = 'h%s%s_%s_obs_%s' % (name, systname, region, variable)

    #htemp = histogram(hname, *binning)
    htemp  = ROOT.TH1F(hname, hname, *binning)
    htemp.Sumw2()

    # if not scale:
    #     w_str = ''
    # elif syst == 'PRWDOWN':
    #     w_str = 'weight_prwdn'
    # elif syst == 'PRWUP':
    #     w_str = 'weight_prwup'
    # else:
    #     w_str = 'weight'

    # if scale and 'CRL' in region_name:
    #     if syst == 'BJETDOWN':
    #         w_str += '*btag_weight[1]'
    #     elif syst == 'BJETUP':
    #         w_str += '*btag_weight[4]'
    #     elif syst == 'CJETDOWN':
    #         w_str += '*btag_weight[2]'
    #     elif syst == 'CJETUP':
    #         w_str += '*btag_weight[5]'
    #     elif syst == 'BMISTAGDOWN':
    #         w_str += '*btag_weight[3]'
    #     elif syst == 'BMISTAGUP':
    #         w_str += '*btag_weight[6]'
    #     else:
    #         w_str += '*btag_weight[0]'

    # if scale and sample == 'efake':
    #     w_str += '*weight_feg'

    # remove variable from selection if n-1
    if remove_var and variable in selection and not variable == 'cuts':
        if 'ph_pt' in variable or 'jet_n' in variable:
            pass
        else:
            selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == variable ])

    # MC xs weight (temp)
    w_str = ''
    if 'mc15_13TeV' in sample:

        did = sample.split('.')[3]

        xs = get_xs(did)

        weight = (LUMI * xs) / number_events

        w_str = '%s' % weight

    elif 'GGM' in sample:
        weight = (get_signal_xs(sample) * LUMI) / 1000.

        w_str = '%s' % weight

   
    varexp = ''
    if selection and w_str:
        varexp = '(%s)*(%s)' % (selection, w_str)
    elif selection:
        varexp = selection
    elif scale:
        varexp = w_str

#    print sample, varexp
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

#    print w_str, htemp.Integral(1, hist.GetNbinsX())

    htemp.Delete()

    # if sample == 'jfake':
    #     if syst == 'JFAKEUP':
    #         hist.scale(njg_up)
    #     elif syst == 'JFAKEDOWN':
    #         hist.scale(njg_dn)
    #     else:
    #         hist.scale(njg)

    return hist


def get_events(sample, region='SR', selection='', syst='Nom', rootfile=None, scale=True, truth=False):

    hist = get_histogram(sample, 'cuts', region, selection, syst, rootfile, scale=scale, truth=truth)

    mean = hist.GetBinContent(1)
    error = hist.GetBinError(1)

    hist.Delete()

    return Value(mean, error)


# def get_preselection_cutflow(sample, tag):


#     periods = ['A', 'B', 'C', 'D', 'E', 'G', 'H', 'I', 'J', 'L']

#     h = None
#     if sample == 'data':
#         for p in periods:
            
#             tmp_file = ROOT.TFile.Open('%s/%s%s.tight.%s_spntuple.root' % (SpDir, sample, p, tag))
#             tmp_h = tmp_file.Get('h_cutflow')

#             if h is None:
#                 h = tmp_h.Clone('h')
#             else:
#                 h.Add(tmp_h, 1)

#             h.SetDirectory(0)
#             tmp_file.Close()
#     else:
#         tmp_file = ROOT.TFile.Open('%s/%s.tight.%s_spntuple.root' % (SpDir, sample, tag))
#         tmp_h = tmp_file.Get('h_cutflow')

#         h = tmp_h.Clone('h')
#         h.SetDirectory(0)
#         tmp_file.Close()

#     return h


def get_cutflow(sample='', selection=''):

    ds = get_datasets(sample)

    if not ds:
        return get_cutflow2(sample, selection)

    hist = None
    for s in ds:

        if not os.path.exists(os.path.join(MiniDir, s)):
            print 'error:', s
            continue

        h = get_cutflow2(s, selection)
        
        if hist is None:
            hist = h.Clone()
        else:
            hist.Add(h, 1)

    return hist

def get_cutflow2(sample='', selection='', syst='Nom', rootfile=None, scale=True, preselection=False):

    if not selection:
        return None

    if 'GGM_M3_mu_total' in sample:
        # sum strong+ewk contributions
        strong_sample = sample.replace('_total', '')

        mu = sample.split('_')[5]
        ewk_sample = 'GGM_mu_%s' % mu

        h_strong = get_cutflow2(strong_sample, selection) #, tag, syst, rootfile, scale, preselection)
        h_ewk    = get_cutflow2(ewk_sample, selection) #, tag, syst, rootfile, scale, preselection)
        
        h_sum = h_strong + h_ewk

        return h_sum


    if preselection:
        h_preselection = get_preselection_cutflow(sample, tag)

    if syst == 'Nom' or any([s in syst for s in syst_nom]):
        tree = ROOT.TChain('mini')
    else:
        tree = ROOT.TChain('mini_'+syst)

    if rootfile is not None:
        tree.Add(rootfile)
    elif 'GGM' in sample:
        tree.Add('%s/mc15_13TeV.*.%s.mini.root' % (TruthDir, sample))
    else:
        #tree.Add("%s/%s.%s_mini.root" % (MiniDir, sample, tag))

        ds_dir = os.path.join(MiniDir, sample)

        number_events = 0
        for fname in os.listdir(ds_dir):

            with RootFile(os.path.join(ds_dir, fname)) as f:
                try:
                    tmp = f.Get('number_events')
                    number_events += tmp.GetBinContent(2)
                except:
                    continue

        tree.Add('%s/*.root' % ds_dir)


    cuts = [ split_cut(cut) for cut in selection.split('&&') ]

    cutflow = ROOT.TH1F('cutflow', 'cutflow', len(cuts), 0.5, len(cuts)+0.5)

    for i, cut in enumerate(cuts):
        cutflow.GetXaxis().SetBinLabel(i+1, cut[0])

    if 'mc15_13TeV' in sample:

        did = sample.split('.')[3]

        xs = get_xs(did)

        weight = (LUMI * xs) / number_events

    elif 'GGM' in sample:

        weight = (get_signal_xs(sample) * LUMI) / 1000.


    for event in tree:

        # if scale:
        #     w = event.weight
        #     if sample == 'efake':
        #         w *= event.weight_feg
        # else:
        #     w = 1

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

    print cutflow.GetBinContent(len(cuts))
    return cutflow

