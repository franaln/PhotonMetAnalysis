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

from drawlib import colors_dict
from rootutils import get_color
from binning import get_binning

def color(sample):
    return get_color(colors_dict[sample])

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

parser.add_argument("--val", action='store_true')
parser.add_argument("--mc", action='store_true')
parser.add_argument("--syst", action='store_true')
parser.add_argument("--rm", action='store_true')

userArg = [ i.replace('"', '') for i in configMgr.userArg.split()]
args = parser.parse_args(userArg)
print "Parsed user args %s" % str(args)



# user_arg_list  = configMgr.userArg.split(',')
hist_file  = args.hist_file #user_arg_list[0]
signal_region  = args.signal_region #user_arg_list[1]
do_validation = args.val #('validation' in user_arg_list)
use_mc_bkgs   = args.mc #('mc' in user_arg_list)
do_syst       = args.syst #('syst' in user_arg_list)

nom_name      = 'Nom'
model_hypo_test = 'GGM'
do_signal_theory_unc = True
variable = 'cuts'
binning  = get_binning(variable)

region_str = "%s_%s" % (base_analysis, signal_region)


configMgr.writeXML = True  #for debugging


#--- Flags to control which fit is executed
useStat = True

configMgr.blindSR = False #True
configMgr.blindCR = False
configMgr.blindVR = False
configMgr.useSignalInBlindedData = False

#--- Parameters for hypothesis test
configMgr.calculatorType = 2 # 0: toys, 2: asimov?
configMgr.testStatType = 3
configMgr.nPoints = 20
configMgr.nTOYs = 5000

muSigInitValue = [0.05, 0., 5.]


#--------------------------------
# Now we start to build the model
#--------------------------------

if myFitType == FitType.Background:
    fittag = 'bkgonly'
elif myFitType == FitType.Exclusion:
    fittag = 'excl'
elif myFitType == FitType.Discovery:
    fittag = 'disc'

if use_mc_bkgs:
    configMgr.analysisName = "%sAnalysis_%s_mc_%s" % (base_analysis, fittag, signal_region)
else:
    configMgr.analysisName = "%sAnalysis_%s_%s" % (base_analysis, fittag, signal_region)

configMgr.histCacheFile  = hist_file
configMgr.outputFileName = 'results/%s/Output.root' % configMgr.analysisName

if args.rm:
    rmdir('./results/%s' % configMgr.analysisName)
    rmdir('./config/%s' % configMgr.analysisName)
    rmdir('./data/%s' % configMgr.analysisName)


## Read the histograms already produced
inputFileNames = [configMgr.histCacheFile,]
    
## Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi  = 3.2 # Luminosity of input TTree after weighting
configMgr.outputLumi = 3.2 # Luminosity required for output histograms
configMgr.setLumiUnits("fb-1")

## Regions
regions = [
    'SR', 
    'SRincl',
    'CRQ', 'CRW', 'CRT',
    'VRM1', 'VRM2', 'VRM3', 
    'VRD1', 'VRD2', 'VRD3',
    'VRL1', 'VRL2', 'VRL3', 'VRL4',
  ]

for r in regions:
    configMgr.cutsDict[r] = '' # not used anyway


## Parameters of the Measurement
measName = "BasicMeasurement"
measLumi = 1.0
measLumiError = 0.021


#-----------------
# Samples 
#-----------------

# W/Z + jets
wjets_sample = Sample('wjets', color("wjets"))
zjets_sample = Sample('zjets', color("zjets"))
#dibosonSample = Sample("diboson", colors_dict["diboson"])

wjets_sample.setNormByTheory()
zjets_sample.setNormByTheory()

# ttbar
ttbar_sample  = Sample('ttbar', color("ttbar"))
ttbarg_sample = Sample('ttbarg', color("ttbarg"))
#topSample     = Sample("Top", colors_dict["ttbar"]) 
#topSample.setTreeName("ttbar")  ##change tree name for ttbar
#topgSample       = Sample("topgamma", colors_dict["topgamma"])

ttbarg_sample.setNormByTheory()
ttbarg_sample.setNormFactor("mu_t", 1., 0., 5.)   

