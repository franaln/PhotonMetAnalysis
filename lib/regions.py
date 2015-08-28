# single photon analysis
# SRs, CRs, VRs definitions

#--- Signal Regions
SR_L = 'ph_n>0 && ph_pt>150 && (el_n+mu_n)==0 && jet_n>=4 && jet_pt[]>40 && jet_pt[0]>100 && jet_pt[1]>100 && dphi_jetmet>0.4 && met_et>200 && rt4<0.85 '
SR_H = 'ph_n>0 && ph_pt>300 && (el_n+mu_n)==0 && jet_n>=2 && jet_pt[]>40 && dphi_jetmet>0.4 && met_et>300 && ht>800 && dphi_gamjet<2.0'

#--- Control Regions
# QCD normalization region (reversing MET: MET < 50 GeV)
CRM_L = 'ph_n>0 && ph_pt>150 && (el_n+mu_n)==0 && met_et<50 && jet_n>=4 && jet_pt[]>40 && jet_pt[0]>100 && jet_pt[1]>100 && dphi_jetmet>0.4 && rt4<0.85'
CRM_H = 'ph_n>0 && ph_pt>300 && (el_n+mu_n)==0 && met_et<50 && jet_n>=2 && jet_pt[]>40 && dphi_jetmet>0.4 && ht>800 && dphi_gamjet<2.0'

# W+gamma control region
CRLW_L = 'ph_n==1 && ph_pt[0]>145 && (el_n+mu_n)==1 && jet_n>=4 && jet_pt[0]>100 && jet_pt[1]>100 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && bjet_n==0'
CRLW_H = 'ph_n==1 && ph_pt[0]>145 && (el_n+mu_n)==1 && jet_n>=2 && jet_pt[0]>40  && jet_pt[1]>40  && met_et>100 && met_et<200 && dphi_jetmet>0.4 && dphi_gamjet<2.0 && bjet_n==0'

# ttbar+gamma control region
CRLT_L = 'ph_n==1 && ph_pt[0]>145 && (el_n+mu_n)>0 && jet_n>=4 && jet_pt[0]>100 && jet_pt[1]>100 && met_et>80 && met_et<200 && dphi_jetmet>0.4 && bjet_n>0'
CRLT_H = 'ph_n==1 && ph_pt[0]>145 && (el_n+mu_n)>0 && jet_n>=2 && jet_pt[0]>40  && jet_pt[1]>40  && met_et>80 && met_et<200 && dphi_jetmet>0.4 && dphi_gamjet<2.0 && bjet_n>0'

#--- Validation Regions
# MET-sideband
VRM50_2  = 'ph_n==1 && ph_pt[0]>145 && (el_n+mu_n)==0 && jet_n>=4 && jet_pt[0]>100 && jet_pt[1]>100 && met_et>50  && met_et<150 && rt4<0.85 && dphi_jetmet>0.4'
VRM75_2  = 'ph_n==1 && ph_pt[0]>145 && (el_n+mu_n)==0 && jet_n>=4 && jet_pt[0]>100 && jet_pt[1]>100 && met_et>75  && met_et<150 && rt4<0.85 && dphi_jetmet>0.4'
VRM100_2 = 'ph_n==1 && ph_pt[0]>145 && (el_n+mu_n)==0 && jet_n>=4 && jet_pt[0]>100 && jet_pt[1]>100 && met_et>100 && met_et<150 && rt4<0.85 && dphi_jetmet>0.4'

# HT-sideband
VRH_H = 'ph_n==1 && ph_pt[0]>145 && (el_n+mu_n)==0 && jet_n>=2 && jet_pt[0]>40 && jet_pt[1]>40 && met_et>300 && ht>0 && ht<800 && dphi_gamjet<2.0 && dphi_jetmet>0.4'

# QCD-enriched  (reversed dphi(jet,MET))
VRQ_L = 'ph_n==1 && ph_pt[0]>145 && (el_n+mu_n)==0 && jet_n>=4 && jet_pt[0]>100 && jet_pt[1]>100 && met_et>200 && ht>0   && rt4<0.85        && dphi_jetmet<0.4'
VRQ_H = 'ph_n==1 && ph_pt[0]>145 && (el_n+mu_n)==0 && jet_n>=2 && jet_pt[0]>40  && jet_pt[1]>40  && met_et>300 && ht>800 && dphi_gamjet<2.0 && dphi_jetmet<0.4'

# QCD-enriched  (reversed R_T^4)
VRR_L = 'ph_n==1 && ph_pt[0]>145 && (el_n+mu_n)==0 && jet_n>=4 && jet_pt[0]>100 && jet_pt[1]>100 && met_et>200 && ht>0 && rt4>0.85 && dphi_jetmet>0.4'
