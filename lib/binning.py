## Histograms binning

bins = dict()

## counts
bins['cuts'] = (1, 0.5, 1.5)

## photon
bins['ph_n']  = (5, 0, 5)
bins['ph_pt']  = (20, 0., 2000.)
bins['ph_iso'] = (40, -20., 20.)
bins['ph_eta'] = (15, -3., 3.)
bins['ph_phi'] = (17, -3.4, 3.4)

## jets
bins['jet_n']   = (20, 0, 20)
bins['bjet_n']  = (10, 0, 10)
bins['jet_pt']  = (30, 0., 1500.)
bins['jet_eta'] = (15, -3., 3.)
bins['jet_phi'] = (34, -3.4, 3.4)

## met
bins['met_et']  = (20, 0., 1000.)
bins['met_phi'] = (17, -3.4, 3.4)
bins['met_truth_et']  = (20, 0., 1000.)

## dphi
bins['dphi_jetmet']     = (17, 0., 3.4)
bins['dphi_gamjet']     = (17, 0., 3.4)
bins['dphi_gammet']     = (17, 0., 3.4)
bins['dphi'] = (17, 0., 3.4)

## others
bins['ht']              = (25, 0., 5000.)
bins['meff']            = (25, 0., 5000.)
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

##
bins['ht+met_et'] = (50, 0, 5000.)
bins['ht+met_et-ph_pt'] = (60, 0, 6000.)
bins['ph_pt[0]/ht'] = (11, 0, 1.1)
bins['(jet_pt[0]+jet_pt[1])/(ht-ph_pt[0])'] = (22, 0., 1.1)

bins['avg_mu'] = (50, 0, 50)
bins['avgmu'] = (50, 0, 50)