# W/Z gamma
wgamma_sample     = Sample('wgamma', color("wgamma"))
zllgamma_sample   = Sample('zllgamma', color("zllgamma"))
znunugamma_sample = Sample('znunugamma', color("znunugamma"))
#VqqgammaSample   = Sample("vqqgamma", colors_dict["vqqgamma"])

zllgamma_sample.setNormByTheory()
znunugamma_sample.setNormByTheory()
wgamma_sample.setNormByTheory()
wgamma_sample.setNormFactor("mu_w", 1., 0., 5.)

# QCD
photonjet_sample = Sample('photonjet', color("photonjet"))
multijet_sample = Sample('multijet', color("multijet"))

multijet_sample.setNormByTheory()
photonjet_sample.setNormByTheory()
photonjet_sample.setNormFactor("mu_q", 1., 0., 5.)

# Fakes
efake_sample  = Sample("efake", color("efake"))
jfake_sample = Sample("jfake", color("jfake"))

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

# Data
data_sample = Sample('data', ROOT.kBlack)
data_sample.setData()

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
    Sys("JET_GroupedNP_1"),
    Sys("JET_GroupedNP_2"),
    Sys("JET_GroupedNP_3"),
    Sys("JET_JER_SINGLE_NP"),
]

syst_btagging = []

syst_met = [
    Sys("MET_SoftTrk_ResoPara"),
    Sys("MET_SoftTrk_ResoPerp"),
    Sys("MET_SoftTrk_Scale"),
]

syst_egamma = [
    Sys("EG_RESOLUTION_ALL"),
    Sys("EG_SCALE_ALL"),
]

syst_muon = [
    Sys("MUONS_SCALE"),
    Sys("MUONS_MS"),
    Sys("MUONS_ID"),
]

# #Efake background
syst_feg = Sys('Feg')

#Jet fake background
#syst_jFakeRate = getSys('jfake', 'histoSys') 

syst_weight = [
    # Sys('EL_EFF_ID_CorrUncertaintyNP0'),
    # Sys('EL_EFF_ID_CorrUncertaintyNP1'),
    # Sys('EL_EFF_ID_CorrUncertaintyNP2'),
    # Sys('EL_EFF_ID_CorrUncertaintyNP3'),
    # Sys('EL_EFF_ID_CorrUncertaintyNP4'),
    # Sys('EL_EFF_ID_CorrUncertaintyNP5'),
    # Sys('EL_EFF_ID_CorrUncertaintyNP6'),
    # Sys('EL_EFF_ID_CorrUncertaintyNP7'),
    # Sys('EL_EFF_ID_CorrUncertaintyNP8'),
    # Sys('EL_EFF_ID_CorrUncertaintyNP9'),
    # Sys('EL_EFF_ID_CorrUncertaintyNP10'),
    # Sys('EL_EFF_ID_CorrUncertaintyNP11'),
    # Sys('EL_EFF_ID_TOTAL_UncorrUncertainty'),
    # Sys('EL_EFF_Iso_CorrUncertaintyNP0'),
    # Sys('EL_EFF_Iso_CorrUncertaintyNP1'),
    # Sys('EL_EFF_Iso_CorrUncertaintyNP2'),
    # Sys('EL_EFF_Iso_CorrUncertaintyNP3'),
    # Sys('EL_EFF_Iso_CorrUncertaintyNP4'),
    # Sys('EL_EFF_Iso_CorrUncertaintyNP5'),
    # Sys('EL_EFF_Iso_CorrUncertaintyNP6'),
    # Sys('EL_EFF_Iso_CorrUncertaintyNP7'),
    # Sys('EL_EFF_Iso_CorrUncertaintyNP8'),
    # Sys('EL_EFF_Iso_CorrUncertaintyNP9'),
    # Sys('EL_EFF_Iso_CorrUncertaintyNP10'),
    # Sys('EL_EFF_Iso_TOTAL_UncorrUncertainty'),
    # Sys('EL_EFF_Reco_CorrUncertaintyNP0'),
    # Sys('EL_EFF_Reco_CorrUncertaintyNP1'),
    # Sys('EL_EFF_Reco_CorrUncertaintyNP2'),
    # Sys('EL_EFF_Reco_CorrUncertaintyNP3'),
    # Sys('EL_EFF_Reco_CorrUncertaintyNP4'),
    # Sys('EL_EFF_Reco_CorrUncertaintyNP5'),
    # Sys('EL_EFF_Reco_CorrUncertaintyNP6'),
    # Sys('EL_EFF_Reco_CorrUncertaintyNP7'),
    # Sys('EL_EFF_Reco_CorrUncertaintyNP8'),
    # Sys('EL_EFF_Reco_CorrUncertaintyNP9'),
    # Sys('EL_EFF_Reco_TOTAL_UncorrUncertainty'),
    # Sys('EL_EFF_Trigger_CorrUncertaintyNP0'),
    # Sys('EL_EFF_Trigger_CorrUncertaintyNP1'),
    # Sys('EL_EFF_Trigger_CorrUncertaintyNP2'),
    # Sys('EL_EFF_Trigger_CorrUncertaintyNP3'),
    # Sys('EL_EFF_Trigger_CorrUncertaintyNP4'),
    # Sys('EL_EFF_Trigger_TOTAL_UncorrUncertainty'),
    Sys('FT_EFF_B_systematics'),
    Sys('FT_EFF_C_systematics'),
    Sys('FT_EFF_Light_systematics'),
    Sys('FT_EFF_extrapolation'),
    Sys('JvtEfficiency'),
    # Sys('MUON_EFF_STAT'),
    # Sys('MUON_EFF_STAT_LOWPT'),
    # Sys('MUON_EFF_SYS'),
    # Sys('MUON_EFF_SYS_LOWPT'),
    # Sys('MUON_EFF_TrigStatUncertainty'),
    # Sys('MUON_EFF_TrigSystUncertainty'),
    # Sys('MUON_ISO_STAT'),
    # Sys('MUON_ISO_SYS'),
    Sys('PH_EFF_ID_Uncertainty'),
]

