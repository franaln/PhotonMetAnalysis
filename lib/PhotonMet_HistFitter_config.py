#------------------------#
# single photon analysis #
# HistFitter config file #
#------------------------#

import os
import sys
import shutil

from configManager import configMgr
from configWriter import fitConfig, Measurement, Channel, Sample
from systematic import Systematic

#from style import colors_dict

def color(sample):
    return ROOT.kBlack #ROOT.TColor.GetColor(colors_dict[sample])

def rmdir(dir_):
    try:
        print 'Removing dir %s' % dir_
        shutil.rmtree(dir_)
    except OSError:
        pass

# Options
base_analysis  = "PhotonMet"

print "Found user args %s" % configMgr.userArg

# Options
parser = argparse.ArgumentParser('PhotonMet_HistFitter_config')

parser.add_argument("-i", dest='hist_file')
parser.add_argument("--sr", dest='signal_region')
parser.add_argument("--data", default='data')

parser.add_argument("--val", action='store_true')
parser.add_argument("--mc", action='store_true')
parser.add_argument("--syst", action='store_true')
parser.add_argument("--rm", action='store_true')
parser.add_argument("--asimov", action='store_true')
parser.add_argument("--ntoys", type=int, default=5000)
parser.add_argument("--npoints", type=int, default=1)
parser.add_argument("--sigxs", action='store_true')

userArg = [ i.replace('"', '') for i in configMgr.userArg.split() ]
args = parser.parse_args(userArg)
print "Parsed user args %s" % str(args)

hist_file  = args.hist_file 
signal_region = args.signal_region
do_validation = args.val 
use_mc_bkgs   = args.mc 
do_syst       = args.syst 

data_name = args.data

nom_name  = 'Nom'
model_hypo_test = 'GGM'
do_signal_theory_unc = args.sigxs
variable = 'cuts'
binning  = (1, 0.5, 1.5) 

configMgr.writeXML = False  #for debugging

#--- Flags to control which fit is executed
useStat = True
configMgr.blindSR = False #True
configMgr.blindCR = False
configMgr.blindVR = False
configMgr.useSignalInBlindedData = False

#--- Parameters for hypothesis test
configMgr.calculatorType = 2 if args.asimov else 0 # 0: toys, 2: asimov?
configMgr.testStatType = 3
configMgr.nPoints = args.npoints
configMgr.nTOYs = args.ntoys


#--------------------------------
# Now we start to build the model
#--------------------------------

if myFitType == FitType.Background:
    fittag = 'bkgonly'
elif myFitType == FitType.Exclusion:
    fittag = 'excl'
elif myFitType == FitType.Discovery:
    fittag = 'disc'

opttag = ''
if use_mc_bkgs:
    opttag += '_mc'
if not do_syst:
    opttag += '_nosys'

if opttag:
    configMgr.analysisName = "%sAnalysis_%s%s_%s" % (base_analysis, fittag, opttag, signal_region)
else:
    configMgr.analysisName = "%sAnalysis_%s_%s" % (base_analysis, fittag, signal_region)

configMgr.histCacheFile  = hist_file
configMgr.outputFileName = 'results/%s/Output.root' % configMgr.analysisName

if args.rm and configMgr.analysisName:
    rmdir('./results/%s' % configMgr.analysisName)
    rmdir('./config/%s' % configMgr.analysisName)
    rmdir('./data/%s' % configMgr.analysisName)


## Read the histograms already produced
inputFileNames = [configMgr.histCacheFile, ]
    
## Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi  = 13.3 # Luminosity of input TTree after weighting
configMgr.outputLumi = 13.3 # Luminosity required for output histograms
configMgr.setLumiUnits("fb-1")

## Regions
sr_name = signal_region[:-1] # could be SR or SRincl
sr_type = signal_region[-1].upper()

regions = [
    'SR', 
    'SRi',
    'CRQ', 'CRW', 'CRT',
    'VRM1', 'VRM2', 'VRM3', 
    'VRD1', 'VRD2', 'VRD3',
    'VRL1', 'VRL2', 'VRL3', 'VRL4',
  ]

for r in regions:
    configMgr.cutsDict[r] = '' # not used anyway


#-----------------
# Samples 
#-----------------

# W/Z + jets
wjets_sample = Sample('wjets', color("wjets"))
zjets_sample = Sample('zjets', color("zjets"))

