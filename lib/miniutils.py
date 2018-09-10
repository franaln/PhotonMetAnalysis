# single photon analysis
# mini->histogram machinery

import os
import re
import sys
import glob
from array import array

import ROOT
from rootutils import Value, histogram, histogram_equal_to
import multidraw

from samples import samples_dict, samples_r20_dict;
from binning import  binning_dict
import xsutils
import systematics as systematics_
import regions as regions_

MiniDirs = [
    '/eos/user/f/falonso/data/mini2',
    ]

# Mini version
versions_ = ['56', ] # v56: last r20.7 version used for paper (not used for r21)

# Luminosity
lumi_dict = {
    '2015':  3219.56,
    '2016': 32965.30,
    '2017': 44307.40,  ## CHECK/UPDATE
}

# --------
# Binning
#---------
def get_binning_single_variable(variable):

    binning = binning_dict.get(variable, None)

    if binning is None and '[' in variable and ']' in variable:
        binning = binning_dict.get(variable[:variable.index('[')], None)

    if variable is None:
        for var in binning_dict.iterkeys():
            if var in variable:
                binning = binning_dict[var]
                break

    if binning is None:
        try:
            binning = binning_dict.get(variable.split('_')[1], None)
        except:
            binning = None

    if binning is None:
        try:
            binning = binning_dict.get(variable.split('_')[0], None)
        except:
            binning = None

    if binning is None and 'dphi' in variable:
        binning = binning_dict.get('dphi', None)

    return binning


def get_binning(variable):

    if ':' in variable and not '::' in variable:
        varx, vary = variable.split(':')

        binning_x = get_binning_single_variable(varx)
        binning_y = get_binning_single_variable(vary)

        binning = binning_x + binning_y
    else:
        binning = get_binning_single_variable(variable)

    if binning is None:
        print 'Not bins configured for this variable %s. Using default binning' % variable
        binning = binning_dict['default']

    return binning


#------------
# Cuts utils
#------------
def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def split_selection(s):

    selection = []

    for cut in s.split('&&'):
        cut = cut.strip()
        if cut.startswith('(') and cut.endswith(')'):
            try:
                cut1, cut2 = cut[1:-1].split('&&')
                selection.append(cut1)
                selection.append(cut2)
            except:
                cut1, cut2 = cut[1:-1].split('||')
                selection.append(cut1)
                selection.append(cut2)
        else:
            selection.append(cut)

    return selection


def split_cut(s):
    s = s.strip()
    for op in ['==', '>=', '<=', '>', '<', '!=']:
        if op in s:
            var, value = s.split(op)
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


def replace_var(selection, oldvar, newvar):

    new_cuts = []
    for cut in split_selection(selection):
        if split_cut(cut)[0] == oldvar:
            new_cuts.append(cut.replace(oldvar, newvar))
        else:
            new_cuts.append(cut)

    return '&&'.join(new_cuts)


#---------------------------
# Cross section/lumi weight
#---------------------------
def get_sumw(ds):

    sumw = 0
    f = ROOT.TFile.Open(ds['path'])

    tmp = f.Get('events')
    sumw = tmp.GetBinContent(3) # bin 3 is the initial sumw

    f.Close()

    return sumw


def get_lumi_weight(ds, lumi, fs=None):

    luminosity = float(lumi)

    if not ds['project'].startswith('mc'):
        return 1.

    sumw = get_sumw(ds)

    xs = xsutils.get_xs_from_did(int(ds['did']))

    try:
        weight = (luminosity * xs) / sumw
    except:
        weight = 0.
        
    return weight


#----------
# Samples
#----------

r_ds = re.compile('(mc15_13TeV|mc16_13TeV|data15_13TeV|data16_13TeV|data17_13TeV|efake15|efake16|efak17|jfake15|jfake16|jfake17)\.([0-9]*)\.(.*)')