syst_to_all = syst_met  + syst_egamma + syst_jets + syst_muon + syst_weight


## Theory Uncertainties
theoSysGJ    = Sys('theoSysGJ') #, 'histoSys')
theoSysTopG  = Sys('theoSysTopG')
theoSysWG    = Sys('theoSysWG')
theoSysZG    = Sys('theoSysZG') #, 'histoSys')
sigXsec      = Sys('SigXSec')

# theoSysGJgen = getSys('theoSysGJgen', 'histoSys')
# theoSysTop  = getSys('theoSysTop')
# theoSysSingleTop  = getSys('theoSysSingleTop')
# theoSysSingleTopG  = getSys('theoSysSingleTopG')
# theoSysWZ  = getSys('theoSysWZ')
# theoSysVV  = getSys('theoSysVV')



# Add Sample Specific Systematics (apparently it's needed to add these systs to the samples *BEFORE* adding them to the FitConfig
if do_syst: 

    #-- sample specific systematics
    # ttbarghadSample.addSystematic(theoSysTopG)
    # topgSample.addSystematic(theoSysSingleTopG)

    ttbarg_sample.addSystematic(theoSysTopG)
    wgamma_sample.addSystematic(theoSysWG)
    zllgamma_sample.addSystematic(theoSysZG)
    znunugamma_sample.addSystematic(theoSysZG)
    photonjet_sample.addSystematic(theoSysGJ)

    efake_sample.addSystematic(syst_feg)
    # jfake_sample.addSystematic(syst_jFakeRate)

    #-- global systematics
    for gsyst in syst_to_all:
        # fitconfig.addSystematic(gsyst)

        for sample in bkg_samples:
            if sample.name in ['efake', 'jfake']:
                continue

            print "*** Adding %s in %s" % (gsyst.name, sample.name) 
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
    
    # unitary_sample2 = Sample('Unitary', ROOT.kViolet+5)
    # unitary_sample2.setNormFactor('mu_SIG', 1, 0, 10)
    # unitary_sample2.buildHisto([0,], 'CRQ', '0.5')
    # fitconfig.addSamples(unitary_sample2)
    
    # unitary_sample3 = Sample('Unitary', ROOT.kViolet+5)
    # unitary_sample3.setNormFactor('mu_SIG', 1, 0, 10)
    # unitary_sample3.buildHisto([0,], 'CRW', '0.5')
    # fitconfig.addSamples(unitary_sample3)
    
    # unitary_sample4 = Sample('Unitary', ROOT.kViolet+5)
    # unitary_sample4.setNormFactor('mu_SIG', 1, 0, 10)
    # unitary_sample4.buildHisto([0,], 'CRT', '0.5')
    # fitconfig.addSamples(unitary_sample4)
    
