## Histograms binning

bins = dict()

## counts
bins['cuts'] = (1, 0.5, 1.5)

## photon
bins['ph_n']  = (5, 0, 5)
bins['ph_pt']  = (14, 145., 1545) ##(150., 350, 550, 750, 950, 1250, 1550)  ##15, 145., 1645.)
bins['ph_iso'] = (40, -20., 20.)
bins['ph_eta'] = (30, -3., 3.)
bins['ph_etas2'] = (30, -3., 3.)
bins['ph_phi'] = (17, -3.4, 3.4)
bins['ph_truth_pt']  = (100, 145., 2045.)

## jets
bins['jet_n']   = (20, 0, 20)
bins['bjet_n']  = (10, 0, 10)
bins['jet_pt']  = (40, 0., 2000.)
bins['jet_e']  = (40, 0., 2000.)
bins['jet_eta'] = (15, -3., 3.)
bins['jet_phi'] = (34, -3.4, 3.4)
bins['jet_isb'] = (2, 0, 2)

## met
bins['met_et']  = (10, 0, 1000)
#bins['met_et']  = (0, 100, 200, 300, 400, 500, 600, 1000) 
bins['met_phi'] = (17, -3.4, 3.4)
bins['met_soft_et']  = (20, 0., 1000.)
bins['met_soft_phi'] = (17, -3.4, 3.4)
bins['met_gam_et']  = (20, 0., 1000.)
bins['met_gam_phi'] = (17, -3.4, 3.4)
bins['met_jet_et']  = (20, 0., 1000.)
bins['met_jet_phi'] = (17, -3.4, 3.4)
bins['met_ele_et']  = (20, 0., 1000.)
bins['met_ele_phi'] = (17, -3.4, 3.4)
bins['met_muon_et']  = (20, 0., 1000.)
bins['met_muon_phi'] = (17, -3.4, 3.4)
bins['met_track_et']  = (20, 0., 1000.)
bins['met_track_phi'] = (17, -3.4, 3.4)
bins['met_sig'] = (50, 0., 50.)
bins['met_sumet']  = (40, 0., 8000.)
bins['met_truth_et']  = (20, 0., 1000.)

## dphi
bins['dphi_jetmet']     = (17, 0., 3.4)
bins['dphi_gamjet']     = (17, 0., 3.4)
bins['dphi_gammet']     = (17, 0., 3.4)
bins['dphi'] = (17, 0., 3.4)

## others
bins['ht0']             = (25, 0., 5000.)
bins['ht']              = (25, 0., 5000.)
bins['meff']            = (12, 0., 6000.)
#bins['meff']            = (15, 0., 6000.)
bins['rt1']             = (22, 0., 1.1)
bins['rt2']             = (22, 0., 1.1)
bins['rt3']             = (22, 0., 1.1)
bins['rt4']             = (22, 0., 1.1)

## leptons
bins['el_n']    = (10, 0, 10)
bins['mu_n']    = (10, 0, 10)

# default for common variables
bins['pt']  = (30, 0, 1500)
bins['eta'] = (15, -3.,3.)
bins['phi'] = (34, -3.4,3.4)

## invariant mass
bins['mgj'] = (100, 0, 7000.)
bins['mgjj'] = (100, 0, 7000.)
bins['mgjjj'] = (107, 0, 7490.)

## others
bins['ph_pt[0]+met_et'] = (25, 0, 5000.)
bins['ht+met_et'] = (50, 0, 5000.)
bins['ht+met_et-ph_pt'] = (60, 0, 6000.)
bins['ht-ph_pt[0]'] = (25, 0, 5000.)

bins['mt']  = (50, 0, 2500.)
bins['mt_gam']  = (60, 0, 1500.)
bins['mt2'] = (50, 0, 15000.)
bins['stgam'] = (25, 0, 5000.)

bins['avg_mu'] = (50, 0, 50)
bins['avgmu'] = (50, 0, 50)

bins['deta_gamjet'] = (60, 0., 6.)
bins['dr_gamjet'] = (60, 0., 6.)

bins['jet_pt[0]']  = (40, 0., 2000.)
bins['jet_pt[1]']  = (40, 0., 2000.)
bins['jet_pt[2]']  = (40, 0., 2000.)
bins['jet_pt[3]']  = (40, 0., 2000.)

bins['met_et/sqrt(ht)']  = (100, 0., 50.)
bins['met_et/meff']  = (20, 0., 1.)
bins['met_et/ht']  = (40, 0., 2.)

bins['photontype'] = (4, 0, 4)


bins['m_jetjet'] = (16, 0, 400)

bins['pass_g140'] = (2, 0, 2)
bins['pass_g70_xe70'] = (2, 0, 2)

bins['dphi_gamsoft'] = (17, 0., 3.4)
# bins['get_dphi(ph_phi[0], met_soft_phi)'] = (17, 0., 3.4)