def find_path(project, did, short_name, version, mc_campaign):

    if project.startswith('mc') and mc_campaign is not None:
        guess_path = 'v%s/%s.%s.%s.mini.%s.p*.v%s_output.root' % (version, project, did, short_name, mc_campaign, version)
    else:
        guess_path = 'v%s/%s.%s.%s.mini.p*.v%s_output.root' % (version, project, did, short_name, version)

    for mini_dir in MiniDirs:

        full_guess_path = '%s/%s' % (mini_dir, guess_path)

        try:
            paths = glob.glob(full_guess_path)

            if paths:
                # TODO: sort by ptag and choose the latest
                return paths[0]
        except:
            pass


    return None


def get_dsnames(name, version):

    if version == '56':
        ds_tmp = samples_r20_dict.get(name)
    else:
        ds_tmp = samples_dict.get(name)

    dsnames = []
    if isinstance(ds_tmp, str):
        if '+' in ds_tmp:
            names = [ i.strip() for i in ds_tmp.split('+')  if i ]
            for name in names:
                dsnames += get_dsnames(name, version)
        else:
            dsnames.append(ds_tmp)

    else:
        dsnames = ds_tmp

    return dsnames

def get_datasets(name, version=None, mc_campaign=None, ignore_missing=False):

    # get datasets corresponding to sample
    dsnames = get_dsnames(name, version)

    if not dsnames:
        raise Exception('Sample %s not found in samples.py' % name)

    datasets = []
    for ds in dsnames:

        try:
            m = r_ds.match(ds)
            project, did, short_name = m.group(1), m.group(2), m.group(3)
        except:
            raise Exception(ds)

        path = find_path(project, did, short_name, version, mc_campaign)

        if not path:
            if ignore_missing:
                continue
            else:
                raise Exception('File not found for ds %s with version %s.' % (ds, version))

        dataset = {
            'name': name,
            'project': project,
            'mc_campaign': mc_campaign,
            'did': did,
            'short_name': short_name,
            'path': path,
            }

        datasets.append(dataset)

    return datasets
    

#---------------
# Histogram
#---------------
def is_2d_variable(variable):
    return ':' in variable and not '::' in variable

def get_escaped_variable(variable):
    return variable.replace(':', '_').replace('/', '').replace('(', '').replace(')', '')


