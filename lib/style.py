import ROOT

# Legend labels
labels_dict = dict()
labels_dict['data']         = 'Data'
labels_dict['photonjet']    = '#gamma + jets'
labels_dict['gamjet']       = '#gamma + jets'
labels_dict['ttgamma']       = 't#bar{t}#gamma' # /single-t \\gamma'
labels_dict['vgamma']       = 'W#gamma/Z#gamma'
labels_dict['zgamma']       = 'Z#gamma'
labels_dict['wgamma']       = 'W#gamma'
labels_dict['znngam']       = 'Z(#nu#nu)#gamma'
labels_dict['efake']        = 'e#rightarrow#gamma fake'
labels_dict['jfake']        = 'jet#rightarrow#gamma fake'
labels_dict['multijet']     = 'Multijet'
labels_dict['wjets']        = 'W + jets'
labels_dict['zjets']        = 'Z + jets'
labels_dict['vjets']        = 'W/Z + jets'
labels_dict['ttbar']        = 'tt'
labels_dict['diphoton']     = '#gamma#gamma/W#gamma#gamma/Z#gamma#gamma'
labels_dict['others']       = 'Others'
labels_dict['fakes']        = '#gamma fakes'

labels_dict['zllgamma'] = ''
labels_dict['znunugamma'] = ''

mn1_text = 'm_{#tilde{#chi} #kern[-0.8]{#lower[1.2]{#scale[0.6]{1}}} #kern[-1.6]{#lower[-0.6]{#scale[0.6]{0}}}}'


# GGM MadGraph grid 
from signalgrid import mg_gg_grid, mg_cn_grid

for (m3, mu), (mgl, mn1) in mg_gg_grid.iteritems():
    name = 'GGM_GG_bhmix_%i_%i' % (m3, mu)
    
    label = 'm_{#tilde{g}} = %i, %s = %i GeV' % (mgl, mn1_text, mn1)

    labels_dict[name] = label

for mu, mn1 in mg_cn_grid.iteritems():
    name = 'GGM_CN_bhmix_%i' % mu
    
    label = '%s=%i GeV' % (mn1_text, mn1)

    labels_dict[name] = label


# # Colours
colors_dict = dict()
colors_dict['data']        = ROOT.kBlack
colors_dict['photonjet']   = '#e55e49'
colors_dict['gamjet']      = '#e55e49'
colors_dict['wgamma']      = '#fcdd5d'
colors_dict['zllgamma']    = '#f7fab4'
colors_dict['znunugamma']  = '#f7fab5'
colors_dict['zgamma']      = '#b599cc'
colors_dict['tgamma']      = '#32b43c' 
colors_dict['ttgamma']     = '#32b43c'
colors_dict['vgamma']      = '#f8f59b' 
colors_dict['efake']       = '#a4cee6'
colors_dict['jfake']       = '#348ABD'
colors_dict['multijet']    = '#348ABD'
colors_dict['wjets']       = '#BCBC93'
colors_dict['zjets']       = '#36BDBD'
colors_dict['vjets']       = '#a4cee6'
colors_dict['ttbar']       = '#32b422'
colors_dict['diphoton']    = '#ffa04d'
colors_dict['vgammagamma'] = '#e5ac49'
colors_dict['others']      = '#676363'
colors_dict['fakes']       = '#348ABD'

# MG focus points
colors_dict['GGM_GG_bhmix_1900_150']  = '#3a92fa'
colors_dict['GGM_GG_bhmix_1900_250']  = '#fa3a92'
colors_dict['GGM_GG_bhmix_1900_450']  = '#8453fb'
colors_dict['GGM_GG_bhmix_1900_650']  = '#faa23a'

colors_dict['GGM_GG_bhmix_1900_1450']  = '#3a92fa'
colors_dict['GGM_GG_bhmix_1900_1650']  = '#fa3a92'
colors_dict['GGM_GG_bhmix_1900_1810']  = '#8453fb'
colors_dict['GGM_GG_bhmix_1900_1860']  = '#faa23a'

colors_dict['GGM_CN_bhmix_150'] = '#059bfd' ##4e5de4'
colors_dict['GGM_CN_bhmix_200'] = '#fd059b' #e44e5d'
colors_dict['GGM_CN_bhmix_250'] = '#fd6705' 
colors_dict['GGM_CN_bhmix_450'] = '#6021fa'

