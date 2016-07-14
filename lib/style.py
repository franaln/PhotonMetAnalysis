# Style

import ROOT
from mass_dict import mass_dict

# Legend labels
labels_dict = dict()
labels_dict['data']         = 'Data'
labels_dict['photonjet']    = '#gamma + jets'
labels_dict['gamjet']       = '#gamma + jets'
labels_dict['tgamma']       = 't#bar{t} #gamma' # /single-t #gamma'
labels_dict['vgamma']       = 'W/Z #gamma'
labels_dict['znngam']       = 'Z(#nu#nu) #gamma'
labels_dict['efake']        = 'e#rightarrow#gamma fake'
labels_dict['jfake']        = 'jet#rightarrow#gamma fake'
labels_dict['multijet']     = 'Multijet'
labels_dict['wjets']        = 'W + jets'
labels_dict['zjets']        = 'Z + jets'
labels_dict['vjets']        = 'W/Z + jets'
labels_dict['ttbar']        = 't#bar{t}'
labels_dict['diphoton']     = '#gamma#gamma / W/Z#gamma#gamma'

mn1_text = 'm_{#tilde{#chi} #kern[-0.8]{#lower[1.2]{#scale[0.6]{1}}} #kern[-1.8]{#lower[-0.6]{#scale[0.6]{0}}}}'

for (m3, mu), (mgl, mn1) in mass_dict.iteritems():

    name = 'GGM_M3_mu_%i_%i' % (m3, mu)
    
    label = 'm_{#tilde{g}} = %i, %s = %i GeV' % (mgl, mn1_text, mn1)

    labels_dict[name] = label


# Colours
colors_dict = dict()
colors_dict['data']       = ROOT.kBlack
colors_dict['photonjet']  = '#e55e49' #'#E24A33'
colors_dict['gamjet']     = '#e55e49' #'#E24A33'
colors_dict['wgamma']     = '#f7fab3'
colors_dict['zllgamma']   = '#f7fab4'
colors_dict['znunugamma'] = '#f7fab5'
colors_dict['zgamma']     = '#f7fab5'
colors_dict['tgamma']     = '#5fe872' #'#49e55e'
colors_dict['ttbarg']     = '#5fe872' #'#49e55e'
colors_dict['vgamma']     = '#f8f59b' #'#f7fab3' #'#f7fab3'
colors_dict['efake']      = '#a4cee6'
colors_dict['jfake']      = '#348ABD'
colors_dict['multijet']   = '#348ABD'
colors_dict['wjets']      = '#BCBC93'
colors_dict['zjets']      = '#36BDBD'
colors_dict['vjets']      = '#a4cee6'
colors_dict['ttbar']      = '#32b422'
colors_dict['diphoton']   = '#e5ac49'
colors_dict['vgammagamma'] = '#e5ac49'

colors_dict['GGM_M3_mu_1400_250']  = '#85ea7a' 
colors_dict['GGM_M3_mu_1400_650']  = '#fa3a92'
colors_dict['GGM_M3_mu_1400_1050'] = '#8453fb'
colors_dict['GGM_M3_mu_1400_1375'] = '#53fb84'

colors_dict['GGM_M3_mu_1600_250']  = '#85ea7a' 
colors_dict['GGM_M3_mu_1600_650']  = '#fa3a92'
colors_dict['GGM_M3_mu_1600_1250'] = '#8453fb'
colors_dict['GGM_M3_mu_1600_1450'] = '#53fb84'

# Plot config
plots_conf = dict()
plots_conf['cuts']         = ('', 'Events', 'right')
plots_conf['ph_n']         = ('Number of photons', 'Events', 'right')
plots_conf['el_n']         = ('Number of electrons', 'Events', 'right')
plots_conf['jet_n']        = ('Number of jets', 'Events', 'right')
plots_conf['ph_pt']        = ('p_{T}^{#gamma} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['ph_eta']       = ('Photon #eta', 'Events / (BIN GeV)', 'right')
plots_conf['ph_phi']       = ('Photon #phi', 'Events / (BIN GeV)', 'right')
plots_conf['ph_iso']       = ('Isolation (Etcone20) [GeV]', 'Events (1/BIN GeV)', 'right')
plots_conf['met_et']       = ('E_{T}^{miss} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['met_phi']      = ('#phi^{miss}', 'Events', 'right')
plots_conf['ht']           = ('H_{T} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['jet_pt']       = ('Jet p_{T} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['jet_pt[0]']    = ('Jet1 p_{T} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['jet_pt[1]']    = ('Jet2 p_{T} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['jet_eta']      = ('Jet #eta', 'Events', 'right')
plots_conf['rt2']          = ('R_{T}^{2}', 'Events', 'left', 0.3, 1.1)
plots_conf['rt4']          = ('R_{T}^{4}', 'Events / BIN', 'left', 0.3, 1.1)
plots_conf['dphi_jetmet']  = ('#Delta#phi(jet, E_{T}^{miss})', 'Events', 'right')
plots_conf['dphi_gamjet']  = ('#Delta#phi(#gamma, jet)', 'Events', 'right')
plots_conf['dphi_gammet']  = ('#Delta#phi(#gamma, E_{T}^{miss})', 'Events', 'right')

plots_conf['ht+met_et'] = ('M_{eff} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['meff']      = ('M_{eff} [GeV]', 'Events / (BIN GeV)', 'right')

plots_conf['mgj']    = ('m_{#gammaj} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['mgjj']   = ('m_{#gammajj} [GeV]', 'Events / (BIN GeV)', 'right')
plots_conf['mgjjj']  = ('m_{#gammajjj} [GeV]', 'Events / (BIN GeV)', 'right')

plots_conf['default'] = ('','', 'right')