def _get_multi_histograms(ds, **kwargs):

    """
    get histogram for a given sample (ds) and year

    """

    regions     = kwargs.get('regions', [])
    selections  = kwargs.get('selections', [])
    variables   = kwargs.get('variables', [])
    systematics = kwargs.get('systematics', ['Nom',])

    lumi  = kwargs.get('lumi')
    scale = kwargs.get('scale', True)

    use_lumiw   = kwargs.get('use_lumiw',   True)
    use_sfw     = kwargs.get('use_sfw',     True)
    use_mcw     = kwargs.get('use_mcw',     True)
    use_purw    = kwargs.get('use_purw',    True)
    use_mcveto  = kwargs.get('use_mcveto',  True)

    do_remove_var  = kwargs.get('do_remove_var',  False)

    is_mc = ds['project'].startswith('mc')
    is_fake = ('efake' in ds['name'] or 'jfake' in ds['name'])

    #-----------
    # File/Chain
    #-----------
    file_ = ROOT.TFile.Open(ds['path'])
    tree = file_.Get('mini')

    # Lumi weight is the same for all histograms
    if is_mc and use_lumiw:
        lumi_weight = get_lumi_weight(ds, lumi)

    #---------------------------------------------
    # Create histograms and "tuples" for MultiDraw
    #---------------------------------------------
    draw_list  = []
    histograms = []

    if regions and selections:
        # check if same size ...
        pass
    elif regions and not selections:
        selections = [ getattr(regions_, reg) for reg in regions ]
    elif selections and not regions:
        regions = [ 'R' for sel in selections ]
    

    for region, selection in zip(regions, selections):
        for variable in variables:
            for syst in systematics:

                systname = syst

                # fix_events_by_interval = False
                if is_2d_variable(variable):
                    varx, vary = variable.split(':')

                binning = kwargs.get('binning', None) # only valid from get_histogram
                if binning is None:
                    binning = get_binning(variable)

                # name to avoid the ROOT warning, not used
                hname = 'h__%s__%s_%s_obs_%s' % (ds['did'], systname, region, variable)
    
                if is_2d_variable(variable):
                    htemp = ROOT.TH2D(hname, hname, *binning)
                    htemp.Sumw2()
                else:
                    if len(binning) > 3:
                        if nominal_width is not None:
                            fix_events_by_interval = True
                        htemp = ROOT.TH1D(hname, hname, len(binning)-1, array('d', binning))
                    else:
                        htemp = ROOT.TH1D(hname, hname, int(binning[0]), binning[1], binning[2])
                    htemp.Sumw2()

                # # Variable
                # if ':' in variable and '::' not in variable:
                #     varx = variable_aliases.get(varx, varx)
                #     vary = variable_aliases.get(vary, vary)
                # else:
                #     variable = variable_aliases.get(variable, variable) # check if alias

                # Selection

                ## MC veto
                if is_mc and use_mcveto:
                    if selection:
                        selection = '%s && mcveto==0' % selection
                    else:
                        selection = 'mcveto==0'

                ## Remove variable from selection if n-1
                if do_remove_var and variable in selection and not variable == 'cuts':
                    selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == variable ])
    
                # if do_remove_var and (':' in variable):
                #     if varx in selection:
                #         selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == varx ])
                #     if vary in selection:
                #         selection = '&&'.join([ cut for cut in selection.split('&&') if not split_cut(cut)[0] == vary ])

            
                ## change selection and variable for systematics
                if syst != 'Nom' and systematics_.affects_kinematics(syst):
                    for var in systematics_.get_affected_variables(syst):
                        selection = replace_var(selection, var, '%s_%s' % (var, syst))
                    
                # Weights
                w_list = []
                if is_mc:

                    # lumi weight
                    if use_lumiw:
                        w_list.append('%s' % lumi_weight)

                    # mc weight
                    if use_mcw:
                        w_list.append('weight_mc')

                    # scale factors (btag SF is already included (?))
                    if use_sfw:
                        if syst != 'Nom' and systematics_.affects_weight(syst) and not 'PRW_DATASF' in syst:
                            w_list.append('weight_sf_%s' % syst)
                        else:
                            w_list.append('weight_sf')

                    # pile-up
                    if use_purw:
                        if 'PRW_DATASF__1down' == syst:
                            w_list.append('weight_pu_down')
                        elif 'PRW_DATASF__1up' == syst:
                            w_list.append('weight_pu_up')
                        else:
                            w_list.append('weight_pu')

                elif is_fake:
                    if syst == 'Nom':
                        w_list.append('weight_ff')
                    elif syst == 'EFAKE_SYST__1down' or syst == 'JFAKE_SYST__1down':
                        w_list.append('weight_ff_dn')
                    elif syst == 'EFAKE_SYST__1up' or syst == 'JFAKE_SYST__1up':
                        w_list.append('weight_ff_up')

                if not scale:
                    w_str = ''
                else:
                    w_str = '*'.join(w_list)

                # Add histogram and draw tuple
                varexp = ''
                if selection and w_str:
                    varexp = '(%s)*(%s)' % (selection, w_str)
                elif selection:
                    varexp = selection
                elif scale:
                    varexp = w_str

                histograms.append(htemp)

                if variable == 'cuts':
                    draw_list.append((hname, '1', varexp))
                else: 
                    draw_list.append((hname, variable, varexp))


    # Use MutiDraw to project all histograms
    if len(draw_list) > 1:
        tree.MultiDraw(*draw_list)
    else:
        hname, variable, selection = draw_list[0]
        tree.Project(hname, variable, selection)


    for hist in histograms:
        hist.SetDirectory(0)

    file_.Close()

    return histograms