wjets_sample.setNormByTheory()
zjets_sample.setNormByTheory()

# ttbar
ttbar_sample  = Sample('ttbar', color("ttbar"))
ttbarg_sample = Sample('ttbarg', color("ttbarg"))

ttbar_sample.setNormByTheory()
ttbarg_sample.setNormFactor("mu_t", 1., 0., 2.)   

# W/Z gamma
wgamma_sample     = Sample('wgamma', color("wgamma"))
zllgamma_sample   = Sample('zllgamma', color("zllgamma"))
znunugamma_sample = Sample('znunugamma', color("znunugamma"))
#vqqgamma_sample   = Sample("vqqgamma", color('vqqgamma'))

zllgamma_sample.setNormByTheory()
znunugamma_sample.setNormByTheory()
wgamma_sample.setNormFactor("mu_w", 1., 0., 2.)

# Fake met
photonjet_sample = Sample('photonjet', color("photonjet"))
multijet_sample  = Sample('multijet', color("multijet"))

multijet_sample.setNormByTheory()
photonjet_sample.setNormFactor("mu_q", 1., 0., 2.)


# Diphoton backgrounds
diphoton_sample    = Sample('diphoton', color("diphoton"))
vgammagamma_sample = Sample('vgammagamma', color("vgammagamma"))

diphoton_sample.setNormByTheory()
vgammagamma_sample.setNormByTheory()

# Fakes
if data_name == 'data15':
    efake_sample = Sample("efake15", color("efake"))
    jfake_sample = Sample("jfake15", color("jfake"))
elif data_name == 'data16':
    efake_sample = Sample("efake16", color("efake"))
    jfake_sample = Sample("jfake16", color("jfake"))
else: # should be 'data'
    efake_sample = Sample("efake", color("efake"))
    jfake_sample = Sample("jfake", color("jfake"))

# Data
data_sample = Sample(data_name, ROOT.kBlack)
data_sample.setData()

# stat uncertainty
wjets_sample.setStatConfig(useStat)
zjets_sample.setStatConfig(useStat)
wgamma_sample.setStatConfig(useStat)
zllgamma_sample.setStatConfig(useStat)
znunugamma_sample.setStatConfig(useStat)
ttbar_sample.setStatConfig(useStat)
ttbarg_sample.setStatConfig(useStat)
photonjet_sample.setStatConfig(useStat)
multijet_sample.setStatConfig(useStat)
diphoton_sample.setStatConfig(useStat)
vgammagamma_sample.setStatConfig(useStat)
#vqqgamma_sample.setStatConfig(useStat)

if use_mc_bkgs:
    bkg_samples = [
        wgamma_sample, 
        zllgamma_sample,
        znunugamma_sample,
        wjets_sample,
        zjets_sample,
        ttbar_sample,
        ttbarg_sample,
        photonjet_sample,
        multijet_sample,
        ]
else:
    bkg_samples = [
        wgamma_sample, 
        zllgamma_sample,
        znunugamma_sample,
        ttbarg_sample,
        photonjet_sample,
        efake_sample,
        jfake_sample,
        diphoton_sample,
        vgammagamma_sample,
#        vqqgamma_sample,
        ]

data_samples = [data_sample,]


# ------------
# Systematics
# ------------
configMgr.nomName = 'Nom'

def Sys(name='', kind='overallSys'):
    return Systematic(name, nom_name, '_'+name+'Up', '_'+name+'Down', 'tree', kind)


## Detector uncertainties
syst_jets = [
    Sys('JET_EtaIntercalibration_NonClosure'),
    Sys('JET_GroupedNP_1'),
    Sys('JET_GroupedNP_2'),
    Sys('JET_GroupedNP_3'),

    Sys('JET_Rtrk_Baseline_Kin'),
    Sys('JET_Rtrk_Baseline_Sub'),
    Sys('JET_Rtrk_Modelling_Kin'),
    Sys('JET_Rtrk_Modelling_Sub'),
    Sys('JET_Rtrk_TotalStat_Kin'),
    Sys('JET_Rtrk_TotalStat_Sub'),
    Sys('JET_Rtrk_Tracking_Kin'),
    Sys('JET_Rtrk_Tracking_Sub'),

    Systematic('JET_JER_SINGLE_NP', nom_name, '_JET_JER_SINGLE_NPUp', '', 'tree', 'histoSysOneSide'),
]

syst_btagging = []

