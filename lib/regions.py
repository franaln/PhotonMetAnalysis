# single photon analysis
# SRs, CRs, VRs definitions

# Preselection
presel = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4'

# Signal Regions
SR_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
SR_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>400 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000' 

## Inclusive signal regions
SRi_L = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
SRi_H = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>400 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000' 

SRincl_L = SRi_L
SRincl_H = SRi_H

# Control Regions
CRQ_L  = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>4 && met_et<50 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>1500 && rt4<0.9'
CRW_L  = 'ph_n>0 && el_n+mu_n>0  && ph_pt[0]>145 && jet_n>0 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n==0'
CRT_L  = 'ph_n>0 && el_n+mu_n>0  && ph_pt[0]>145 && jet_n>1 && met_et>50  && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n>1'

CRQ_H = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>400 && jet_n>2 && met_et<50  && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000'
CRW_H = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145  && jet_n>0 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n==0'
CRT_H = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145  && jet_n>1 && met_et>50  && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n>1'

# Validation Regions

## Intermediate MET
VRM1_L = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>75 && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>1000 && rt4<0.9'
VRM2_L = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>75 && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>1500 && rt4<0.9'
VRM3_L = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>75 && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'

VRM1_H = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>125 && met_et<175 && jet_n>2 && dphi_jetmet>0.4 && meff>1000'
VRM2_H = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>125 && met_et<175 && jet_n>2 && dphi_jetmet>0.4 && meff>1500'
VRM3_H = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>125 && met_et<175 && jet_n>2 && dphi_jetmet>0.4 && meff>2000'

## Reverse dphi cuts
VRD1_L = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>2 && dphi_jetmet<0.4 && dphi_gammet>0.4 && meff>1000'
VRD2_L = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>2 && dphi_jetmet<0.4 && dphi_gammet>0.4 && meff>1500'
VRD3_L = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>2 && dphi_jetmet<0.4 && dphi_gammet>0.4 && meff>2000'

VRD1_H = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>400 && jet_n>2 && dphi_jetmet<0.4 && dphi_gammet>0.4 && meff>1000'
VRD2_H = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>400 && jet_n>2 && dphi_jetmet<0.4 && dphi_gammet>0.4 && meff>1500'
VRD3_H = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>400 && jet_n>2 && dphi_jetmet<0.4 && dphi_gammet>0.4 && meff>2000'

## Wgamma/ttbarg
VRL1_L = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et<200 && dphi_jetmet>0.4 && meff>1000'
VRL2_L = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et<200 && dphi_jetmet>0.4 && meff>1500'
VRL3_L = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>200 && dphi_jetmet>0.4 && meff<2000'
VRL4_L = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>200 && dphi_jetmet<0.4 && meff>1500'

VRL1_H = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>200 && jet_n>1 && met_et<200 && dphi_jetmet>0.4 && meff>1000'
VRL2_H = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>200 && jet_n>1 && met_et<200 && dphi_jetmet>0.4 && meff>1500'
VRL3_H = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>200 && jet_n>1 && met_et>200 && dphi_jetmet>0.4 && meff<2000'
VRL4_H = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>200 && jet_n>1 && met_et>200 && dphi_jetmet<0.4 && meff>1500'


