# Style

import ROOT
from signalgrid import grid_m3_mu, grid_mu

# Labels
atlas_label = '' ##bf{#it{ATLAS}} Preliminary'

data_label   = '#sqrt{s} = 13 TeV, 13.3 fb^{-1}'
data15_label = '#sqrt{s} = 13 TeV, ~3.2 fb^{-1}'
data16_label = '#sqrt{s} = 13 TeV, ~10.1 fb^{-1}'


# Legend labels
labels_dict = dict()
labels_dict['data']         = 'Data'
labels_dict['photonjet']    = '#gamma + jets'
labels_dict['gamjet']       = '#gamma + jets'
labels_dict['tgamma']       = 't#bar{t}#gamma' # /single-t \\gamma'
labels_dict['vgamma']       = 'W#gamma/Z#gamma'
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

mn1_text = 'm_{#tilde{#chi} #kern[-0.8]{#lower[1.2]{#scale[0.6]{1}}} #kern[-1.8]{#lower[-0.6]{#scale[0.6]{0}}}}'

for (m3, mu), (mgl, mn1) in grid_m3_mu.iteritems():

    name = 'GGM_M3_mu_%i_%i' % (m3, mu)
    
    label = 'm_{#tilde{g}} = %i, %s = %i GeV' % (mgl, mn1_text, mn1)

    labels_dict[name] = label

for mu, mn1 in grid_mu.iteritems():

    name = 'GGM_mu_%i' % mu
    
    label = '%s = %i GeV' % (mn1_text, mn1)

    labels_dict[name] = label


# Colours
colors_dict = dict()
colors_dict['data']        = ROOT.kBlack
colors_dict['photonjet']   = '#e55e49' 
colors_dict['gamjet']      = '#e55e49' 
colors_dict['wgamma']      = '#f7fab3'
colors_dict['zllgamma']    = '#f7fab4'
colors_dict['znunugamma']  = '#f7fab5'
colors_dict['zgamma']      = '#f7fab5'
colors_dict['tgamma']      = '#5fe872' 
colors_dict['ttbarg']      = '#5fe872' 
colors_dict['vgamma']      = '#f8f59b' 
colors_dict['efake']       = '#a4cee6'
colors_dict['jfake']       = '#348ABD'
colors_dict['multijet']    = '#348ABD'
colors_dict['wjets']       = '#BCBC93'
colors_dict['zjets']       = '#36BDBD'
colors_dict['vjets']       = '#a4cee6'
colors_dict['ttbar']       = '#32b422'
colors_dict['diphoton']    = '#e5ac49'
colors_dict['vgammagamma'] = '#e5ac49'
colors_dict['others']      = '#676363'
colors_dict['fakes']       = '#676363'

colors_dict['GGM_M3_mu_1400_250']  = '#85ea7a' 
colors_dict['GGM_M3_mu_1400_650']  = '#fa3a92'
colors_dict['GGM_M3_mu_1400_1050'] = '#8453fb'
colors_dict['GGM_M3_mu_1400_1375'] = '#53fb84'

colors_dict['GGM_M3_mu_1600_250']  = '#4e5de4' #'#7a85ea' 
colors_dict['GGM_M3_mu_1600_650']  = '#e44e5d' #'#ea7a85'
colors_dict['GGM_M3_mu_1600_1250'] = '#a77aea'
colors_dict['GGM_M3_mu_1600_1450'] = '#7abdea'

# 2015+2016 (35 ifb) benchmark points 
colors_dict['GGM_M3_mu_2000_250'] = '#4e5de3' # '#5de34e' 
colors_dict['GGM_M3_mu_2000_450'] = '#f90876'
colors_dict['GGM_M3_mu_2000_850'] = '#6021fa'

colors_dict['GGM_M3_mu_2000_1450']  = '#4e5de3' #'#5de34e' 
colors_dict['GGM_M3_mu_2000_1650']  = '#f90876'
colors_dict['GGM_M3_mu_2000_1850'] = '#6021fa'

colors_dict['GGM_mu_150'] = '#a3fb3b' #'#5de34e' 
colors_dict['GGM_mu_450'] = '#f90876'
colors_dict['GGM_mu_850'] = '#6021fa'

