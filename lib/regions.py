# single photon analysis
# SRs, CRs, VRs definitions

# Preselection
presel          = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && met_et>50'
presel_blind    = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && met_et<200'
presel_meff500  = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && met_et>50 && meff>500'
presel_meff1000 = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && met_et>50 && meff>1000'
presel_meff1500 = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && met_et>50 && meff>1500'
presel_meff2000 = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && met_et>50 && meff>2000'

# Signal Regions
SRL200 = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
SRL300 = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>300 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
SRL = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>300 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'

SRH = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>400 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2400'

# Control Regions
CRQ = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && met_et>100 && meff>2000 && dphi_jetmet<0.4 && dphi_gammet>0.4'
CRW = 'pass_g140==1 && ph_n>0 && el_n+mu_n>0  && ph_pt[0]>145 && jet_n>0 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n==0'
CRT = 'pass_g140==1 && ph_n>0 && el_n+mu_n>0  && ph_pt[0]>145 && jet_n>1 && met_et>50  && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n>=2'


# Validation Regions

## Intermediate MET
VRQ = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && met_et>100 && met_et<200 && meff>2000 && dphi_jetmet>0.4 && dphi_gammet>0.4'

VRM1L = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>100  && met_et<200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
VRM2L = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>150  && met_et<200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'

VRM1H = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>300 && met_et>100  && met_et<200 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000'
VRM2H = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>300 && met_et>150  && met_et<200 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000'

## lepton VR: Wgamma/ttbarg
VRL1 = 'pass_g140==1 && ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et<200 && dphi_jetmet>0.4 && meff>1000'
VRL2 = 'pass_g140==1 && ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et<200 && dphi_jetmet>0.4 && meff>1500'
VRL3 = 'pass_g140==1 && ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>200 && dphi_jetmet>0.4 && meff>1000 && meff<2000'
VRL4 = 'pass_g140==1 && ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>200 && dphi_jetmet<0.4 && meff>1500'
VRL5 = 'pass_g140==1 && ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>200 && dphi_jetmet<0.4 && meff>1000 && bjet_n>0'

VRLW1 = 'pass_g140==1 && ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>1000 && bjet_n==0'
VRLT1 = 'pass_g140==1 && ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>1000 && bjet_n>0'
VRLW3 = 'pass_g140==1 && ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>200 && dphi_jetmet>0.4 && meff>1000 && meff<2000 && bjet_n==0'
VRLT3 = 'pass_g140==1 && ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>200 && dphi_jetmet>0.4 && meff>1000 && meff<2000 && bjet_n>0'

## electron fakes
VRE  = "pass_g140==1 && ph_n>0 && ph_pt[0]>145 && met_et>200 && jet_n>=1 && meff>500 && meff<2000 && bjet_n>=1 && dphi_jetmet>0.4 && dphi_gammet<0.4"


# Others/Old

# CRQ -> SR validation plots
VR_CRQmet = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && meff>2000 && dphi_jetmet<0.4 && dphi_gammet>0.4'
VR_SRLmet = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et<200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
VR_SRHmet = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>400 && met_et<200 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2400'

VR_CRQmeff = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && met_et>100 && dphi_jetmet<0.4 && dphi_gammet>0.4'
VR_SRLmeff = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>300 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && rt4<0.9'
VR_SRHmeff = 'pass_g140==1 && ph_n>0 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>400 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4'

