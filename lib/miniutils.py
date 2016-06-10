# single photon analysis
# mini utils

import os
import re
import ROOT
from rootutils import RootFile, Value, histogram, histogram_equal_to
from binning import get_binning
from signalxs import get_gg_xs, get_ewk_xs, get_ewk_sumw
from xs_dict import xs_dict
import samples
import systematics


MiniDir   = '/ar/pcunlp001/raid/falonso/mini2/'
MiniDir2  = '/ar/pcunlp002/disk/falonso/mini2/'
TruthDir = '/afs/cern.ch/work/f/falonso/Susy/Run2/PhotonMetNtuple/output_truth_final/'

lumi_data_201 = 3209.05 # 3.2 fb-1
lumi_data_207 = 3324.5

lumi_data = lumi_data_201

versions = ['24', '22', '21', '20', '19', '18f', '16f',]

#------------
# Cuts utils
#------------
def split_cut(s):
    s = s.strip()
    for op in ['==', '>=', '<=', '>', '<', '!=']:
        if op in s:
            var, value = s.split(op)
            break

    return (var.strip(), op, value.strip())


def invert_cut(s):
    (var, op, value) = split_cut(s)
    
    if op == '>' or op == '>=':
        newop = '<'
    elif op == '<' or op == '<=':
        newop = '>'
    else:
        newop = op

    return '%s %s %s' % (var, newop, value)


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
    elif op == '!=':
        return (value != cut)


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


#----------------------------
# Cross section/lumi weights
#----------------------------
def get_xs(did):
    xs = xs_dict.get(int(did), None)

    if xs is None:
        print 'missing XS for this ID:', did
        return 0.0
    
    return xs


def get_signal_xs(sample, fs=0):

    if 'GGM_M3' in sample:
        #l = re.findall(ur'[\w.]*.GGM_M3_mu_(\d*)_(\d*).[\w.]*', sample)[0]
        l = re.findall(ur'[\w.]*mc15_13TeV\.(\d*)\..*GGM_M3_mu_(\d*)_(\d*).[\w.]*', sample)[0]

        did, m3, mu = int(l[0]), int(l[1]), int(l[2])

        xs, unc = get_gg_xs(did, m3, mu)

        return xs

    elif 'GGM_mu' in sample:
        l = re.findall(ur'[\w.]*mc15_13TeV\.(\d*)\..*GGM_mu_(\d*).[\w.]*', sample)[0]
        did, mu = int(l[0]), int(l[1])
     
        xs, unc = get_ewk_xs(did, mu, fs)

        return xs


def get_sumw(sample):

    path = sample

    sumw = 0
    with RootFile(path) as f:
        try:
            tmp = f.Get('events')
            sumw = tmp.GetBinContent(3) # bin 3 is the initial sumw
        except:
            pass

    return sumw


def get_lumi_weight(sample, lumi, fs=None):

    lumi = float(lumi)

    if 'mc15_13tev' in sample.lower():

        if 'GGM_mu' in sample and fs is not None:
            mu = int(re.findall(ur'[\w.]*.GGM_mu_(\d*).[\w.]*', sample)[0])
            sumw = get_ewk_sumw(mu, fs)
        else:
            sumw = get_sumw(sample)
    
        did = sample.split('.')[1]
        if 'GGM_M3_mu' in sample or 'GGM_mu' in sample:
            xs = get_signal_xs(sample, fs)
        else:
            xs = get_xs(did)

        try:
            weight = (lumi * xs) / sumw
        except:
            weight = 0.

    elif 'ggm' in sample.lower():

        weight = (get_signal_xs(sample) * lumi) / 1000.

    return weight


