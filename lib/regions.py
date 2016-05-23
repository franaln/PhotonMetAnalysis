# single photon analysis
# SRs, CRs, VRs definitions

# Signal Regions
SR_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
SR_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>400 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000' 


# Control Regions
#CRW_L  = 'ph_n>0 && el_n+mu_n>0   && ph_pt[0]>145 && jet_n>2 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n==0'
#CRT_L  = 'ph_n>0 && el_n+mu_n>0   && ph_pt[0]>145 && jet_n>2 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n>0'
CRQ_L  = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && jet_n>4 && met_et<50 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>1000 && rt4<0.9'
CRW_L  = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n==0'
CRT_L  = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && met_et>50 && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n>1'

CRQ_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>400 && met_et<100 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>1500'
CRW_H = 'ph_n>0  && el_n+mu_n>0 && ph_pt[0]>145 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n==0'
CRT_H = 'ph_n>0  && el_n+mu_n>0 && ph_pt[0]>145 && met_et>50 && met_et<200 && dphi_jetmet>0.4 && meff>500 && bjet_n>1'


# Validation Regions

## Reverse dphi cuts
VR1_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>150 && jet_n>=4 && (dphi_jetmet<0.4 || dphi_gammet<0.4 || rt4>0.9) && meff>500'
VR2_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>150 && jet_n>=4 && (dphi_jetmet<0.4 || dphi_gammet<0.4 || rt4>0.9) && meff>1000'
VR3_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>150 && jet_n>=4 && (dphi_jetmet<0.4 || dphi_gammet<0.4 || rt4>0.9) && meff>2000'
VR4_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>150 && jet_n>=4 && (dphi_jetmet<0.4 || dphi_gammet<0.4 || rt4>0.9) && meff>2000'

VR1_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>200 && met_et>300 && jet_n>2 && dphi_jetmet<0.4 && meff>500'
VR2_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>200 && met_et>300 && jet_n>2 && dphi_jetmet<0.4 && meff>1000'
VR3_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>200 && met_et>300 && jet_n>2 && dphi_jetmet<0.4 && meff>2000'
VR4_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>200 && met_et>300 && jet_n>2 && dphi_jetmet<0.4 && meff>2000'

## Wgamma/ttbarg
VR5_L = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et<200 && dphi_jetmet>0.4 && meff>1000'
VR6_L = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et<200 && dphi_jetmet>0.4 && meff>1500'
VR7_L = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>1000'
VR8_L = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>1 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>1500'

VR5_H = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>400 && jet_n>1 && met_et<200 && dphi_jetmet>0.4 && meff>1000'
VR6_H = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>400 && jet_n>1 && met_et<200 && dphi_jetmet>0.4 && meff>1500'
VR7_H = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>400 && jet_n>1 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>1000'
VR8_H = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>400 && jet_n>1 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && meff>1500'

## Intermediate MET
VR9_L  = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>75 && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>500 && rt4<0.9'
VR10_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>75 && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>1000 && rt4<0.9'
VR11_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>75 && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>1500 && rt4<0.9'
VR12_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>75 && met_et<175 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'

VR9_H  = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>75 && met_et<175 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>500'
VR10_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>75 && met_et<175 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>1000'
VR11_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>75 && met_et<175 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>1500'
VR12_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>75 && met_et<175 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000'

## Intermediate Meff
VR13_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff<1000 && rt4<0.9'
VR14_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff<1500 && rt4<0.9'

VR13_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>400 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff<1000'
VR14_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>400 && jet_n>2 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff<1500'






# SR for ewk?
# SR_E = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>150 && jet_n>1 && dphi_jetmet>0.4 && dphi_gammet>0.4'

# Re-optimization 2016
# SR_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet4>0.4 && dphi_gammet>0.4 && meff>2000 && rt4<0.9'
# SR_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>400 && jet_n>2 && dphi_jetmet4>0.4 && dphi_gammet>0.4 && meff>2000' 

# SR_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet1>0.4 && meff>2000 && rt4<0.9'
# SR_H = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>400 && met_et>400 && jet_n>2 && dphi_jetmet1>0.4 && meff>1500'



# VRM2_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && ht>1000 && ht+met_et<2000 && rt4<0.9'
# VRM3_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && meff>2000 && rt4>0.9'
# VRM4_L = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet<0.4 && ht+met_et>2000'

# VRW1_L = 'ph_n>0 && el_n+mu_n>0 && ph_pt[0]>145 && jet_n>4 && met_et>100 && met_et<200 && dphi_jetmet>0.4 && ht>500 && bjet_n==0 && rt4<0.9'


