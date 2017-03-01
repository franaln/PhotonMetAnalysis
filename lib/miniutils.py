# single photon analysis
# mini->histogram machinery

import os
import re
import ROOT
from array import array

from rootutils import RootFile, Value, histogram, histogram_equal_to

import xsutils
import systematics

# config
import analysis
import samples
import binning

MiniDir1  = '/ar/pcunlp001/raid/falonso/mini2'
MiniDir2  = '/ar/pcunlp002/disk/falonso/mini2'

# FS for EWK samples
relevant_fs = [111, 112, 113, 115, 117, 118, 123, 125, 126, 127, 133, 134, 135, 137, 138, 146, 148, 157, 158, 168]

# Load macros
ROOT.gInterpreter.Declare(open(os.environ['SUSY_ANALYSIS'] + '/lib/variables.cxx').read())

variable_aliases = {
    'photontype': 'photontype(ph_truth_type[0], ph_truth_origin[0])',
}

# --------
# Binning
#---------
def get_binning_single_variable(variable):

    binning_ = binning.bins.get(variable, None)

    if binning_ is None and '[' in variable and ']' in variable:
        binning_ = binning.bins.get(variable[:variable.index('[')], None)

    if variable is None:
        for variable_ in binning.bins.iterkeys():
            if variable_ in variable:
                binning_ = binning.bins[variable_]
                break

    if binning_ is None:
        try:
            binning_ = binning.bins.get(variable.split('_')[1], None)
        except:
            binning_ = None

    if binning_ is None:
        try:
            binning_ = binning.bins.get(variable.split('_')[0], None)
        except:
            binning_ = None

    if binning_ is None and 'ht+' in variable:
        binning_ = binning.bins.get('meff', None)

    return binning_


def get_binning(variable):

    if ':' in variable and not '::' in variable:
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
def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def split_cut(s):
    s = s.strip()
    for op in ['==', '>=', '<=', '>', '<', '!=']:
        if op in s:
            var, value = s.split(op)
            break

    return (var.strip(), op, value.strip())

def revert_cut(s):
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


#----------------------------
# Cross section/lumi weights
#----------------------------
def get_xs(ds):

    xs = xsutils.get_xs_did(int(ds['did']))[0]

    if xs is None:
        print 'missing XS for this ID:', did
        return 0.0
    
    return xs


def get_signal_xs(ds, fs=0):

    if 'GGM_M3' in ds['short_name']:

        xs, unc = xsutils.get_xs_did(ds['did'])

        return xs

    elif 'GGM_mu' in ds['short_name']:

        xs, unc = xsutils.get_xs_did(ds['did'], fs=fs)

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

    weight = 1.
    if ds['project'] == 'mc15_13TeV':

        if 'GGM_mu' in ds['short_name'] and fs is not None:
            mu = int(re.findall(ur'GGM_mu_(\d*)', ds['short_name'])[0])
            sumw = xsutils.get_ewk_sumw(mu, fs)
        else:
            sumw = get_sumw(ds)
    
        xs = xsutils.get_xs_did(int(ds['did']), fs)[0]

        try:
            weight = (lumi * xs) / sumw
        except:
            weight = 0.

    return weight


#----------
# Samples
#----------
def get_datasets_names(name): 

    ds_tmp = samples.samples_dict.get(name)

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
 

r_ds = re.compile('(mc15_13TeV|data15_13TeV|data16_13TeV|efake15|efake16|efake15m|efake15t|efake16m|efake16t|jfake15|jfake16)\.([0-9]*)\.(.*)')

def find_path(project, did, short_name, versions, ptags):

    for version in versions:

        vtag = ''
        if '_' in version:
            vtag    = '_' + version.split('_')[1]
            version = version.split('_')[0]

        for ptag in ptags:
            path = '%s/v%s/%s.%s.%s.mini.p%s.v%s%s_output.root' % (MiniDir1, version, project, did, short_name, ptag, version, vtag)
            if os.path.isfile(path):
                return path

    return ''

def get_did(name):

    # get datasets corresponding to sample
    dsnames = get_datasets_names(name)

    if not dsnames:
        raise Exception('sample %s not found in samples.py' % name)

    for ds in dsnames:
        try:
            m = r_ds.match(ds)
            project, did, short_name = m.group(1), m.group(2), m.group(3)
        except:
            raise Exception(ds)

        return did


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

        versions = [version,] if version is not None else analysis.versions
        ptags = [ptag,] if ptag is not None else analysis.ptags

        path = find_path(project, did, short_name, versions, ptags)

        if not path:
            raise Exception('File not found for ds %s with version %s and ptag %s. (Available ptags: %s)' % (ds, version, ptag, ','.join(ptags)))

        dataset = {
            'name': name,
            'project': project,
            'did': did,
            'short_name': short_name,
            'path': path,
            }

        datasets.append(dataset)
                
    return datasets
    