#----------
# Datasets
#----------
def get_datasets(name, version=None):

    slist = []
    if 'GGM_M3_mu' in name or 'GGM_mu' in name:
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

        if version is not None:

            mini_dir = MiniDir
            try:
                if int(version) > 22:
                    mini_dir = MiniDir2
            except:
                pass

            path = mini_dir + '/v' + version + '/' + '%s.mini_v%s_output.root' % ('.'.join(s.split('.')[0:3]), version)

            if os.path.isfile(path):
                flist.append(path)
            else:
                print path + ' doesn\'t exist'
            
        else:
            for version in versions:
                
                mini_dir = MiniDir
                try:
                    if int(version) > 22:
                        mini_dir = MiniDir2
                except:
                    pass

                path = mini_dir + '/v' + version + '/' + '%s.mini_v%s_output.root' % ('.'.join(s.split('.')[0:3]), version)

                if os.path.isfile(path):
                    flist.append(path)
                    break

            else:
                print 'using 50ns sample: %s' % s
                flist.append(MiniDir + '/50ns/%s.mini_v3c_output.root' % '.'.join(s.split('.')[0:3]))
            
    return flist
    

def show_datasets():

    samples_ = [
        'photonjet',
        'multijet',
        'vgamma',
        'ttbar',
        'ttbarg',
        'wjets',
        'zjets',
        'data',
        ]

    for s in samples_:
        for ds in get_datasets(s):
            print ds

#---------------
# get_histogram
#---------------
def _get_histogram(sample, path, **kwargs):

    variable   = kwargs.get('variable', 'cuts')
    region     = kwargs.get('region', 'SR')
    selection  = kwargs.get('selection', '')
    syst       = kwargs.get('syst', 'Nom')
    scale      = kwargs.get('scale', True)
    remove_var = kwargs.get('remove_var', False)
    invert_var = kwargs.get('invert_var', False)
    truth      = kwargs.get('truth', False)
    lumi       = kwargs.get('lumi', None)
    binning    = kwargs.get('binning', None)
    prw        = kwargs.get('prw', False)
    version    = kwargs.get('version', None)
    fs         = kwargs.get('fs', None)

    # weights
    use_sfw     = kwargs.get('use_sfw', True)
    use_mcw     = kwargs.get('use_mcw', True)
    use_puw     = kwargs.get('use_puw', False)

    debug      = kwargs.get('debug', False)

    #-----------
    # File/Chain
    #-----------
    if ':' in variable:
        varx, vary = variable.split(':')

    tree = ROOT.TChain('mini')
    tree.Add(path)


    #-----------
    # Histogram
    #-----------
    systname = syst

    if binning is None:
        binning = get_binning(variable)

    try:
        name = sample.split('.')[1]
    except:
        name = sample

    if fs is not None:
        hname = 'h%s_%s%s_%s_obs_%s' % (name, fs, systname, region, variable.replace(':', '_'))
    else:
        hname = 'h%s%s_%s_obs_%s' % (name, systname, region, variable.replace(':', '_'))

    if ':' in variable:
        htemp = ROOT.TH2D(hname, hname, *binning)
        htemp.Sumw2()
    else:
        htemp  = ROOT.TH1D(hname, hname, *binning)
        htemp.Sumw2()


    #-----------
    # Selection
    #-----------
    # remove variable from selection if n-1
    if remove_var and variable in selection and not variable == 'cuts':
        
        selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == variable ])

        if variable == 'jet_n':
            selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == 'rt4' ])

    if remove_var and (':' in variable):
        if varx in selection:
            selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == varx ])
        if vary in selection:
            selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == vary ])

    if 'v3c' in sample and 'meff' in selection:
        selection = selection.replace('meff', 'ht+ph_pt[0]')

    if fs is not None:
        if selection:
            selection = selection + ' && fs==%s' % fs
        else:
            selection = 'fs==%s' % fs

    # change selection and variable for systematics
    if syst != 'Nom' and systematics.affects_kinematics(syst):
        for var in systematics.get_affected_variables(syst):
            if var in selection:
                selection = selection.replace(var, var + '_' + syst)
            
        if variable in systematics.get_affected_variables(syst):
            variable = variable.replace(var, var + '_' + syst)
        
        
    #---------
    # Weights
    #---------
    if lumi is not None and lumi != 'data' and float(lumi) < 100:
        lumi = float(lumi) * 1000

    if lumi is None or lumi == 'data':
        lumi = lumi_data

    w_str = ''
    if 'mc15' in sample:

        # lumi weight
        lumi_weight = get_lumi_weight(sample, lumi, fs)        
        w_str += '%s' % lumi_weight

        # mc weight
        if use_mcw:
            w_str += '*weight_mc'

        # scale factors
        if use_sfw:
            if syst != 'Nom' and systematics.affects_weight(syst):
                w_str += '*weight_sf_%s' % syst 
            else:
                w_str += '*weight_sf' 

        # pile-up
        if use_puw:
            w_str += '*weight_pu'
        
    if 'efake' in sample:
        if syst == 'Nom':
            w_str += 'weight_feg'
        elif syst == 'FegLow':
            w_str += 'weight_feg_dn'
        elif syst == 'FegHigh':
            w_str += 'weight_feg_up'

    elif 'jfake' in sample:
        w_str += 'weight_fjg'

    if not scale:
        w_str = ''

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


