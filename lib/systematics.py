# photons+electrons
systematics_egamma_kin = [
    'EG_RESOLUTION_ALL__1down', 'EG_RESOLUTION_ALL__1up',
    'EG_SCALE_ALL__1down',      'EG_SCALE_ALL__1up',
]

systematics_photon_kin = [
    'PH_Iso_DDonoff',
]

systematics_photon_w = [
    'PH_EFF_ID_Uncertainty__1down', 'PH_EFF_ID_Uncertainty__1up',
    'PH_EFF_LOWPTISO_Uncertainty__1down', 'PH_EFF_LOWPTISO_Uncertainty__1up',
#    'PH_EFF_LOWPTISO_Uncertainty__1down', 'PH_EFF_LOWPTISO_Uncertainty__1up',
]

systematics_electron_w = [
    'EL_EFF_ID_TOTAL_1NPCOR_PLUS_UNCOR__1down',          'EL_EFF_ID_TOTAL_1NPCOR_PLUS_UNCOR__1up',
    'EL_EFF_ChargeIDSel_TOTAL_1NPCOR_PLUS_UNCOR__1down', 'EL_EFF_ChargeIDSel_TOTAL_1NPCOR_PLUS_UNCOR__1up',
    'EL_EFF_Iso_TOTAL_1NPCOR_PLUS_UNCOR__1down',         'EL_EFF_Iso_TOTAL_1NPCOR_PLUS_UNCOR__1up',
    'EL_EFF_Reco_TOTAL_1NPCOR_PLUS_UNCOR__1down',        'EL_EFF_Reco_TOTAL_1NPCOR_PLUS_UNCOR__1up',
    'EL_EFF_TriggerEff_TOTAL_1NPCOR_PLUS_UNCOR__1down',  'EL_EFF_TriggerEff_TOTAL_1NPCOR_PLUS_UNCOR__1up',
    'EL_EFF_Trigger_TOTAL_1NPCOR_PLUS_UNCOR__1down',     'EL_EFF_Trigger_TOTAL_1NPCOR_PLUS_UNCOR__1up',
]

# muons
systematics_muon_kin = [
    'MUON_MS__1down',              'MUON_MS__1up',
    'MUON_ID__1down',              'MUON_ID__1up',
    'MUON_SAGITTA_RESBIAS__1down', 'MUON_SAGITTA_RESBIAS__1up',
    'MUON_SAGITTA_RHO__1down',     'MUON_SAGITTA_RHO__1up',
    'MUON_SCALE__1down',           'MUON_SCALE__1up',
]

systematics_muon_w = [
    'MUON_EFF_STAT__1down',                'MUON_EFF_STAT__1up',
    'MUON_EFF_STAT_LOWPT__1down',          'MUON_EFF_STAT_LOWPT__1up',
    'MUON_EFF_SYS__1down',                 'MUON_EFF_SYS__1up',
    'MUON_EFF_SYS_LOWPT__1down',           'MUON_EFF_SYS_LOWPT__1up',
    'MUON_EFF_TrigStatUncertainty__1down', 'MUON_EFF_TrigStatUncertainty__1up',
    'MUON_EFF_TrigSystUncertainty__1down', 'MUON_EFF_TrigSystUncertainty__1up',
    'MUON_ISO_STAT__1down',                'MUON_ISO_STAT__1up',
    'MUON_ISO_SYS__1down',                 'MUON_ISO_SYS__1up',
    'MUON_BADMUON_STAT__1down',             'MUON_BADMUON_STAT__1up',
    'MUON_BADMUON_SYS__1down',             'MUON_BADMUON_SYS__1up',
    'MUON_TTVA_STAT__1down',             'MUON_TTVA_STAT__1up',
    'MUON_TTVA_SYS__1down',             'MUON_TTVA_SYS__1up',

]


# jets 
systematics_jet_kin = [
    'JET_EtaIntercalibration_NonClosure__1up', 'JET_EtaIntercalibration_NonClosure__1down',
    'JET_GroupedNP_1__1up',        'JET_GroupedNP_1__1down',
    'JET_GroupedNP_2__1up',        'JET_GroupedNP_2__1down',
    'JET_GroupedNP_3__1up',        'JET_GroupedNP_3__1down',
    # 'JET_Rtrk_Baseline_Kin__1up',  'JET_Rtrk_Baseline_Kin__1down',
    # 'JET_Rtrk_Baseline_Sub__1up',  'JET_Rtrk_Baseline_Sub__1down',
    # 'JET_Rtrk_Modelling_Kin__1up', 'JET_Rtrk_Modelling_Kin__1down',
    # 'JET_Rtrk_Modelling_Sub__1up', 'JET_Rtrk_Modelling_Sub__1down',
    # 'JET_Rtrk_TotalStat_Kin__1up', 'JET_Rtrk_TotalStat_Kin__1down',
    # 'JET_Rtrk_TotalStat_Sub__1up', 'JET_Rtrk_TotalStat_Sub__1down',
    # 'JET_Rtrk_Tracking_Kin__1up',  'JET_Rtrk_Tracking_Kin__1down',
    # 'JET_Rtrk_Tracking_Sub__1up',  'JET_Rtrk_Tracking_Sub__1down',

    'JET_JER_SINGLE_NP__1up',
]

systematics_jet_w = [
    'JET_JvtEfficiency__1down', 'JET_JvtEfficiency__1up',     
    #     'FT_EFF_B_systematics__1down', 'FT_EFF_B_systematics__1up',
    #     'FT_EFF_C_systematics__1down', 'FT_EFF_C_systematics__1up',
    #     'FT_EFF_Light_systematics__1down', 'FT_EFF_Light_systematics__1up',
    #     'FT_EFF_extrapolation__1down', 'FT_EFF_extrapolation__1up',
    # #    'FT_EFF_extrapolation_from_charm__1down',  'FT_EFF_extrapolation_from_charm__1up',
]

# met
systematics_met = [
    'MET_SoftTrk_ResoPara',
    'MET_SoftTrk_ResoPerp',
    'MET_SoftTrk_ScaleDown', 'MET_SoftTrk_ScaleUp',
]


# weights
systematics_prw_w = [
    'PRW_DATASF__1down', 'PRW_DATASF__1up',
    ]


syst_kin = systematics_egamma_kin + systematics_photon_kin + systematics_jet_kin + systematics_muon_kin + systematics_met
syst_weight = systematics_electron_w + systematics_jet_w + systematics_muon_w + systematics_photon_w + systematics_prw_w

systematics_oneside = [
    'MET_SoftTrk_ResoPara',
    'MET_SoftTrk_ResoPerp',
    'JET_JER_SINGLE_NP__1up',
    'PH_Iso_DDonoff'
]

def get_one_side_systematics():
    return systematics_oneside

def get_high_low_systematics():

    systematics = syst_kin + syst_weight

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
variables_kin = ['ht', 'meff', 'rt2', 'rt4', 'dphi_gammet', 'dphi_jetmet', 'dphi_gamjet']

def get_affected_variables(syst):

    if syst in systematics_jet_kin:
        return variables_jet + variables_met + variables_kin

    elif syst in systematics_egamma_kin:
        return variables_ph + variables_el + variables_met + variables_kin

    elif syst in systematics_photon_kin:
        return variables_ph + variables_kin

    elif syst in systematics_muon_kin:
        return variables_mu + variables_met + variables_kin

    elif syst in systematics_met:
        return variables_met + variables_kin

def affects_weight(syst):
    return syst in syst_weight

def affects_kinematics(syst):
    return syst in syst_kin