# Plot config
class PlotConf():

    def __init__(self, xtitle='', ytitle='', legpos='right', xmin=None, xmax=None, logy=True):
        self.xtitle = xtitle
        self.ytitle = ytitle
        self.legpos = legpos
        self.xmin   = xmin
        self.xmax   = xmax
        self.logy   = logy


plots_conf = dict()
plots_conf['cuts']         = PlotConf('', 'Events', 'right')
plots_conf['ph_n']         = PlotConf('Number of photons', 'Events', 'right')
plots_conf['el_n']         = PlotConf('Number of electrons', 'Events', 'right')
plots_conf['jet_n']        = PlotConf('Number of jets', 'Events', 'right')
plots_conf['ph_pt']        = PlotConf('p_{T}^{#gamma} [GeV]', 'Events / BIN GeV', 'right')
plots_conf['ph_eta']       = PlotConf('Photon #eta', 'Events / BIN GeV', 'right')
plots_conf['ph_phi']       = PlotConf('Photon #phi', 'Events / BIN GeV', 'right')
plots_conf['ph_iso']       = PlotConf('E_{T}^{iso} - 0.022 #times  p_{T} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['ph_pt[0]']     = PlotConf('p_{T}^{#gamma} [GeV]', 'Events / BIN GeV', 'right')
plots_conf['ph_eta[0]']    = PlotConf('Photon #eta', 'Events / BIN GeV', 'right')
plots_conf['ph_phi[0]']    = PlotConf('Photon #phi', 'Events / BIN GeV', 'right')
plots_conf['ph_iso[0]']    = PlotConf('E_{T}^{iso} - 0.022 #times  p_{T} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['met_et']       = PlotConf('E_{T}^{miss} [GeV]', 'Events / BIN GeV', 'right')
plots_conf['met_phi']      = PlotConf('#phi^{miss}', 'Events', 'right')
plots_conf['met_sig']      = PlotConf('E_{T}^{miss} significance', 'Events / BIN', 'right')
plots_conf['met_sumet']    = PlotConf('SumEt [GeV]', 'Events / BIN', 'right')
plots_conf['ht']           = PlotConf('H_{T} [GeV]', 'Events / BIN GeV', 'right')
plots_conf['jet_pt']       = PlotConf('Jet p_{T} [GeV]', 'Events / BIN GeV', 'right')
plots_conf['jet_pt[0]']    = PlotConf('Jet1 p_{T} [GeV]', 'Events / BIN GeV', 'right')
plots_conf['jet_pt[1]']    = PlotConf('Jet2 p_{T} [GeV]', 'Events / BIN GeV', 'right')
plots_conf['jet_eta']      = PlotConf('Jet #eta', 'Events', 'right')
plots_conf['rt2']          = PlotConf('R_{T}^{2}', 'Events', 'left', 0.3, 1.1)
plots_conf['rt4']          = PlotConf('R_{T}^{4}', 'Events / BIN', 'left', 0.3, 1.1)
plots_conf['dphi_jetmet']  = PlotConf('#Delta#phi(jet, E_{T}^{miss})', 'Events', 'right')
plots_conf['dphi_gamjet']  = PlotConf('#Delta#phi(#gamma, jet)', 'Events', 'right')
plots_conf['dphi_gammet']  = PlotConf('#Delta#phi(#gamma, E_{T}^{miss})', 'Events', 'right')
plots_conf['avgmu']        = PlotConf('<#mu>', 'Events', 'right', logy=False)

plots_conf['ht+met_et'] = PlotConf('m_{eff} [GeV]', 'Events / BIN GeV', 'right')
plots_conf['meff']      = PlotConf('m_{eff} [GeV]', 'Events / BIN GeV', 'right')

plots_conf['mgj']    = PlotConf('m_{#gammaj} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['mgjj']   = PlotConf('m_{#gammajj} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['mgjjj']  = PlotConf('m_{#gammajjj} [GeV]', 'Events / (BIN GeV)', 'right')

plots_conf['ph_pt[0]+met_et'] = PlotConf('S_{T}^{#gamma} [GeV]', 'Events / BIN GeV', 'right')
plots_conf['stgam'] = PlotConf('S_{T}^{#gamma} [GeV]', 'Events / BIN GeV', 'right')

plots_conf['mt']  = PlotConf('M_{T}', 'Events / BIN', 'right')
plots_conf['mt2'] = PlotConf('M_{T}^{2}', 'Events / BIN', 'right')

plots_conf['default']  = PlotConf()
