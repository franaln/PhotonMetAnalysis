# single photon analysis
# mini utils

import os
import re
import ROOT

from rootutils import RootFile, Value, histogram, histogram_equal_to
from signalxs import get_gg_xs, get_ewk_xs, get_ewk_sumw
from xs_dict import xs_dict
import systematics

# config
import analysis as config_analysis
import samples as config_samples
import binning as config_binning

MiniDir1  = '/ar/pcunlp001/raid/falonso/mini2'
MiniDir2  = '/ar/pcunlp002/disk/falonso/mini2'

# --------
# Binning
#---------
def get_binning_single_variable(variable):

    if '[' in variable and ']' in variable:
        binning_ = config_binning.bins.get(variable[:variable.index('[')], None)
    else:
        binning_ = config_binning.bins.get(variable, None)

    if binning_ is None:
        try:
            binning_ = config_binning.bins.get(variable.split('_')[1], None)
        except:
            binning_ = None

    if binning_ is None:
        try:
            binning_ = config_binning.bins.get(variable.split('_')[0], None)
        except:
            binning_ = None

    if binning_ is None and 'ht+' in variable:
        binning_ = config_binning.bins.get('meff', None)

    return binning_


def get_binning(variable):

    if ':' in variable:
        varx, vary = variable.split(':')

        binning_x = get_binning_single_variable(varx)
        binning_y = get_binning_single_variable(vary)

        binning_ = binning_x + binning_y
    else:
        binning_ = get_binning_single_variable(variable)

    if binning_ is None:
        raise Exception('Not bins configured for this variable %s' % variable)

    return binning_


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
def get_xs(ds):

    xs = xs_dict.get(int(ds['did']), None)

    if xs is None:
        print 'missing XS for this ID:', did
        return 0.0
    
    return xs


def get_signal_xs(ds, fs=0):

    if 'GGM_M3' in ds['short_name']:

        l = re.findall(ur'GGM_M3_mu_(\d*)_(\d*)', ds['short_name'])[0]

        did = int(ds['did'])

        m3, mu = int(l[0]), int(l[1])

        xs, unc = get_gg_xs(did, m3, mu)

        return xs

    elif 'GGM_mu' in ds['short_name']:

        l = re.findall(ur'*GGM_mu_(\d*)', ds['short_name'])[0]

        did = int(ds['did'])
        mu = int(l[0])
     
        xs, unc = get_ewk_xs(did, mu, fs)

        return xs


def get_sumw(ds):

    sumw = 0
    with RootFile(ds['path']) as f:
        try:
            tmp = f.Get('events')
            sumw = tmp.GetBinContent(3) # bin 3 is the initial sumw
        except:
            pass

    return sumw


def get_lumi_weight(ds, lumi, fs=None):

    lumi = float(lumi)

    if ds['project'] == 'mc15_13TeV':

        if 'GGM_mu' in ds['short_name'] and fs is not None:
            mu = int(re.findall(ur'GGM_mu_(\d*)', ds['short_name'])[0])
            sumw = get_ewk_sumw(mu, fs)
        else:
            sumw = get_sumw(ds)
    
        if 'GGM_M3_mu' in ds['short_name'] or 'GGM_mu' in ds['short_name']:
            xs = get_signal_xs(ds, fs)
        else:
            xs = get_xs(ds)

        try:
            weight = (lumi * xs) / sumw
        except:
            weight = 0.

    elif 'GGM' in ds['short_name']:

        weight = (get_signal_xs(ds) * lumi) / 1000.

    return weight


#----------
# Samples
#----------
def get_datasets_names(name): 

    ds_tmp = config_samples.samples_dict.get(name)

    ds = []
    if isinstance(ds_tmp, str):
        if '+' in ds_tmp:
            dsnames = [ i.strip() for i in ds_tmp.split('+')  if i ]
            for dsname in dsnames:
                ds += get_datasets_names(dsname)

        else:
            ds.append(ds_tmp)

    else:
        ds = ds_tmp

    return ds
 

r_ds = re.compile('(mc15_13TeV|data15_13TeV|data16_13TeV|efake15|efake16|jfake15|jfake16)\.([0-9]*)\.(.*)')

def find_path(project, did, short_name, versions, ptags):

    for version in versions:

        vtag = ''
        if '_' in version:
            vtag    = '_' + version.split('_')[1]
            version = version.split('_')[0]

        version_i = int(version)

        if version_i > 22:
            mini_dir = MiniDir2
        else:
            mini_dir = MiniDir1

        if version_i > 31:
            for ptag in ptags:
                path = '%s/v%s/%s.%s.%s.mini.p%s.v%s%s_output.root' % (mini_dir, version, project, did, short_name, ptag, version, vtag)
                if os.path.isfile(path):
                    return path
        else:
            path = '%s/v%s/%s.%s.%s.mini_v%s_output.root' % (mini_dir, version, project, did, short_name, version)
            if os.path.isfile(path):
                return path

    return ''

