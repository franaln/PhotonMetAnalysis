# single photon analysis
# SRs, CRs, VRs definitions

# Preselection
presel = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && met_et>50'
presel_meff500 = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && met_et>50 && meff>500'
presel_meff1000 = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && met_et>50 && meff>1000'
presel_meff1500 = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && met_et>50 && meff>1500'
presel_meff2000 = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && met_et>50 && meff>2000'

presel_blind = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && met_et<200'

# Signal Regions
SRL100 = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>100 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
SRL200 = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
SRL300 = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>300 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'

SRH = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>400 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2400' 

# Control Regions
CRQ = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && met_et>100 && meff>2000 && dphi_jetmet<0.4 && dphi_gammet>0.4'
CRW = 'ph_n>0 && el_n+mu_n>0  && ph_pt[0]>145 && jet_n>0 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n==0'
CRT = 'ph_n>0 && el_n+mu_n>0  && ph_pt[0]>145 && jet_n>1 && met_et>50  && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n>=2'


# Validation Regions

## Intermediate MET
VRM1L = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>50  && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
VRM2L = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>75  && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
VRM3L = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>100 && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'

VRM1H = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>100  && met_et<175 && jet_n>2 && dphi_jetmet>0.4 && meff>2000'
VRM2H = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>125  && met_et<175 && jet_n>2 && dphi_jetmet>0.4 && meff>2000'
VRM3H = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>150  && met_et<175 && jet_n>2 && dphi_jetmet>0.4 && meff>2000'

## lepton VR: Wgamma/ttbarg
VRL1 = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et<200 && dphi_jetmet>0.4 && meff>1000'
VRL2 = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et<200 && dphi_jetmet>0.4 && meff>1500'
VRL3 = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>200 && dphi_jetmet>0.4 && meff>1000 && meff<2000'
VRL4 = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>200 && dphi_jetmet<0.4 && meff>1500'
VRL5 = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>200 && dphi_jetmet<0.4 && meff>1000 && bjet_n>0'

VRLW1 = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>1000 && bjet_n==0'
VRLT1 = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>1000 && bjet_n>0'
VRLW3 = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>200 && dphi_jetmet>0.4 && meff>1000 && meff<2000 && bjet_n==0'
VRLT3 = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>200 && dphi_jetmet>0.4 && meff>1000 && meff<2000 && bjet_n>0'

VRE  = "ph_n>0 && ph_pt[0]>145 && met_et>200 && jet_n>=1 && meff>500 && meff<2000 && bjet_n>=1 && dphi_jetmet>0.4 && dphi_gammet<0.4"

VRZ  = 'ph_n>0 && ph_pt[0]>145 && (el_n==2 || mu_n==2) && jet_n>0 &&  met_et<200 && meff>1000 && bjet_n==0'



# Others/Old
VRM1eL = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>50  && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && rt4<0.9'
VRM2eL = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>75  && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && rt4<0.9'
VRM3eL = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>100 && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && rt4<0.9'

VRM1eH = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>100  && met_et<175 && jet_n>2 && dphi_jetmet>0.4'
VRM2eH = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>125  && met_et<175 && jet_n>2 && dphi_jetmet>0.4'
VRM3eH = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>150  && met_et<175 && jet_n>2 && dphi_jetmet>0.4'

VRM1LwoRT = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>50  && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000'
CRQ1  = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && met_et<50 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000' 
CRQ2 = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>2 && met_et>75 && met_et<125 && meff>2000 && dphi_jetmet>0.4 && dphi_gammet>0.4'
CRQ4 = "ph_n>0 &&  ph_pt[0]>145 && el_n+mu_n==0 && met_et>200 && jet_n>2 && dphi_jetmet<0.4 && dphi_gammet>0.4 && meff>1000"

#VRF = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et<50 && dphi_jetmet>0.4 && meff>1000'
VRF = 'ph_n>0 && ph_pt[0]>145 && jet_n>2 && met_et>40 && met_et<200 && meff>1000 && mt_gam>35 && mt_gam<90'

## Blinded regions
SRL_ichep_met  = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et<200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
SRL_ichep_meff = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff<2000 && rt4<0.9'

SRL_met  = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>300 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
SRL_meff = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>300 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'

SRH_met  = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>400 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2400' 
SRH_meff = 'ph_n>0 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>400 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2400' 