# CRQ2_L  = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>50  && met_et<100 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && ht>1000 && rt4<0.9'
# CRQ3_L  = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>100 && met_et<150 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && ht>1000 && rt4<0.9'
# CRQ4_L  = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et>150 && met_et<200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && ht>1000 && rt4<0.9'
# CRQ5_L  = 'ph_n==1 && el_n+mu_n==0 && ph_pt[0]>145 && met_et<150 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && ht>1000 && rt4<0.9'

# VRM3_L = 'ph_n>0 && ph_pt[0]>145 && met_et>150 && jet_n>4 && ht+met_et>1000 && dphi_jetmet<0.4'
# VRM4_L = 'ph_n>0 && ph_pt[0]>145 && met_et>150 && jet_n>4 && ht+met_et>1000 && rt4>0.9'

# VRM1_H = 'ph_n==1 && ph_pt[0]>145 && met_et>100 && met_et<200 && jet_n>4 && ht+met_et>2000'
# VRM2_H = 'ph_n==1 && ph_pt[0]>145 && met_et>180 && jet_n>2 && ht+met_et>1500 && ht+met_et<2000'
# VRM3_H = 'ph_n==1 && ph_pt[0]>145 && met_et>150 && jet_n>4 && ht+met_et>1000 && dphi_jetmet<0.4'
# VRM4_H = 'ph_n==1 && ph_pt[0]>145 && met_et>150 && jet_n>4 && ht+met_et>1000 && rt4>0.9'

# VRM1_H = 'ph_n==1 && ph_pt[0]>145 && met_et>100 && met_et<200 && jet_n>2 && ht+met_et>2000'
# VRM2_H = 'ph_n==1 && ph_pt[0]>145 && met_et>100 && met_et<200 && jet_n>2 && ht+met_et>1500 && ht+met_et<2000'

# VRM3_H = 'ph_n==1 && ph_pt[0]>145 && met_et>100 && jet_n>4 && dphi_jetmet<0.4'
# VRM4_H = 'ph_n==1 && ph_pt[0]>145 && met_et>100 && jet_n>4 && rt4<0.4'

# VRM4_L = 'ph_n==1 && ph_pt[0]>145 && met_et>100 && met_et<200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && ht+met_et>2000'

# VRM5_L = 'ph_n==1 && ph_pt[0]>145 && met_et>100 && met_et<200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && ht+met_et>1500'
# VRM6_L = 'ph_n==1 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet<0.4 && ht+met_et>1500'

# VRM7_L = 'ph_n==1 && ph_pt[0]>145 && met_et>200 && jet_n<4' # && dphi_gammet<0.4 && ht+met_et>1500'
# VRM8_L = 'ph_n==1 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && ht+met_et>1500 && rt4>0.9'

#VRM_H = 'ph_n==1 && ph_pt[0]>145 && met_et>100 && met_et<200 && jet_n>2 && jet_pt[0]>50 && jet_pt[1]>50 && dphi_jetmet>0.4 && dphi_gammet>0.4 && ht+met_et>1800'

# meff-sideband
# VRF_L  = 'ph_n==1 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && ht+met_et>1000 && ht+met_et<2000' ## && rt4<0.9'
# VRF2_L = 'ph_n==1 && ph_pt[0]>145 && met_et>200 && jet_n>4 && dphi_jetmet>0.4 && dphi_gammet>0.4 && ht+met_et>1500 && ht+met_et<2000' ## && rt4<0.9'
#VRF_H = 'ph_n==1 && ph_pt[0]>145 && met_et>400 && jet_n>2 && jet_pt[0]>50 && jet_pt[1]>50 && dphi_jetmet>0.4 && dphi_gammet>0.4 && ht+met_et>1000 && ht+met_et<1500'

# QCD-enriched  (reversed dphi(jet,MET))
#VRQ_L = 'ph_n==1 && ph_pt[0]>145 && jet_n>4 && met_et>150 && (dphi_jetmet<0.4 || dphi_gammet<0.4) && ht+met_et>2000'
#VRQ_H = 'ph_n==1 && ph_pt[0]>145 && _n+mu_n)==0 && jet_n>=2 && jet_pt[0]>40  && jet_pt[1]>40  && met_et>300 && ht>800 && dphi_gamjet<2.0 && dphi_jetmet<0.4'

# QCD-enriched  (reversed R_T^4)
#VRR_L = 'ph_n==1 && ph_pt[0]>145 && (el_n+mu_n)==0 && jet_n>=4 && jet_pt[0]>100 && jet_pt[1]>100 && met_et>200 && ht>0 && rt4>0.85 && dphi_jetmet>0.4'