def get_sample_datasets(name, version=None, ptag=None):

    # get datasets corresponding to sample
    dsnames = get_datasets_names(name)

    if not dsnames:
        raise Exception('sample %s not found in samples.py' % name)

    datasets = []
    for ds in dsnames:

        try:
            m = r_ds.match(ds)
            project, did, short_name = m.group(1), m.group(2), m.group(3)
        except:
            raise Exception(ds)

        versions = [version,] if version is not None else config_samples.default_versions
        ptags = [ptag,] if ptag is not None else config_samples.default_ptags

        path = find_path(project, did, short_name, versions, ptags)

        if not path:
            raise Exception('File not found for ds %s' % (ds))

        dataset = {
            'name': name,
            'project': project,
            'did': did,
            'short_name': short_name,
            'path': path,
            }

        datasets.append(dataset)
                

    return datasets
    

#---------------
# get_histogram
#---------------
def _get_histogram(ds, **kwargs):

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

    use_sfw     = kwargs.get('use_sfw', True)
    use_mcw     = kwargs.get('use_mcw', True)
    use_puw     = kwargs.get('use_puw', False)

    debug      = kwargs.get('debug', False)

    #-----------
    # File/Chain
    #-----------
    tree = ROOT.TChain('mini')
    tree.Add(ds['path'])

    #-----------
    # Histogram
    #-----------
    systname = syst

    if ':' in variable:
        varx, vary = variable.split(':')

    if binning is None:
        binning = get_binning(variable)

    # try: FIX
    #     name = sample.name.split('.')[1]
    # except:
    #     name = sample.name

    if fs is not None:
        hname = 'h%s_%s%s_%s_obs_%s' % (name, fs, systname, region, variable.replace(':', '_'))
    else:
        # to avoid the ROOT warning, not using this name anyway
        hname = 'h%s%s_%s_obs_%s' % (ds['did'], systname, region, variable.replace(':', '_')) 

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

    if 'v3c' in ds['name'] and 'meff' in selection:
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
    if lumi is not None and not 'data' in lumi and float(lumi) < 100:
        lumi = float(lumi) * 1000

    if lumi == 'data15':
        lumi = config_analysis.lumi_data15
    elif lumi == 'data16':
        lumi = config_analysis.lumi_data16
    elif lumi == 'data':
        lumi = config_analysis.lumi_data15 + config_analysis.lumi_data16
        
    if lumi is None:
        lumi = 1000.
    
    w_str = ''
    if ds['project'] == 'mc15_13TeV':

        # lumi weight
        lumi_weight = get_lumi_weight(ds, lumi, fs)        
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
        
    if 'efake' in ds['name']:
        if syst == 'Nom':
            w_str += 'weight_feg'
        elif syst == 'FegLow':
            w_str += 'weight_feg_dn'
        elif syst == 'FegHigh':
            w_str += 'weight_feg_up'

    elif 'jfake' in ds['name']:
        if syst == 'Nom':
            w_str += 'weight_fjg'
        elif syst == 'FjgLow':
            w_str += 'weight_fjg_dn'
        elif syst == 'FjgHigh':
            w_str += 'weight_fjg_up'

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


def get_histogram(name, **kwargs):

    variable   = kwargs.get('variable', 'cuts')
    region     = kwargs.get('region', 'SR')
    syst       = kwargs.get('syst', 'Nom')
    rootfile   = kwargs.get('rootfile', None)

    ptag       = kwargs.get('ptag', None)
    version    = kwargs.get('version', None)

    if '.root' in name:

        # try to identify file
        # name = os.path.basename(sample_name).split('.')[0]

        # return _get_histogram(Sample(name), sample_name, **kwargs)
        return None # FIX

    # if name in ['efake', 'jfake']:

    #     ds_tmp = get_sample_datasets(name, version, ptag)

    #     datasets = dict(ds_tmp)
    #     paths = []
    #     for s in datasets:
    #         s['path'] = s['path'].replace('data15_13TeV', sample_name)

    # else:
    datasets = get_sample_datasets(name, version, ptag)

    if datasets is None:
        return _get_histogram(ds, **kwargs)


    hist = None
                                 
    # ewk grid: sum over all sub-processes
    if 'GGM_mu' in name and len(datasets) == 1:
        pass
    #     relevant_fs = [111, 112, 113, 115, 117, 118, 123, 125, 126, 127, 133, 134, 135, 137, 138, 146, 148, 157, 158, 168]
    #     for fs in relevant_fs:
            
    #         h = _get_histogram(sample.name, sample.paths[0], fs=fs, **kwargs)

    #         if hist is None:
    #             hist = h.Clone()
    #         else:
    #             hist.Add(h, 1)

    
    else:
        
        for ds in datasets:

            #if not os.path.exists(path):
            #             print 'file doesn\'t exist:', path
            #             continue

            h = _get_histogram(ds, **kwargs)

            if hist is None:
                hist = h.Clone()
            else:
                hist.Add(h, 1)

    # fix histogram name
    if name.startswith('data'):
        hname = 'h%s_%s_obs_%s' % (name, region, variable.replace(':', '_'))
    else:
        if syst != 'Nom':
            syst = syst.replace('Up', 'High').replace('Down', 'Low')
            syst = syst.replace('__1up', 'High').replace('__1down', 'Low')

        hname = 'h%s%s_%s_obs_%s' % (name, syst, region, variable.replace(':', '_'))

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
