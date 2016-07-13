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

from style import colors_dict

def color(sample):
    return ROOT.TColor.GetColor(colors_dict[sample])

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

userArg = [ i.replace('"', '') for i in configMgr.userArg.split()]
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
do_signal_theory_unc = False
variable = 'cuts'
binning  = (1, 0.5, 1.5) ##get_binning(variable)

region_str = "%s_%s" % (base_analysis, signal_region)

configMgr.writeXML = False  #for debugging

#--- Flags to control which fit is executed
useStat = True
configMgr.blindSR = False #True
configMgr.blindCR = False
configMgr.blindVR = False
configMgr.useSignalInBlindedData = False

#--- Parameters for hypothesis test
configMgr.doExclusion = False

configMgr.calculatorType = 2 if args.asimov else 0 # 0: toys, 2: asimov?
configMgr.testStatType = 3
configMgr.nPoints = args.npoints
configMgr.nTOYs = args.ntoys

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
    'VRM2incl', 'VRL2incl', 'VRL3incl',
  ]

for r in regions:
    configMgr.cutsDict[r] = '' # not used anyway


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

ttbar_sample.setNormByTheory()
ttbarg_sample.setNormFactor("mu_t", 1., 0., 2.)   

# W/Z gamma
wgamma_sample     = Sample('wgamma', color("wgamma"))
zllgamma_sample   = Sample('zllgamma', color("zllgamma"))
znunugamma_sample = Sample('znunugamma', color("znunugamma"))
#zllgamma_sample   = Sample('zgamma', color("zgamma"))
#VqqgammaSample   = Sample("vqqgamma", colors_dict["vqqgamma"])

zllgamma_sample.setNormByTheory()
znunugamma_sample.setNormByTheory()
wgamma_sample.setNormFactor("mu_w", 1., 0., 2.)

# QCD
photonjet_sample = Sample('photonjet', color("photonjet"))
multijet_sample = Sample('multijet', color("multijet"))

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
    Systematic('JET_EtaIntercalibration_NonClosure', nom_name, '_JET_EtaIntercalibration_NonClosureUp', '_JET_EtaIntercalibration_NonClosureDown', 'tree', 'overallSys'),
    Systematic('JET_GroupedNP_1', nom_name, '_JET_GroupedNP_1Up', '_JET_GroupedNP_1Down', 'tree', 'overallSys'),
    Systematic('JET_GroupedNP_2', nom_name, '_JET_GroupedNP_2Up', '_JET_GroupedNP_2Down', 'tree', 'overallSys'),
    Systematic('JET_GroupedNP_3', nom_name, '_JET_GroupedNP_3Up', '_JET_GroupedNP_3Down', 'tree', 'overallSys'),
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
]

syst_muon = [
    Sys("MUONS_SCALE"),
    Sys("MUONS_MS"),
    Sys("MUONS_ID"),
]

# Fake photon backgrounds
syst_feg = Systematic('Feg', nom_name, '_FegUp', '_FegDown', 'tree', 'histoSys')
syst_fjg = Systematic('Fjg', nom_name, '_FjgUp', '_FjgDown', 'tree', 'histoSys')

syst_weight = [
    Sys('EL_EFF_ID_TOTAL_1NPCOR_PLUS_UNCOR'),
    Sys('EL_EFF_Iso_TOTAL_1NPCOR_PLUS_UNCOR'),
    Sys('EL_EFF_Reco_TOTAL_1NPCOR_PLUS_UNCOR'),
    Sys('EL_EFF_Trigger_TOTAL_1NPCOR_PLUS_UNCOR'),


    # Sys('EL_EFF_Trigger_TOTAL_UncorrUncertainty'),
    Sys('FT_EFF_B_systematics'),
    Sys('FT_EFF_C_systematics'),
    Sys('FT_EFF_Light_systematics'),
    # Sys('FT_EFF_extrapolation'),
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
theoSysGJ    = Sys('theoSysGJ') 
theoSysTopG  = Sys('theoSysTopG')
theoSysWG    = Sys('theoSysWG')
theoSysZG    = Sys('theoSysZG') 
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
    ttbarg_sample.addSystematic(theoSysTopG)
    wgamma_sample.addSystematic(theoSysWG)
    zllgamma_sample.addSystematic(theoSysZG)
    znunugamma_sample.addSystematic(theoSysZG)
    photonjet_sample.addSystematic(theoSysGJ)

    efake_sample.addSystematic(syst_feg)
    jfake_sample.addSystematic(syst_fjg)
    
    #-- global systematics
    for gsyst in syst_to_all:
        # fitconfig.addSystematic(gsyst)

        for sample in bkg_samples:
            if sample.name.startswith('efake') or sample.name.startswith('jfake'):
                continue

            #print "*** Adding %s in %s" % (gsyst.name, sample.name) 
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
measLumiError = 0.021

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

    # inclusive VR
    # VRM2incl = fitconfig.addChannel(variable, ["VRM2incl"], *binning)
    # VRL2incl = fitconfig.addChannel(variable, ["VRL2incl"], *binning)
    # VRL3incl = fitconfig.addChannel(variable, ["VRL3incl"], *binning)

    # validation_channels.append(VRM2incl)
    # validation_channels.append(VRL2incl)
    # validation_channels.append(VRL3incl)

   
# ---------------
# Signal region 
# ---------------
sr_name = signal_region[:-1] # could be SR or SRincl

SR = fitconfig.addChannel(variable, [sr_name], *binning)
# if myFitType == FitType.Discovery:
#     SR.addDiscoverySamples([sr_name,], [1.,], [0.,], [100.,], [ROOT.kMagenta,])

signal_channels.append(SR)



# Add CR/VR/SR 
fitconfig.setBkgConstrainChannels(constraint_channels)

if myFitType == FitType.Background: 
    validation_channels.append(SR) #--- Define SR as validation region.

    # For now as a validation region. FIX!
    if sr_name == 'SR': 
        SRincl  = fitconfig.addChannel(variable, ["SRincl"], *binning)
        validation_channels.append(SRincl)

else:
    #for sr in signal_channels:
        #print sr
        #print sr.name
        #sr.addDiscoverySamples([sr.name],[1.],[0.],[100.],[ROOT.kMagenta])
        #meas.addPOI("mu_%s" % sr.name)

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
        sigSample.setNormFactor("mu_SIG", muSigInitValue[0], muSigInitValue[1], muSigInitValue[2])

        if do_signal_theory_unc:
            configMgr.fixSigXSec = True
            sigSample.addSystematic(sigXsec) #--- Special uncertainty. Theory variations (creates extra files)

        exclfit.addSamples(sigSample)
        exclfit.setSignalSample(sigSample)
        exclfit.setSignalChannels(signal_channels)