# Exclusion fit
elif myFitType == FitType.Exclusion:
    fitconfig = configMgr.addFitConfig('ExclusionFit')


fitconfig.addSamples(bkg_samples + data_samples)

meas = fitconfig.addMeasurement(measName, measLumi, measLumiError)

# if not use_mc_bkgs:
#     meas.addParamSetting("mu_efake", True, 1) # fix efake BKG
#     meas.addParamSetting("mu_jfake", True, 1) # fix jfake BKG
    
if useStat:
    fitconfig.statErrThreshold = 0.05 #low stat error now (as in 2L-paper13)
else:
    fitconfig.statErrThreshold = None

meas.addPOI("mu_SIG")
meas.addParamSetting("Lumi", True)

constraint_channels = []
validation_channels = []
signal_channels = []

# -----------------
#  Control regions 
# -----------------
CRW = fitconfig.addChannel(variable, ["CRW"], *binning)
CRT = fitconfig.addChannel(variable, ["CRT"], *binning)
CRQ = fitconfig.addChannel(variable, ['CRQ'], *binning)

constraint_channels.append(CRQ)
constraint_channels.append(CRW)
constraint_channels.append(CRT)

wgamma_sample.setNormRegions(["CRW", variable])
ttbarg_sample.setNormRegions(["CRT",variable])
photonjet_sample.setNormRegions(["CRQ",variable])


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

# ---------------
# Signal region 
# ---------------
sr_name = signal_region[:-1] # could be SR or SRincl

SR = fitconfig.addChannel(variable, [sr_name], *binning)
signal_channels.append(SR)



# Add CR/VR/SR 
#if myFitType == FitType.Background or myFitType == FitType.Exclusion:
fitconfig.setBkgConstrainChannels(constraint_channels)

if myFitType == FitType.Background: 
    validation_channels.append(SR) #--- Define SR as validation region.

elif myFitType == FitType.Discovery:
    fitconfig.setSignalChannels(signal_channels) #--- Define SR as signal region.

if do_validation:
    fitconfig.setValidationChannels(validation_channels)


if myFitType == FitType.Exclusion:
    #print 'SR defined as signal region and GGM_X_Y as signal sample'
    #fitconfig.setSignalSample(sigSample)
    #fitconfig.setSignalChannels(signalChannels) #--- Define SR as signal region.             

    points = []
    
    try:
        sigSamples
    except NameError:
        sigSamples = None

    #if sigSamples is None:
    #points = dict(pointdict) ##.copy()
    # else:
    for sid in sigSamples:
        m3, mu = sid.split('_')
        points.append((int(m3), int(mu)))
    
    for (m3, mu) in points:
        print "Adding fit config for sample (%d, %d)" % (m3, mu)
        exclfit = configMgr.addFitConfigClone(fitconfig, "GGM_M3_mu_%d_%d" % (m3, mu))

        sigSample = Sample("GGM_M3_mu_%d_%d" % (m3, mu), ROOT.kOrange+3)
        sigSample.setNormByTheory()
        sigSample.setStatConfig(useStat)
        sigSample.setNormFactor("mu_SIG", muSigInitValue[0], muSigInitValue[1], muSigInitValue[2])

        if do_signal_theory_unc:
            configMgr.fixSigXSec = True
            sigSample.addSystematic(sigXsec) #--- Special uncertainty. Theory variations (creates extra files)

        exclfit.addSamples(sigSample)
        exclfit.setSignalSample(sigSample)
        exclfit.setSignalChannels(signal_channels)

