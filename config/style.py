# Style

import ROOT

# Legend labels
labels_dict = dict()
labels_dict['data']   = 'Data 2015'
labels_dict['photonjet'] = '#gamma + jets'
labels_dict['gamjet']    = '#gamma + jets'
labels_dict['photonjet_25ns'] = '#gamma + jets'
labels_dict['tgamma'] = 't#bar{t} #gamma' # /single-t #gamma'
labels_dict['vgamma'] = 'W/Z #gamma'
labels_dict['znngam'] = 'Z(#nu#nu) #gamma'
labels_dict['efake']  = 'e#rightarrow#gamma fake'
labels_dict['jfake']  = 'jet#rightarrow#gamma fake'
labels_dict['multijet']  = 'Multijet'
labels_dict['wjets']  = 'W + jets'
labels_dict['zjets']  = 'Z + jets'
labels_dict['vjets']  = 'W/Z + jets'
labels_dict['ttbar']  = 't#bar{t}'

mn1_text = 'm_{#tilde{#chi} #kern[-0.8]{#lower[1.2]{#scale[0.6]{1}}} #kern[-1.8]{#lower[-0.6]{#scale[0.6]{0}}}}'
labels_dict['GGM_M3_mu_1400_250']  = '(1400, 250)' ##m_{#tilde{g}} = 1522, ' + mn1_text + ' = 191 GeV'
labels_dict['GGM_M3_mu_1400_650']  = '(1400, 650)' ##)m_{#tilde{g}} = 1522, ' + mn1_text + ' = 442 GeV'
labels_dict['GGM_M3_mu_1400_1050'] = '(1400, 1050)' #m_{#tilde{g}} = 1522, ' + mn1_text + ' = 1072 GeV'
labels_dict['GGM_M3_mu_1400_1375'] = '(1400, 1375)' #m_{#tilde{g}} = 1522, ' + mn1_text + ' = 1283 GeV'

labels_dict['GGM_M3_mu_1700_250']  = '(1700, 250)' ##m_{#tilde{g}} = 1522, ' + mn1_text + ' = 191 GeV'
labels_dict['GGM_M3_mu_1700_650']  = '(1700, 650)' ##)m_{#tilde{g}} = 1522, ' + mn1_text + ' = 442 GeV'
labels_dict['GGM_M3_mu_1700_1050'] = '(1700, 1050)' #m_{#tilde{g}} = 1522, ' + mn1_text + ' = 1072 GeV'
labels_dict['GGM_M3_mu_1700_1375'] = '(1700, 1375)' #m_{#tilde{g}} = 1522, ' + mn1_text + ' = 1283 GeV'

# Colours
colors_dict = dict()
colors_dict['photonjet'] = '#E24A33'
colors_dict['gamjet'] = '#E24A33'
colors_dict['tgamma']    = '#32b45d'
colors_dict['vgamma']    = '#f7fab3'
colors_dict['znngam']    = '#7A68A6'
colors_dict['efake']     = '#a4cee6'
colors_dict['jfake']     = '#348ABD'
colors_dict['multijet']  = '#348ABD'
colors_dict['wjets']     = '#BCBC93'
colors_dict['zjets']     = '#36BDBD'
colors_dict['vjets']     = '#a4cee6'
colors_dict['ttbar']     = '#32b45d'

colors_dict['wgamma']    = '#f7fab3'
colors_dict['zllgamma']    = '#f7fab4'
colors_dict['znunugamma']    = '#f7fab5'
colors_dict['ttbar']    = '#32b422'
colors_dict['ttbarg']    = '#32b45d'
colors_dict['data']    = ROOT.kBlack

colors_dict['GGM_M3_mu_1400_250']  = '#85ea7a' 
colors_dict['GGM_M3_mu_1400_650']  = '#fa3a92'
colors_dict['GGM_M3_mu_1400_1050'] = '#8453fb'
colors_dict['GGM_M3_mu_1400_1375'] = '#53fb84'

colors_dict['GGM_M3_mu_1700_250']  = '#85ea7a' 
colors_dict['GGM_M3_mu_1700_650']  = '#fa3a92'
colors_dict['GGM_M3_mu_1700_1050'] = '#8453fb'
colors_dict['GGM_M3_mu_1700_1375'] = '#53fb84'

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
