
# photons+electrons
systematics_egamma_kin = [
    'EG_RESOLUTION_ALL__1down', 'EG_RESOLUTION_ALL__1up',
    'EG_SCALE_ALL__1down', 'EG_SCALE_ALL__1up',
]

# muons
systematics_muon_kin = [
    'MUONS_SCALE__1down', 'MUONS_SCALE__1up',
    'MUONS_MS__1down',     'MUONS_MS__1up',
    'MUONS_ID__1down',     'MUONS_ID__1up',
]

# jets 
systematics_jet_kin = [
    'JET_GroupedNP_1__1down', 'JET_GroupedNP_1__1up',
    'JET_GroupedNP_2__1down',     'JET_GroupedNP_2__1up',
    'JET_GroupedNP_3__1down',     'JET_GroupedNP_3__1up',
    'JET_JER_SINGLE_NP__1up',
]

# met
systematics_met = [
    'MET_SoftTrk_ResoPara',
    'MET_SoftTrk_ResoPerp',
    'MET_SoftTrk_ScaleDown', 'MET_SoftTrk_ScaleUp',
]


# weights
systematics_electron_w = [
    'EL_EFF_ID_CorrUncertaintyNP0__1down', 'EL_EFF_ID_CorrUncertaintyNP0__1up',
    'EL_EFF_ID_CorrUncertaintyNP1__1down',     'EL_EFF_ID_CorrUncertaintyNP1__1up',
    'EL_EFF_ID_CorrUncertaintyNP2__1down',     'EL_EFF_ID_CorrUncertaintyNP2__1up',
    'EL_EFF_ID_CorrUncertaintyNP3__1down',     'EL_EFF_ID_CorrUncertaintyNP3__1up',
    'EL_EFF_ID_CorrUncertaintyNP4__1down',     'EL_EFF_ID_CorrUncertaintyNP4__1up',
    'EL_EFF_ID_CorrUncertaintyNP5__1down',     'EL_EFF_ID_CorrUncertaintyNP5__1up',
    'EL_EFF_ID_CorrUncertaintyNP6__1down',     'EL_EFF_ID_CorrUncertaintyNP6__1up',
    'EL_EFF_ID_CorrUncertaintyNP7__1down',     'EL_EFF_ID_CorrUncertaintyNP7__1up',
    'EL_EFF_ID_CorrUncertaintyNP8__1down',     'EL_EFF_ID_CorrUncertaintyNP8__1up',
    'EL_EFF_ID_CorrUncertaintyNP9__1down',     'EL_EFF_ID_CorrUncertaintyNP9__1up',
    'EL_EFF_ID_CorrUncertaintyNP10__1down',     'EL_EFF_ID_CorrUncertaintyNP10__1up',
    'EL_EFF_ID_CorrUncertaintyNP11__1down',     'EL_EFF_ID_CorrUncertaintyNP11__1up',
    'EL_EFF_ID_TOTAL_UncorrUncertainty__1down',     'EL_EFF_ID_TOTAL_UncorrUncertainty__1up',
    'EL_EFF_Iso_CorrUncertaintyNP0__1down',     'EL_EFF_Iso_CorrUncertaintyNP0__1up',
    'EL_EFF_Iso_CorrUncertaintyNP1__1down',     'EL_EFF_Iso_CorrUncertaintyNP1__1up',
    'EL_EFF_Iso_CorrUncertaintyNP2__1down',     'EL_EFF_Iso_CorrUncertaintyNP2__1up',
    'EL_EFF_Iso_CorrUncertaintyNP3__1down',     'EL_EFF_Iso_CorrUncertaintyNP3__1up',
    'EL_EFF_Iso_CorrUncertaintyNP4__1down',     'EL_EFF_Iso_CorrUncertaintyNP4__1up',
    'EL_EFF_Iso_CorrUncertaintyNP5__1down',     'EL_EFF_Iso_CorrUncertaintyNP5__1up',
    'EL_EFF_Iso_CorrUncertaintyNP6__1down',     'EL_EFF_Iso_CorrUncertaintyNP6__1up',
    'EL_EFF_Iso_CorrUncertaintyNP7__1down',     'EL_EFF_Iso_CorrUncertaintyNP7__1up',
    'EL_EFF_Iso_CorrUncertaintyNP8__1down',     'EL_EFF_Iso_CorrUncertaintyNP8__1up',
    'EL_EFF_Iso_CorrUncertaintyNP9__1down',     'EL_EFF_Iso_CorrUncertaintyNP9__1up',
    'EL_EFF_Iso_CorrUncertaintyNP10__1down',     'EL_EFF_Iso_CorrUncertaintyNP10__1up',
    'EL_EFF_Iso_TOTAL_UncorrUncertainty__1down',     'EL_EFF_Iso_TOTAL_UncorrUncertainty__1up',
    'EL_EFF_Reco_CorrUncertaintyNP0__1down',     'EL_EFF_Reco_CorrUncertaintyNP0__1up',
    'EL_EFF_Reco_CorrUncertaintyNP1__1down',     'EL_EFF_Reco_CorrUncertaintyNP1__1up',
    'EL_EFF_Reco_CorrUncertaintyNP2__1down',     'EL_EFF_Reco_CorrUncertaintyNP2__1up',
    'EL_EFF_Reco_CorrUncertaintyNP3__1down',     'EL_EFF_Reco_CorrUncertaintyNP3__1up',
    'EL_EFF_Reco_CorrUncertaintyNP4__1down',     'EL_EFF_Reco_CorrUncertaintyNP4__1up',
    'EL_EFF_Reco_CorrUncertaintyNP5__1down',     'EL_EFF_Reco_CorrUncertaintyNP5__1up',
    'EL_EFF_Reco_CorrUncertaintyNP6__1down',     'EL_EFF_Reco_CorrUncertaintyNP6__1up',
    'EL_EFF_Reco_CorrUncertaintyNP7__1down',     'EL_EFF_Reco_CorrUncertaintyNP7__1up',
    'EL_EFF_Reco_CorrUncertaintyNP8__1down',     'EL_EFF_Reco_CorrUncertaintyNP8__1up',
    'EL_EFF_Reco_CorrUncertaintyNP9__1down',     'EL_EFF_Reco_CorrUncertaintyNP9__1up',
    'EL_EFF_Reco_TOTAL_UncorrUncertainty__1down',     'EL_EFF_Reco_TOTAL_UncorrUncertainty__1up',
    'EL_EFF_Trigger_CorrUncertaintyNP0__1down',     'EL_EFF_Trigger_CorrUncertaintyNP0__1up',
    'EL_EFF_Trigger_CorrUncertaintyNP1__1down',     'EL_EFF_Trigger_CorrUncertaintyNP1__1up',
    'EL_EFF_Trigger_CorrUncertaintyNP2__1down',     'EL_EFF_Trigger_CorrUncertaintyNP2__1up',
    'EL_EFF_Trigger_CorrUncertaintyNP3__1down',     'EL_EFF_Trigger_CorrUncertaintyNP3__1up',
    'EL_EFF_Trigger_CorrUncertaintyNP4__1down',     'EL_EFF_Trigger_CorrUncertaintyNP4__1up',
    'EL_EFF_Trigger_TOTAL_UncorrUncertainty__1down',     'EL_EFF_Trigger_TOTAL_UncorrUncertainty__1up',
]