def get_histogram(sample, **kwargs):

    variable   = kwargs.get('variable', 'cuts')
    region     = kwargs.get('region', 'SR')
    syst       = kwargs.get('syst', 'Nom')
    rootfile   = kwargs.get('rootfile', None)
    version    = kwargs.get('version', None)

    if '.root' in sample:

        path = sample
        sample = os.path.basename(sample).split('.')[0]

        return _get_histogram(sample, path, **kwargs)

    # sum strong+ewk contributions
    if 'GGM_M3_mu_total' in sample:
        strong_sample = sample.replace('_total', '')

        mu = sample.split('_')[5]
        ewk_sample = 'GGM_mu_%s' % mu

        h_strong = get_histogram(strong_sample, strong_sample, **kwargs)
        h_ewk    = get_histogram(ewk_sample, ewk_sample, **kwargs)
        
        h_sum = h_strong + h_ewk

        return h_sum


    ds = get_datasets(sample, version)

    if sample in ['efake', 'jfake']:
        ds_tmp = get_datasets('data')

        ds = []
        for s in ds_tmp:
            ds.append(s.replace('data15_13TeV', sample))

    if not ds:
        return _get_histogram(sample, sample, **kwargs)


    hist = None

    # ewk grid: sum over all sub-processes
    if 'GGM_mu' in sample and len(ds) == 1:

        spath = os.path.join(MiniDir, ds[0])

        relevant_fs = [111, 112, 113, 115, 117, 118, 123, 125, 126, 127, 133, 134, 135, 137, 138, 146, 148, 157, 158, 168]
        for fs in relevant_fs:
            
            h = _get_histogram(sample, spath, fs=fs, **kwargs)

            if hist is None:
                hist = h.Clone()
            else:
                hist.Add(h, 1)

    
    else:
        
        for s in ds:

            spath = os.path.join(MiniDir, s)

            if not os.path.exists(spath):
                print 'file doesn\'t exist:', s
                continue

            h = _get_histogram(s, spath, **kwargs)

            if hist is None:
                hist = h.Clone()
            else:
                hist.Add(h, 1)


    # fix histogram name
    if sample == 'data':
        hname = 'h%s_%s_obs_%s' % (sample, region, variable.replace(':', '_'))
    else:

        if syst != 'Nom':
            syst = syst.replace('Up', 'High').replace('Down', 'Low')
            syst = syst.replace('__1up', 'High').replace('__1down', 'Low')

        hname = 'h%s%s_%s_obs_%s' % (sample, syst, region, variable.replace(':', '_'))

    hist.SetName(hname)
    hist.SetTitle(hname)
            
    return hist