syst_met = [
    Systematic('MET_SoftTrk_ResoPara', nom_name, '_MET_SoftTrk_ResoParaUp', '', 'tree', 'histoSysOneSide'),
    Systematic('MET_SoftTrk_ResoPerp', nom_name, '_MET_SoftTrk_ResoPerpUp', '', 'tree', 'histoSysOneSide'),
    Systematic('MET_SoftTrk_Scale', nom_name, '_MET_SoftTrk_ScaleUp', '_MET_SoftTrk_ScaleDown', 'tree', 'overallSys'),
]

syst_egamma = [
    Sys("EG_RESOLUTION_ALL"),
    Sys("EG_SCALE_ALL"),
    Sys('PH_Iso_DDonoff'),
]

syst_muon = [
    Sys("MUONS_SCALE"),
    Sys("MUONS_MS"),
    Sys("MUONS_ID"),
]

# Fake photon backgrounds
syst_feg = Systematic('Feg', nom_name, '_FegUp', '_FegDown', 'tree', 'overallSys')
syst_fjg = Systematic('Fjg', nom_name, '_FjgUp', '_FjgDown', 'tree', 'overallSys')

syst_weight = [
    Sys('EL_EFF_ID_TOTAL_1NPCOR_PLUS_UNCOR'),
    Sys('EL_EFF_Iso_TOTAL_1NPCOR_PLUS_UNCOR'),
    Sys('EL_EFF_Reco_TOTAL_1NPCOR_PLUS_UNCOR'),
    Sys('EL_EFF_Trigger_TOTAL_1NPCOR_PLUS_UNCOR'),
    Sys('EL_EFF_TriggerEff_TOTAL_1NPCOR_PLUS_UNCOR'),

    # Sys('FT_EFF_B_systematics'),
    # Sys('FT_EFF_C_systematics'),
    # Sys('FT_EFF_Light_systematics'),
    # # Sys('FT_EFF_extrapolation'),

    Sys('JvtEfficiency'),

    Sys('MUON_EFF_STAT'),
    Sys('MUON_EFF_STAT_LOWPT'),
    Sys('MUON_EFF_SYS'),
    Sys('MUON_EFF_SYS_LOWPT'),
    Sys('MUON_EFF_TrigStatUncertainty'),
    Sys('MUON_EFF_TrigSystUncertainty'),
    Sys('MUON_ISO_STAT'),
    Sys('MUON_ISO_SYS'),

    Sys('PH_EFF_ID_Uncertainty'),

    Sys('PRW_DATASF'),
]

syst_to_all = syst_jets +syst_met + syst_egamma + syst_muon + syst_weight

## Theory Uncertainties

## gamjet
sigma_gamjet_srl = 0.57
sigma_gamjet_srh = 0.43

if sr_type == 'L':
    syst_gamjet_theo = Systematic("theoSysGJ", 1 , 1+sigma_gamjet_srl, 1-sigma_gamjet_srl, "user", "userOverallSys")
else:
    syst_gamjet_theo = Systematic("theoSysGJ", 1 , 1+sigma_gamjet_srh, 1-sigma_gamjet_srh, "user", "userOverallSys")

## wgamma
sigma_wgamma_srl   = 0.065
sigma_wgamma_srh   = 0.083
sigma_wgamma_crql  = 0.056
sigma_wgamma_crqh  = 0.070
sigma_wgamma_crwtl = 0.044
sigma_wgamma_crwth = 0.044

if sr_type == 'L':
    syst_wgamma_theo_sr   = Systematic("theoSysWG", 1 , 1+sigma_wgamma_srl,   1-sigma_wgamma_srl,   "user", "userOverallSys")
    syst_wgamma_theo_crq  = Systematic("theoSysWG", 1 , 1+sigma_wgamma_crql,  1-sigma_wgamma_crql,  "user", "userOverallSys")
    syst_wgamma_theo_crwt = Systematic("theoSysWG", 1 , 1+sigma_wgamma_crwtl, 1-sigma_wgamma_crwtl, "user", "userOverallSys")
else:
    syst_wgamma_theo_sr   = Systematic("theoSysWG", 1 , 1+sigma_wgamma_srh,   1-sigma_wgamma_srh,   "user", "userOverallSys")
    syst_wgamma_theo_crq  = Systematic("theoSysWG", 1 , 1+sigma_wgamma_crqh,  1-sigma_wgamma_crqh,  "user", "userOverallSys")
    syst_wgamma_theo_crwt = Systematic("theoSysWG", 1 , 1+sigma_wgamma_crwth, 1-sigma_wgamma_crwth, "user", "userOverallSys")