# Plot config
plots_conf = {
    'default': {
        'xtitle': '',
        'ytitle': '',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'cuts': {
        'xtitle': '',
        'ytitle': 'Events',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'ph_n': {
        'xtitle': 'Number of photons',
        'ytitle': 'Events',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'el_n': {
        'xtitle': 'Number of electrons',
        'ytitle': 'Events',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'mu_n': {
        'xtitle': 'Number of muons',
        'ytitle': 'Events',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'jet_n': {
        'xtitle': 'Number of jets',
        'ytitle': 'Events',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'bjet_n': {
        'xtitle': 'Number of b-jets',
        'ytitle': 'Events',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'ph_pt': {
        'xtitle': 'p_{T}^{#gamma} [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'ph_eta': {
        'xtitle': 'Photon #eta',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'ph_phi': {
        'xtitle': 'Photon #phi',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'ph_iso': {
        'xtitle': 'E_{T}^{iso} - 0.022 #times  p_{T} [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'ph_pt[0]': {
        'xtitle': 'p_{T}^{leading-#gamma} [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'ph_eta[0]': {
        'xtitle': '#eta^{leading-#gamma}',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'ph_etas2[0]': {
        'xtitle': '#eta_{s2}^{leading-#gamma}',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'ph_phi[0]': {
        'xtitle': '#phi^{leading-#gamma}',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'ph_iso[0]': {
        'xtitle': 'E_{T}^{iso} - 0.022 #times  p_{T} [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'met_et': {
        'xtitle': 'E_{T}^{miss} [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'met_phi': {
        'xtitle': '#phi^{miss} [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'met_sig': {
        'xtitle': 'E_{T}^{miss} Significance [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'met_sumet': {
        'xtitle': 'SumEt [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'ht0': {
        'xtitle': 'H_{T} (only jets) [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'ht': {
        'xtitle': 'H_{T} [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'jet_pt': {
        'xtitle': 'Jet p_{T} [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'jet_pt[0]': {
        'xtitle': 'Leading Jet p_{T} [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'jet_pt[1]': {
        'xtitle': 'Subleading Jet p_{T} [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'jet_eta': {
        'xtitle': 'Jet #eta',
        'ytitle': 'Events',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'rt2': {
        'xtitle': 'R_{T}^{2}',
        'ytitle': 'Events / BIN',
        'legpos': 'left',
        'xmin': 0.3,
        'xmax': 1.1,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'rt4': {
        'xtitle': 'R_{T}^{4}',
        'ytitle': 'Events / BIN',
        'legpos': 'left',
        'xmin': 0.3,
        'xmax': 1.1,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'dphi_jetmet': {
        'xtitle': '#Delta#phi(jet, E_{T}^{miss})',
        'ytitle': 'Events / BIN',
        'legpos': 'top',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'dphi_gamjet': {
        'xtitle': '#Delta#phi(#gamma, jet)',
        'ytitle': 'Events / BIN',
        'legpos': 'top',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'dphi_gammet': {
        'xtitle': '#Delta#phi(#gamma, E_{T}^{miss})',
        'ytitle': 'Events / BIN',
        'legpos': 'top',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'met_soft_et': {
        'xtitle': 'E_{T}^{miss} Soft Term [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'met_gam_et': {
        'xtitle': 'E_{T}^{miss} Photon Term [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'met_jet_et': {
        'xtitle': 'E_{T}^{miss} Jet Term [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },


    'avgmu': {
        'xtitle': '<#mu>',
        'ytitle': 'Events',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': False,
        },

    'meff': {
        'xtitle': 'm_{eff} [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

    'mt': {
        'xtitle': 'M_{T} [GeV]',
        'ytitle': 'Events / BIN GeV',
        'legpos': 'right',
        'xmin': None,
        'xmax': None,
        'ymin': None,
        'ymax': None,
        'logx': False,
        'logy': True,
        },

}

def get_plotconf(variable):

    if ':' in variable:

        varx, vary = variable.split(':')

        if '[' in varx:
            vartmp = varx[:varx.find('[')]
            confx = plots_conf.get(vartmp)
        else:
            confx = plots_conf.get(varx)

        if '[' in vary:
            vartmp = vary[:vary.find('[')]
            confy = plots_conf.get(vartmp)
        else:
            confy = plots_conf.get(vary)

        if confx is None:
            confx = plots_conf['default']
        if confy is None:
            confy = plots_conf['default']

        return confx, confy

    else:
        return plots_conf.get(variable, plots_conf['default'])