#------------
# get_events
#------------
def get_events(sample, **kwargs):

    hist = get_histogram(sample, variable='cuts', **kwargs)

    mean = hist.GetBinContent(1)
    error = hist.GetBinError(1)

    hist.Delete()

    return Value(mean, error)


#-------------
# get_cutflow
#-------------
def get_cutflow(sample, selection='', scale=True, lumi=None, preselection=False):

    if not selection:
        return None

    # sum strong+ewk contributions
    # if 'GGM_M3_mu_total' in sample:
    #     strong_sample = sample.replace('_total', '')

    #     mu = sample.split('_')[5]
    #     ewk_sample = 'GGM_mu_%s' % mu

    #     h_strong = _get_cutflow(strong_sample, selection) 
    #     h_ewk    = _get_cutflow(ewk_sample, selection) 
        
    #     h_sum = h_strong + h_ewk

    #     return h_sum


    cuts = [ split_cut(cut) for cut in selection.split('&&') ]

    cutflow = ROOT.TH1F('cutflow', 'cutflow', len(cuts)+1, 0.5, len(cuts)+1.5)

    cutflow.GetXaxis().SetBinLabel(1, 'No Cut')
    for i, cut in enumerate(cuts):
        cutflow.GetXaxis().SetBinLabel(i+2, cut[0])

    cuts = [('', '', ''),] + cuts

    selection = ''
    for i, (var, op, value) in enumerate(cuts):

        if not selection:
            selection += '%s %s %s' % (var, op, value)
        else:
            selection += ' && %s %s %s' % (var, op, value)

        selection = selection.strip()
        if selection == ' ':
            selection = ''

        evts = get_events(sample, selection=selection, lumi=lumi, scale=scale)

        cutflow.SetBinContent(i+1, evts.mean)
        cutflow.SetBinError(i+1, evts.error)


    if preselection:

        if '.root' in sample:
            ds = [sample, ]
        else:
            ds = get_datasets(sample)

        h_preselection = None
        for s in ds:
            f = ROOT.TFile.Open(s)
            htmp = f.Get('cutflow')

            # Weight
            if lumi is None or lumi == 'data':
                lumi = lumi_data

            if scale and 'data' not in sample:
                lumi_weight = get_lumi_weight(sample, lumi)
                htmp.Scale(lumi_weight)


            if h_preselection is None:
                h_preselection = htmp.Clone()
                h_preselection.SetDirectory(0)
            else:
                h_preselection.Add(htmp, 1)

            f.Close()
        

        pre_cuts = h_preselection.GetNbinsX()
        new_h = ROOT.TH1F('cutflow', 'cutflow', len(cuts)+pre_cuts, 0.5, len(cuts)+pre_cuts+0.5)
        for b in xrange(pre_cuts):
            new_h.SetBinContent(b+1, h_preselection.GetBinContent(b+1))
            new_h.GetXaxis().SetBinLabel(b+1, h_preselection.GetXaxis().GetBinLabel(b+1))
        
        for b in xrange(len(cuts)):
            new_h.SetBinContent(pre_cuts+b+1, cutflow.GetBinContent(b+1))
            new_h.GetXaxis().SetBinLabel(pre_cuts+b+1, cutflow.GetXaxis().GetBinLabel(b+1))
            
        return new_h


    return cutflow



# def get_cutflow(sample='', selection='', scale=True, lumi=None, preselection=False):

#     ds = get_datasets(sample)

#     if not ds:
#         return _get_cutflow(sample, selection, scale, lumi, preselection)

#     hist = None
#     for s in ds:

#         if not os.path.exists(os.path.join(MiniDir, s)):
#             print 'file doesn\'t exist:', s
#             continue

#         h = _get_cutflow(s, selection, scale, lumi, preselection)

#         if hist is None:
#             hist = h.Clone()
#         else:
#             hist.Add(h, 1)

#     return hist