## ttgamma
sigma_ttgamma_srl   = 0.133
sigma_ttgamma_srh   = 0.372
sigma_ttgamma_crql  = 0.136
sigma_ttgamma_crqh  = 0.177
sigma_ttgamma_crwtl = 0.085
sigma_ttgamma_crwth = 0.085

if sr_type == 'L':
    syst_ttgamma_theo_sr   = Systematic("theoSysTG", 1 , 1+sigma_ttgamma_srl,   1-sigma_ttgamma_srl,   "user", "userOverallSys")
    syst_ttgamma_theo_crq  = Systematic("theoSysTG", 1 , 1+sigma_ttgamma_crql,  1-sigma_ttgamma_crql,  "user", "userOverallSys")
    syst_ttgamma_theo_crwt = Systematic("theoSysTG", 1 , 1+sigma_ttgamma_crwtl, 1-sigma_ttgamma_crwtl, "user", "userOverallSys")
else:
    syst_ttgamma_theo_sr   = Systematic("theoSysTG", 1 , 1+sigma_ttgamma_srh,   1-sigma_ttgamma_srh,   "user", "userOverallSys")
    syst_ttgamma_theo_crq  = Systematic("theoSysTG", 1 , 1+sigma_ttgamma_crqh,  1-sigma_ttgamma_crqh,  "user", "userOverallSys")
    syst_ttgamma_theo_crwt = Systematic("theoSysTG", 1 , 1+sigma_ttgamma_crwth, 1-sigma_ttgamma_crwth, "user", "userOverallSys")

theoSysZG    = Sys('theoSysZG') 
sigXsec      = Sys('SigXSec')



# Add Sample Specific Systematics (apparently it's needed to add these systs to the samples *BEFORE* adding them to the FitConfig
if do_syst: 

    #-- sample specific systematics
    zllgamma_sample.addSystematic(theoSysZG)
    znunugamma_sample.addSystematic(theoSysZG)
    # ttbarg_sample.addSystematic(theoSysTopG)
    # wgamma_sample.addSystematic(theoSysWG)
    photonjet_sample.addSystematic(syst_gamjet_theo)

    efake_sample.addSystematic(syst_feg)
    jfake_sample.addSystematic(syst_fjg)
    
    #-- global systematics
    for gsyst in syst_to_all:

        for sample in bkg_samples:
            if sample.name.startswith('efake') or sample.name.startswith('jfake'):
                continue

            sample.addSystematic(gsyst)

    #-- channel specific systematics (still *before* adding them to FitConfig)
    # for bsyst in syst_bjet:
    #     CRW.addSystematic(bsyst)
    #     CRT.addSystematic(bsyst)



#---------
#   Fit
#---------

# Background only fit
if myFitType == FitType.Background:
    fitconfig = configMgr.addFitConfig('BkgOnlyFit')

# Discovery fit
elif myFitType == FitType.Discovery:
    fitconfig = configMgr.addFitConfig('DiscoveryFit')

    unitary_sample = Sample('Unitary', ROOT.kViolet+5)
    unitary_sample.setNormFactor('mu_SIG', 1, 0, 10)
    unitary_sample.buildHisto([1,], 'SR', '0.5')

    fitconfig.addSamples(unitary_sample)
    fitconfig.setSignalSample(unitary_sample)
    
# Exclusion fit
elif myFitType == FitType.Exclusion:
    fitconfig = configMgr.addFitConfig('ExclusionFit')


fitconfig.addSamples(bkg_samples + data_samples)

# Measurement
measName = "BasicMeasurement"
measLumi = 1.0
measLumiError = 0.029 # Preliminar for ICHEP: 2.9% (3.7% for 2016 and 2.1% for 2015)

meas = fitconfig.addMeasurement(measName, measLumi, measLumiError)

if useStat:
    fitconfig.statErrThreshold = 0.05 #low stat error now (as in 2L-paper13)
else:
    fitconfig.statErrThreshold = None

meas.addPOI("mu_SIG")
meas.addParamSetting("Lumi", True)

constraint_channels = []
validation_channels = []
signal_channels = []


# ---------------
# Signal region 
# ---------------
SR = fitconfig.addChannel(variable, [sr_name], *binning)
signal_channels.append(SR)