systematics_jet_w = [
    'FT_EFF_B_systematics__1down', 'FT_EFF_B_systematics__1up',
    'FT_EFF_C_systematics__1down',     'FT_EFF_C_systematics__1up',
    'FT_EFF_Light_systematics__1down',     'FT_EFF_Light_systematics__1up',
    'FT_EFF_extrapolation__1down',     'FT_EFF_extrapolation__1up',
#    'FT_EFF_extrapolation from charm__1down',     'FT_EFF_extrapolation from charm__1up',
    'JvtEfficiencyDown', 'JvtEfficiencyUp',     
    'JvtEfficiencyDown', 'JvtEfficiencyUp',
]

systematics_muon_w = [
    'MUON_EFF_STAT__1down', 'MUON_EFF_STAT__1up',
    'MUON_EFF_STAT_LOWPT__1down',     'MUON_EFF_STAT_LOWPT__1up',
    'MUON_EFF_SYS__1down',     'MUON_EFF_SYS__1up',
    'MUON_EFF_SYS_LOWPT__1down',     'MUON_EFF_SYS_LOWPT__1up',
    'MUON_EFF_TrigStatUncertainty__1down',     'MUON_EFF_TrigStatUncertainty__1up',
    'MUON_EFF_TrigSystUncertainty__1down',     'MUON_EFF_TrigSystUncertainty__1up',
    'MUON_ISO_STAT__1down',     'MUON_ISO_STAT__1up',
    'MUON_ISO_SYS__1down',     'MUON_ISO_SYS__1up',
]

systematics_photon_w = [
    'PH_EFF_ID_Uncertainty__1down', 'PH_EFF_ID_Uncertainty__1up',
    ]

# systematics_efake_w = [
#     'efakeLow', 'efakeHigh'
#     ]

syst_kin = systematics_egamma_kin + systematics_jet_kin + systematics_muon_kin + systematics_met
syst_weights = systematics_electron_w + systematics_jet_w + systematics_muon_w + systematics_photon_w

systematics_oneside = [
        'MET_SoftTrk_ResoPara',
        'MET_SoftTrk_ResoPerp',
        'JET_JER_SINGLE_NP__1up',
]

def get_one_side_systematics():
    return systematics_oneside

def get_high_low_systematics():

    systematics = syst_kin + syst_weights

    for sys in systematics_oneside:
        systematics.remove(sys)
        
    systematics = [ i.replace('__1down', '').replace('__1up', '') for i in systematics ]
    systematics = [ i.replace('Down', '').replace('Up', '') for i in systematics ]

    return list(set(systematics))



# variables used in the regions selection
variables_ph  = ['ph_n', 'ph_pt', 'ph_eta', 'ph_phi']
variables_jet = ['jet_n', 'jet_pt', 'jet_eta', 'jet_phi']
variables_el  = ['el_n', ]
variables_mu  = ['mu_n', ]
variables_met = ['met_et', 'met_phi']
variables_kin = ['ht', 'meff', 'rt2', 'rt4', 'dphi_gammet', 'dphijetmet', 'dphi_gamjet']

def get_affected_variables(syst):

    if syst in systematics_jet_kin:
        return variables_jet + variables_met + variables_kin

    elif syst in systematics_egamma_kin:
        return variables_ph + variables_el + variables_met + variables_kin

    elif syst in systematics_muon_kin:
        return variables_mu + variables_met + variables_kin

    elif syst in systematics_met:
        return variables_met + variables_kin


def affects_weight(syst):
    return syst in syst_weights

def affects_kinematics(syst):
    return syst in syst_kin