def sum_histograms(histograms):
    """
    histograms: list of list of histograms, e.g. [(h1, h2, h3), (h4, h5, h6)]
    return: [h1+h4, h2+h5, h3+h6]
    """
    new_histograms = []

    for hlist in zip(*histograms):
        hist = hlist[0].Clone()
        for h in hlist[1:]:
            hist.Add(h, 1)

        new_histograms.append(hist)

    return new_histograms


def print_progressbar(name, total, progress):

    bar_length, status = 60, ""
    progress = float(progress) / float(total)
    if progress >= 1.:
        progress, status = 1, "\r\n"
    block = int(round(bar_length * progress))
    text = "\rProcessing {:10}  [{}] {:.0f}% {}".format(name, 
        "#" * block + "-" * (bar_length - block), round(progress * 100, 0),
        status)
    sys.stdout.write(text)
    sys.stdout.flush()


def get_histograms(name, **kwargs):

    """
    get histograms for a given sample (name)
    and some regions, variables, systematics
    """

    year = kwargs.get('year')
    version = kwargs.get('version', None)
    is_mc = (not 'data' in name and not 'efake' in name and not 'jfake' in name)

    if '+' in year and (not is_mc or year!='2015+2016'):

        del kwargs['year']

        years = year.split('+')

        return sum_histograms([ get_histograms(name, year=y, **kwargs) for y in years ])


    # Data type/MC campaign 
    mc_campaign = None
    if is_mc:
        if year in ('2015', '2016', '2015+2016'):
            mc_campaign = 'mc16a'
        elif year == '2017':
            mc_campaign = 'mc16d'
    elif name in ['data', 'efake', 'jfake']:
        name = name+year[-2:]

    # lumi
    lumi = 0.
    if is_mc:
        if year == '2015+2016':
            lumi = lumi_dict['2015'] + lumi_dict['2016']
        else:
            lumi = lumi_dict[year]

        kwargs['lumi'] = lumi
       

    datasets = get_datasets(name, version, mc_campaign, kwargs.get('ignore_missing', False))

    histograms = []

    print_progressbar(name, len(datasets), 0) 
    for ids, ds in enumerate(datasets):

        histograms_ds = _get_multi_histograms(ds, **kwargs)

        if not histograms:
            for hist in histograms_ds:
                histograms.append(hist.Clone())
        else:
            for hall, hnew in zip(histograms, histograms_ds):
                hall.Add(hnew, 1)

        print_progressbar(name, len(datasets), ids+1) 


    # Fix histogram name
    replace_dict = {
        'efake15': 'efake',
        'efake16': 'efake',
        'efake17': 'efake',
        'jfake15': 'jfake',
        'jfake16': 'jfake',
        'jfake17': 'jfake',
        'data15Nom': 'data',
        'data16Nom': 'data',
        'data17Nom': 'data',
        }

    for hist in histograms:
        hname = hist.GetName()

        to_replace = '__' + hname.split('__')[1] + '__'

        new_hname = hname.replace(to_replace, name)

        for i, j in replace_dict.iteritems():
            if i in new_hname:
                new_hname = new_hname.replace(i, j)

        hist.SetName(new_hname)

    return histograms


def get_histogram(name, **kwargs):

    variable   = kwargs.get('variable', 'cuts')
    region     = kwargs.get('region', '')
    selection  = kwargs.get('selection', '')
    syst       = kwargs.get('syst', 'Nom')

    histograms = get_histograms(name, variables=[variable,], regions=[region,], selections=[selection,], systematics=[syst,], **kwargs)

    if histograms:
        return histograms[0]

    return None


def get_events(name, **kwargs):

    hist = get_histogram(name, variable='cuts', **kwargs)

    mean = hist.GetBinContent(1)
    error = hist.GetBinError(1)

    hist.Delete()

    return Value(mean, error)


def get_multi_events(name, **kwargs):

    histograms = get_histograms(name, variable='cuts', **kwargs)

    hlist = []

    for hist in histograms:

        name = hist.GetName()

        mean  = hist.GetBinContent(1)
        error = hist.GetBinError(1)

        hlist.append( (name, mean, error) ) 


    return hlist