# -----------------
#  Control regions 
# -----------------
CRQ = fitconfig.addChannel(variable, ['CRQ'], *binning)
CRW = fitconfig.addChannel(variable, ["CRW"], *binning)
CRT = fitconfig.addChannel(variable, ["CRT"], *binning)

constraint_channels.append(CRQ)
constraint_channels.append(CRW)
constraint_channels.append(CRT)

wgamma_sample.setNormRegions(["CRW", variable])
ttbarg_sample.setNormRegions(["CRT",variable])
photonjet_sample.setNormRegions(["CRQ",variable])

# Add theoretical systematics region specific
if do_syst:
    SR. getSample("wgamma").addSystematic(syst_wgamma_theo_sr)
    CRQ.getSample("wgamma").addSystematic(syst_wgamma_theo_crq)
    CRW.getSample("wgamma").addSystematic(syst_wgamma_theo_crwt)
    CRT.getSample("wgamma").addSystematic(syst_wgamma_theo_crwt)

    SR. getSample("ttbarg").addSystematic(syst_ttgamma_theo_sr)
    CRQ.getSample("ttbarg").addSystematic(syst_ttgamma_theo_crq)
    CRW.getSample("ttbarg").addSystematic(syst_ttgamma_theo_crwt)
    CRT.getSample("ttbarg").addSystematic(syst_ttgamma_theo_crwt)




# -------------------
# Validation regions 
# -------------------
if do_validation:

    VRM1  = fitconfig.addChannel(variable, ["VRM1"], *binning)
    VRM2  = fitconfig.addChannel(variable, ["VRM2"], *binning)
    VRM3  = fitconfig.addChannel(variable, ["VRM3"], *binning)

    validation_channels.append(VRM1)
    validation_channels.append(VRM2)
    validation_channels.append(VRM3)

    if sr_type == 'L':
        VRD1  = fitconfig.addChannel(variable, ["VRD1"], *binning)
        VRD2  = fitconfig.addChannel(variable, ["VRD2"], *binning)
        VRD3  = fitconfig.addChannel(variable, ["VRD3"], *binning)

        validation_channels.append(VRD1)
        validation_channels.append(VRD2)
        validation_channels.append(VRD3)

    VRL1  = fitconfig.addChannel(variable, ["VRL1"], *binning)
    VRL2  = fitconfig.addChannel(variable, ["VRL2"], *binning)
    VRL3  = fitconfig.addChannel(variable, ["VRL3"], *binning)
    VRL4  = fitconfig.addChannel(variable, ["VRL4"], *binning)

    validation_channels.append(VRL1)
    validation_channels.append(VRL2)
    validation_channels.append(VRL3)
    validation_channels.append(VRL4)

   


# Add CR/VR/SR 
fitconfig.setBkgConstrainChannels(constraint_channels)

if myFitType == FitType.Background: 
    validation_channels.append(SR) #--- Define SR as validation region.

    # For now as a validation region. FIX!
    if sr_name == 'SR': 
        SRi  = fitconfig.addChannel(variable, ["SRi"], *binning)
        validation_channels.append(SRi)

else:
    fitconfig.setSignalChannels(signal_channels) #--- Define SR as signal region.

if do_validation:
    fitconfig.setValidationChannels(validation_channels)


if myFitType == FitType.Exclusion:

    points = []
    
    try:
        sigSamples
    except NameError:
        sigSamples = None

    for sid in sigSamples:
        m3, mu = sid.split('_')
        points.append((int(m3), int(mu)))
    
    for (m3, mu) in points:
        print "Adding fit config for sample (%d, %d)" % (m3, mu)
        exclfit = configMgr.addFitConfigClone(fitconfig, "GGM_M3_mu_%d_%d" % (m3, mu))

        sigSample = Sample("GGM_M3_mu_%d_%d" % (m3, mu), ROOT.kOrange+3)
        sigSample.setNormByTheory()
        sigSample.setStatConfig(useStat)
        sigSample.setNormFactor("mu_SIG", 1., 0., 5.)

        if do_signal_theory_unc:
            configMgr.fixSigXSec = True
            sigSample.addSystematic(sigXsec) #--- Special uncertainty. Theory variations (creates extra files)

        exclfit.addSamples(sigSample)
        exclfit.setSignalSample(sigSample)
        exclfit.setSignalChannels(signal_channels)

