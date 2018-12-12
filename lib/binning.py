## Histograms binning

binning_dict = dict()

## counts
binning_dict['cuts'] = (1, 0.5, 1.5)

## photon
binning_dict['ph_n']  = (5, 0, 5)
binning_dict['ph_pt']  = (145., 200, 250, 300, 450, 500, 550, 600, 700, 800, 900, 1000, 1250, 1500, 1750, 2000)
binning_dict['ph_iso'] = (40, -20., 20.)
binning_dict['ph_eta'] = (30, -3., 3.)
binning_dict['ph_etas2'] = (30, -3., 3.)
binning_dict['ph_phi'] = (17, -3.4, 3.4)
binning_dict['ph_truth_pt']  = (100, 145., 2045.)
binning_dict['ph_etcone40']  = (50, -5., 20.)
binning_dict['ph_ptcone20']  = (50, -5., 20.)

## jets
binning_dict['jet_n']   = (20, 0, 20)
binning_dict['bjet_n']  = (10, 0, 10)
binning_dict['jet_pt']  = (50, 0., 2500.)
binning_dict['jet_e']  = (40, 0., 2000.)
binning_dict['jet_eta'] = (15, -3., 3.)
binning_dict['jet_phi'] = (34, -3.4, 3.4)
binning_dict['jet_isb'] = (2, 0, 2)

## met
#binning_dict['met_et']  = (10, 0, 1000)
binning_dict['met_et']  = (20, 0, 1000)
#binning_dict['met_et']  = (0, 100, 200, 300, 400, 500, 600, 1000)
binning_dict['met_phi'] = (17, -3.4, 3.4)
binning_dict['met_soft_et']  = (20, 0., 1000.)
binning_dict['met_soft_phi'] = (17, -3.4, 3.4)
binning_dict['met_gam_et']  = (20, 0., 1000.)
binning_dict['met_gam_phi'] = (17, -3.4, 3.4)
binning_dict['met_jet_et']  = (20, 0., 1000.)
binning_dict['met_jet_phi'] = (17, -3.4, 3.4)
binning_dict['met_ele_et']  = (20, 0., 1000.)
binning_dict['met_ele_phi'] = (17, -3.4, 3.4)
binning_dict['met_muon_et']  = (20, 0., 1000.)
binning_dict['met_muon_phi'] = (17, -3.4, 3.4)
binning_dict['met_track_et']  = (20, 0., 1000.)
binning_dict['met_track_phi'] = (17, -3.4, 3.4)
binning_dict['met_sig'] = (50, 0., 50.)
binning_dict['met_sumet']  = (40, 0., 8000.)
binning_dict['met_truth_et']  = (20, 0., 1000.)

## dphi
binning_dict['dphi_jetmet']     = (17, 0., 3.4)
binning_dict['dphi_gamjet']     = (17, 0., 3.4)
binning_dict['dphi_gammet']     = (17, 0., 3.4)
binning_dict['dphi'] = (17, 0., 3.4)

## others
binning_dict['ht0']             = (30, 0., 6000.)
binning_dict['ht']              = (30, 0., 6000.)
binning_dict['meff']            = (12, 0., 6000.)
#binning_dict['meff']            = (15, 0., 6000.)
binning_dict['rt1']             = (22, 0., 1.1)
binning_dict['rt2']             = (22, 0., 1.1)
binning_dict['rt3']             = (22, 0., 1.1)
binning_dict['rt4']             = (22, 0., 1.1)

## leptons
binning_dict['el_n']    = (10, 0, 10)
binning_dict['mu_n']    = (10, 0, 10)

# default for common variables
binning_dict['pt']  = (30, 0, 1500)
binning_dict['eta'] = (15, -3.,3.)
binning_dict['phi'] = (34, -3.4,3.4)

## invariant mass
binning_dict['mgj'] = (100, 0, 7000.)
binning_dict['mgjj'] = (100, 0, 7000.)
binning_dict['mgjjj'] = (107, 0, 7490.)

## others
binning_dict['ph_pt[0]+met_et'] = (25, 0, 5000.)
binning_dict['ht+met_et'] = (50, 0, 5000.)
binning_dict['ht+met_et-ph_pt'] = (60, 0, 6000.)
binning_dict['ht-ph_pt[0]'] = (25, 0, 5000.)

binning_dict['mt']  = (50, 0, 2500.)
binning_dict['mt_gam']  = (60, 0, 1500.)
binning_dict['mt2'] = (50, 0, 15000.)
binning_dict['stgam'] = (25, 0, 5000.)

binning_dict['avg_mu'] = (50, 0, 50)
binning_dict['avgmu'] = (50, 0, 50)

binning_dict['deta_gamjet'] = (60, 0., 6.)
binning_dict['dr_gamjet'] = (60, 0., 6.)

binning_dict['jet_pt[0]']  = (50, 0., 2500.)
binning_dict['jet_pt[1]']  = (40, 0., 2000.)
binning_dict['jet_pt[2]']  = (40, 0., 2000.)
binning_dict['jet_pt[3]']  = (40, 0., 2000.)

binning_dict['met_et/sqrt(ht)']  = (100, 0., 50.)
binning_dict['met_et/meff']  = (20, 0., 1.)
binning_dict['met_et/ht']  = (40, 0., 2.)

binning_dict['photontype'] = (4, 0, 4)


binning_dict['m_jetjet'] = (16, 0, 400)

binning_dict['pass_g140'] = (2, 0, 2)
binning_dict['pass_g70_xe70'] = (2, 0, 2)

binning_dict['dphi_gamsoft'] = (17, 0., 3.4)
# binning_dict['get_dphi(ph_phi[0], met_soft_phi)'] = (17, 0., 3.4)

binning_dict['default'] = (100, 0., 1000)