#----------
# get_mini
#----------
def get_mini(name, **kwargs):

    ptag       = kwargs.get('ptag', None)
    version    = kwargs.get('version', None)
    lumi       = kwargs.get('lumi', None)

    if lumi is not None:
        try: 
            if float(lumi) < 100:
                lumi = float(lumi) * 1000
        except:
            pass

        if lumi == 'data15':
            lumi = analysis.lumi_data15
        elif lumi == 'data16':
            lumi = analysis.lumi_data16
        elif lumi == 'data':
            lumi = analysis.lumi_data15 + analysis.lumi_data16
        
    if lumi is None:
        lumi = 1000.

    datasets = get_sample_datasets(name, version, ptag)

    if datasets is None:
        return None

    # ewk: not implemented
    # if 'GGM_mu' in name and len(datasets) == 1 and 'fs' not in kwargs:
    #     pass

    weights = []
    for ds in datasets:
        if ds['project'] == 'mc15_13TeV':
            lumi_weight = get_lumi_weight(ds, lumi)
            weights.append(lumi_weight)
        else:
            weights.append(None)

    return datasets, weights


#---------------
# get_histogram
#---------------
def get_escaped_variable(variable):
    return variable.replace(':', '_').replace('/', '').replace('(', '').replace(')', '')

def _get_histogram(ds, **kwargs):

    variable   = kwargs.get('variable', 'cuts')
    region     = kwargs.get('region', 'SR')
    selection  = kwargs.get('selection', '')
    syst       = kwargs.get('syst', 'Nom')
    scale      = kwargs.get('scale', True)
    truth      = kwargs.get('truth', False)
    lumi       = kwargs.get('lumi', None)
    binning    = kwargs.get('binning', None)
    version    = kwargs.get('version', None)
    fs         = kwargs.get('fs', None)
    year       = kwargs.get('year', None)

    do_remove_var = kwargs.get('remove_var', False)
    do_revert_cut = kwargs.get('revert_cut', False)

    use_lumiw   = kwargs.get('use_lumiw',   True)
    use_sfw     = kwargs.get('use_sfw',     True)
    use_mcw     = kwargs.get('use_mcw',     True)
    use_purw    = kwargs.get('use_purw',    True) #False) 
    use_mcveto  = kwargs.get('use_mcveto',  True)

    debug = kwargs.get('debug', False)

    is_mc = (ds['project'] == 'mc15_13TeV')

    #-----------
    # File/Chain
    #-----------
    tree = ROOT.TChain('mini')
    tree.Add(ds['path'])

    #-----------
    # Histogram
    #-----------
    systname = syst

    if ':' in variable and '::' not in variable:
        varx, vary = variable.split(':')

    if binning is None:
        binning = get_binning(variable)

    if fs is not None:
        hname = 'h%s_%s%s_%s_obs_%s' % (ds['did'], fs, systname, region, get_escaped_variable(variable))
    else:
        # to avoid the ROOT warning, not using this name anyway
        hname = 'h%s%s_%s_obs_%s' % (ds['did'], systname, region, get_escaped_variable(variable))

    if ':' in variable and '::' not in variable:
        htemp = ROOT.TH2D(hname, hname, *binning)
        htemp.Sumw2()
    else:
        if len(binning) > 3:
            htemp = ROOT.TH1D(hname, hname, len(binning)-1, array('d', binning))
        else:
            htemp = ROOT.TH1D(hname, hname, *binning)
        htemp.Sumw2()


    # Variable
    variable = variable_aliases.get(variable, variable) # check if alias


    #-----------
    # Selection
    #-----------
    # reverse variable cut to blind region
    if do_revert_cut and variable in selection and not variable == 'cuts':
        new_cuts = []

        for cut in selection.split('&&'):
            if split_cut(cut)[0] == variable:
                new_cuts.append(revert_cut(cut))
            else:
                new_cuts.append(cut)

        selection = '&&'.join(new_cuts)

    elif do_revert_cut and variable not in selection and variable != 'cuts':
        return None

    # remove variable from selection if n-1
    elif do_remove_var and variable in selection and not variable == 'cuts':
        selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == variable ])
    
    if do_remove_var and (':' in variable):
        if varx in selection:
            selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == varx ])
        if vary in selection:
            selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == vary ])

    if is_mc and fs is not None:
        if selection:
            selection = selection + ' && fs==%s' % fs
        else:
            selection = 'fs==%s' % fs

    if year is not None:
        if selection:
            selection = selection + ' && year==%s' % year
        else:
            selection = 'year==%s' % year

    if is_mc and use_mcveto:
        if selection:
            selection = '%s && mcveto==0' % selection
        else:
            selection = 'mcveto==0'


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
    if lumi is not None:
        try:
            if float(lumi) < 100:
                lumi = float(lumi) * 1000
        except:
            pass

    if lumi == 'data15':
        lumi = analysis.lumi_data15
    elif lumi == 'data16':
        lumi = analysis.lumi_data16
    elif lumi == 'data':
        lumi = analysis.lumi_data
        
    # by default normalize to 1 ifb
    if lumi is None:
        lumi = 1000.

    w_list = []
    if is_mc and scale:

        # lumi weight
        if use_lumiw:
            lumi_weight = get_lumi_weight(ds, lumi, fs)        
            w_list.append('%s' % lumi_weight)

        # mc weight
        if use_mcw:
            w_list.append('weight_mc')

        # scale factors (btag SF is already included (?))
        if use_sfw:
            if syst != 'Nom' and systematics.affects_weight(syst) and not 'PRW_DATASF' in syst:
                w_list.append('weight_sf_%s' % syst)
            else:
                w_list.append('weight_sf')

        # pile-up
        if use_purw:
            if syst == 'Nom':
                w_list.append('weight_pu')
            elif 'PRW_DATASF__1down' == syst:
                w_list.append('weight_pu_down')
            elif 'PRW_DATASF__1up' == syst:
                w_list.append('weight_pu_up')

        
    if 'efake' in ds['name']:
        if syst == 'Nom':
            w_list.append('weight_feg')
        elif syst == 'FegLow':
            w_list.append('weight_feg_dn')
        elif syst == 'FegHigh':
            w_list.append('weight_feg_up')

    elif 'jfake' in ds['name']:
        if syst == 'Nom':
            w_list.append('weight_fjg')
        elif syst == 'FjgLow':
            w_list.append('weight_fjg_dn')
        elif syst == 'FjgHigh':
            w_list.append('weight_fjg_up')

    if not scale:
        w_str = ''
    else:
        w_str = '*'.join(w_list)


    #-----------------
    # Create histogram
    #-----------------
    varexp = ''
    if selection and w_str:
        varexp = '(%s)*(%s)' % (selection, w_str)
    elif selection:
        varexp = selection
    elif scale:
        varexp = w_str

    if debug:
        print 'get_histogram:', hname, variable, varexp

    if variable == 'cuts':
        tree.Project(hname, '1', varexp)

        hist = histogram_equal_to(htemp)
        error = ROOT.Double(0.0)
        integral = htemp.IntegralAndError(1, hist.GetNbinsX()+1, error)

        hist.SetBinContent(1, integral)
        hist.SetBinError(1, error)

    elif ':' in variable and not '::' in variable:
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

    ismc       = kwargs.get('ismc', False)

    if name.endswith('.root'):
        # try to identify file
        dname = os.path.basename(name).replace('.root', '')

        if ismc:
            project, did = 'mc15_13TeV', 0
        else:
            project, did = 'data15_13TeV', 0

        dataset = {
            'name': dname,
            'project': project,
            'did': did,
            'short_name': dname,
            'path': name,
            }

        hist = None

        if 'GGM_mu' in name and 'fs' not in kwargs:
            for fs in relevant_fs:
                h = _get_histogram(dataset, fs=fs, **kwargs)
                if hist is None:
                    hist = h.Clone()
                else:
                    hist.Add(h, 1)

        else:
            hist = _get_histogram(dataset, **kwargs)


        return hist

    datasets = get_sample_datasets(name, version, ptag)

    if datasets is None:
        return _get_histogram(ds, **kwargs)


    hist = None
                                 
    # ewk grid: sum over all sub-processes
    if 'GGM_mu' in name and len(datasets) == 1 and 'fs' not in kwargs:

        for fs in relevant_fs:
            
            h = _get_histogram(datasets[0], fs=fs, **kwargs)

            if hist is None:
                hist = h.Clone()
            else:
                hist.Add(h, 1)
                
    else:
        
        for ds in datasets:

            h = _get_histogram(ds, **kwargs)

            if h is None:
                return None

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
def get_cutflow(sample, selection='', scale=True, lumi=None, preselection=False, **kwargs):

    if not selection:
        return None

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

        evts = get_events(sample, selection=selection, lumi=lumi, scale=scale, **kwargs)

        cutflow.SetBinContent(i+1, evts.mean)
        cutflow.SetBinError(i+1, evts.error)


    if preselection:

        if '.root' in sample:
            ds = [sample, ]
        else:
            if 'version' in kwargs:
                ds = get_sample_datasets(sample, kwargs['version'])
            else:
                ds = get_sample_datasets(sample)

        h_preselection = None
        for s in ds:

            f = ROOT.TFile.Open(s['path'])
            htmp = f.Get('cutflow_w')

            # Weight
            if lumi is not None:
                try: 
                    if float(lumi) < 100:
                        lumi = float(lumi) * 1000
                except:
                    pass

            if lumi == 'data15':
                lumi = analysis.lumi_data15
            elif lumi == 'data16':
                lumi = analysis.lumi_data16
            elif lumi == 'data':
                lumi = analysis.lumi_data15 + analysis.lumi_data16
        
            if lumi is None:
                lumi = 1000.

            if scale and 'data' not in sample:
                lumi_weight = get_lumi_weight(s, lumi)
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
