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

def color(sample):
    return ROOT.kBlack

def rmdir(dir_):
    try:
        print 'Removing dir %s' % dir_
        shutil.rmtree(dir_)
    except OSError:
        pass

# Options
base_analysis  = "PhotonMet"

# Options
parser = argparse.ArgumentParser('PhotonMet_HistFitter_config')

parser.add_argument('-i', dest='hist_file')
parser.add_argument('--sr', dest='signal_region')
parser.add_argument('--data', default='data')

parser.add_argument('--syst', action='store_true')
parser.add_argument('--detsyst', action='store_true')
parser.add_argument('--ddsyst', action='store_true')
parser.add_argument('--mcsyst', action='store_true')

parser.add_argument('--val', action='store_true')
parser.add_argument('--mc', action='store_true')
parser.add_argument('--rm', action='store_true')
parser.add_argument('--asimov', action='store_true')
parser.add_argument('--ntoys', type=int, default=5000)
parser.add_argument('--npoints', type=int, default=1)
parser.add_argument('--sigxs', action='store_true')
parser.add_argument('--lumi', type=float, default=1.0)

userArg = [ i.replace('"', '') for i in configMgr.userArg.split() ]
args = parser.parse_args(userArg)
print "Parsed user args %s" % str(args)

hist_file     = args.hist_file 
signal_region = args.signal_region
do_validation = args.val 
use_mc_bkgs   = args.mc 

do_detector_syst = args.detsyst or args.syst
do_dd_syst       = args.ddsyst or args.syst
do_mc_syst       = args.mcsyst or args.syst

data_name = args.data

nom_name  = 'Nom'
model_hypo_test = 'GGM'
do_signal_theory_unc = args.sigxs
variable = 'cuts'
binning  = (1, 0.5, 1.5) 

configMgr.writeXML = True  #for debugging

#--- Flags to control which fit is executed
useStat = True
configMgr.blindSR = False
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
# if not do_syst:
#     opttag += '_nosys'

if opttag:
    configMgr.analysisName = "%sAnalysis_%s%s_%s" % (base_analysis, fittag, opttag, signal_region)
else:
    configMgr.analysisName = "%sAnalysis_%s_%s" % (base_analysis, fittag, signal_region)

if myFitType == FitType.Background:
    configMgr.analysisName = configMgr.analysisName.replace('_'+signal_region, '')


configMgr.histCacheFile  = hist_file
configMgr.outputFileName = 'results/%s/Output.root' % configMgr.analysisName

if args.rm and configMgr.analysisName:
    rmdir('./results/%s' % configMgr.analysisName)
    rmdir('./config/%s' % configMgr.analysisName)
    rmdir('./data/%s' % configMgr.analysisName)


## Read the histograms already produced
inputFileNames = [configMgr.histCacheFile, ]
    
## Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi  = args.lumi # Luminosity of input TTree after weighting
configMgr.outputLumi = args.lumi # Luminosity required for output histograms
configMgr.setLumiUnits("fb-1")

## Regions
srs = signal_region.split(',')

regions = [
    'CRQ', 'CRW', 'CRT',
    
    'VRM1L', 'VRM2L', 'VRM3L', 
    'VRM1H', 'VRM2H', 'VRM3H', 
    
    'VRL1', 'VRL2', 'VRL3', 'VRL4', 'VRE',
    ]

regions += srs

for r in regions:
    configMgr.cutsDict[r] = '' # need by HF but not used anyway o.O


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
vqqgamma_sample   = Sample("vqqgamma", color('vqqgamma'))

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
# vgammagamma_sample = Sample('vgammagamma', color("vgammagamma"))

diphoton_sample.setNormByTheory()
# vgammagamma_sample.setNormByTheory()

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
# data_sample.setStatConfig(useStat)
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
vqqgamma_sample.setStatConfig(useStat)

efake_sample.setStatConfig(False)
jfake_sample.setStatConfig(False)

data_samples = [data_sample,]

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
        ]



# ------------
# Systematics
# ------------
configMgr.nomName = 'Nom'

def HistSys(name='', kind='overallSys'):
    #return Systematic(name, nom_name, '_'+name+'Up', '_'+name+'Down', 'tree', kind)
    return Systematic(name, nom_name, '_'+name+'High', '_'+name+'Low', 'tree', kind)

# Detector uncertainties
syst_to_all = [
    # egamma
    HistSys("EG_RESOLUTION_ALL"),
    HistSys("EG_SCALE_ALL"),

    Systematic('PH_Iso_DDonoff', nom_name, '_PH_Iso_DDonoffHigh', nom_name, 'tree', 'histoSysOneSide'),
    HistSys('PH_EFF_ID_Uncertainty'),

    # jets
    HistSys('JET_EtaIntercalibration_NonClosure'),
    HistSys('JET_JvtEfficiency'),
    HistSys('JET_GroupedNP_1'),
    HistSys('JET_GroupedNP_2'),
    HistSys('JET_GroupedNP_3'),
    Systematic('JET_JER_SINGLE_NP', nom_name, '_JET_JER_SINGLE_NPHigh', nom_name, 'tree','histoSysOneSide'),

    # met 
    Systematic('MET_SoftTrk_ResoPara', nom_name, '_MET_SoftTrk_ResoParaHigh', nom_name, 'tree', 'histoSysOneSide'),
    Systematic('MET_SoftTrk_ResoPerp', nom_name, '_MET_SoftTrk_ResoPerpHigh', nom_name, 'tree', 'histoSysOneSide'),
    Systematic('MET_SoftTrk_Scale',    nom_name, '_MET_SoftTrk_ScaleHigh', '_MET_SoftTrk_ScaleLow', 'tree', 'overallSys'),

    # pile-up
    HistSys('PRW_DATASF'),
]

# Flat 100% unc for photon+jet in SRs
sigma_gamjet_flat = 0.9999
syst_gamjet_flat_SR  = Systematic("flat100GJ", 1, 1+sigma_gamjet_flat, 1-sigma_gamjet_flat, "user", "userOverallSys")


# Fake photon backgrounds
## e->g
syst_feg      = HistSys('EFAKE_SYST')
syst_stat_feg = Systematic('EFAKE_STAT', nom_name, nom_name, nom_name, 'tree', 'shapeStat') ##, constraint='Poisson')
#syst_stat_feg = HistSys('EFAKE_STAT') 

## j->g
syst_fjg      = HistSys('JFAKE_SYST')
syst_stat_fjg = Systematic('JFAKE_STAT', nom_name, nom_name, nom_name, 'tree', 'shapeStat') ##, constraint='Poisson')
#syst_stat_fjg = HistSys('JFAKE_STAT')

# Theory Uncertainties
## Zgamma
sigma_zgamma_srl = 0.30 #0.0567
sigma_zgamma_srh = 0.30 #0.1154
sigma_zgamma_crq = 0.0620
sigma_zgamma_crw = 0.0714
sigma_zgamma_crt = 0.6891
sigma_zgamma_vrl = 0.1572

syst_zgamma_theo_srl = Systematic("theoSysZG", 1, 1+sigma_zgamma_srl, 1-sigma_zgamma_srl, "user", "userOverallSys")
syst_zgamma_theo_srh = Systematic("theoSysZG", 1, 1+sigma_zgamma_srh, 1-sigma_zgamma_srh, "user", "userOverallSys")
syst_zgamma_theo_crq = Systematic("theoSysZG", 1, 1+sigma_zgamma_crq, 1-sigma_zgamma_crq, "user", "userOverallSys")
syst_zgamma_theo_crw = Systematic("theoSysZG", 1, 1+sigma_zgamma_crw, 1-sigma_zgamma_crw, "user", "userOverallSys")
syst_zgamma_theo_crt = Systematic("theoSysZG", 1, 1+sigma_zgamma_crt, 1-sigma_zgamma_crt, "user", "userOverallSys")
syst_zgamma_theo_vrl = Systematic("theoSysZG", 1, 1+sigma_zgamma_vrl, 1-sigma_zgamma_vrl, "user", "userOverallSys")

## gamjet
sigma_gamjet_all = 0.29 

syst_gamjet_theo_all  = Systematic("theoSysGJ", 1, 1+sigma_gamjet_all, 1-sigma_gamjet_all, "user", "userOverallSys")


## wgamma
sigma_wgamma_srl   = 0.30 #0.0473
sigma_wgamma_srh   = 0.30 #0.1455
sigma_wgamma_crq   = 0.0855
sigma_wgamma_crw   = 0.0477
sigma_wgamma_crt   = 0.0486
sigma_wgamma_vrl   = 0.30 #0.09

syst_wgamma_theo_srl = Systematic("theoSysWG", 1, 1+sigma_wgamma_srl, 1-sigma_wgamma_srl, "user", "userOverallSys")
syst_wgamma_theo_srh = Systematic("theoSysWG", 1, 1+sigma_wgamma_srh, 1-sigma_wgamma_srh, "user", "userOverallSys")
syst_wgamma_theo_crq = Systematic("theoSysWG", 1, 1+sigma_wgamma_crq, 1-sigma_wgamma_crq, "user", "userOverallSys")
syst_wgamma_theo_crw = Systematic("theoSysWG", 1, 1+sigma_wgamma_crw, 1-sigma_wgamma_crw, "user", "userOverallSys")
syst_wgamma_theo_crt = Systematic("theoSysWG", 1, 1+sigma_wgamma_crt, 1-sigma_wgamma_crt, "user", "userOverallSys")
syst_wgamma_theo_vrl = Systematic("theoSysWG", 1, 1+sigma_wgamma_vrl, 1-sigma_wgamma_vrl, "user", "userOverallSys")

## ttgamma
sigma_tgamma_srl = 0.30 #0.2839
sigma_tgamma_srh = 0.30 #0.3305
sigma_tgamma_crq = 0.2134
sigma_tgamma_crw = 0.1317
sigma_tgamma_crt = 0.0987
sigma_tgamma_vrl = 0.30 #0.19

syst_tgamma_theo_srl = Systematic("theoSysTG", 1, 1+sigma_tgamma_srl, 1-sigma_tgamma_srl, "user", "userOverallSys")
syst_tgamma_theo_srh = Systematic("theoSysTG", 1, 1+sigma_tgamma_srh, 1-sigma_tgamma_srh, "user", "userOverallSys")
syst_tgamma_theo_crq = Systematic("theoSysTG", 1, 1+sigma_tgamma_crq, 1-sigma_tgamma_crq, "user", "userOverallSys")
syst_tgamma_theo_crw = Systematic("theoSysTG", 1, 1+sigma_tgamma_crw, 1-sigma_tgamma_crw, "user", "userOverallSys")
syst_tgamma_theo_crt = Systematic("theoSysTG", 1, 1+sigma_tgamma_crt, 1-sigma_tgamma_crt, "user", "userOverallSys")
syst_tgamma_theo_vrl = Systematic("theoSysTG", 1, 1+sigma_tgamma_vrl, 1-sigma_tgamma_vrl, "user", "userOverallSys")

## signal
sigXsec = HistSys('SigXSec')


# Add Sample Specific Systematics (apparently it's needed to add these systs to the samples *BEFORE* adding them to the FitConfig
if do_detector_syst:
    for gsyst in syst_to_all:

        for sample in bkg_samples:
            if sample.name.startswith('efake') or sample.name.startswith('jfake'):
                continue

            if sample.name == 'photonjet':
                continue

            sample.addSystematic(gsyst)


if do_dd_syst:
    efake_sample.addSystematic(syst_feg)
    jfake_sample.addSystematic(syst_fjg)

    efake_sample.addSystematic(syst_stat_feg)
    jfake_sample.addSystematic(syst_stat_fjg)

if do_mc_syst:
    photonjet_sample.addSystematic(syst_gamjet_theo_all)



#---------
#   Fit
#---------

# Background only fit
if myFitType == FitType.Background:
    fitconfig = configMgr.addFitConfig('BkgOnlyFit')

# Discovery fit
elif myFitType == FitType.Discovery:
    fitconfig = configMgr.addFitConfig('DiscoveryFit')

# Exclusion fit
elif myFitType == FitType.Exclusion:
    fitconfig = configMgr.addFitConfig('ExclusionFit')


fitconfig.addSamples(bkg_samples + data_samples)

# Stat uncertainties
fitconfig.statErrThreshold = 0.01
#fitconfig.statStatErrorType('Poisson')

# Measurement
measName = "BasicMeasurement"
measLumi = 1.0
#measLumiError = 0.029 # Preliminar for ICHEP: 2.9% (3.7% for 2016 and 2.1% for 2015)
#measLumiError = 0.041 # Preliminar Moriond: 4.1% (4.5% for 2016 and 2.1% for 2015)
measLumiError = 0.032 # Moriond: 3.2% (3.% for 2016 and 2.1% for 2015)

meas = fitconfig.addMeasurement(measName, measLumi, measLumiError)

meas.addPOI('mu_SIG')
meas.addParamSetting('Lumi', True)


constraint_channels = []
validation_channels = []
signal_channels     = []

# ---------------
# Signal regions 
# ---------------

# if not bkg-only only allow ONE SR.
if myFitType != FitType.Background and len(srs) > 1:
    raise Exception('For discovery/exclusion fit only one SR allowed')

# create SR channel and add them to signal_channels
for sr in srs:
    signal_channels.append(fitconfig.addChannel(variable, [sr], *binning))

# -----------------
#  Control regions 
# -----------------
CRQ = fitconfig.addChannel(variable, ['CRQ'], *binning)
CRW = fitconfig.addChannel(variable, ['CRW'], *binning)
CRT = fitconfig.addChannel(variable, ['CRT'], *binning)

constraint_channels.append(CRQ)
constraint_channels.append(CRW)
constraint_channels.append(CRT)

wgamma_sample   .setNormRegions(['CRW', variable])
ttbarg_sample   .setNormRegions(['CRT', variable])
photonjet_sample.setNormRegions(['CRQ', variable])

# -------------------
# Validation regions 
# -------------------
if do_validation:

    VRM1L  = fitconfig.addChannel(variable, ['VRM1L'], *binning)
    VRM2L  = fitconfig.addChannel(variable, ['VRM2L'], *binning)
    VRM3L  = fitconfig.addChannel(variable, ['VRM3L'], *binning)
    VRM1H  = fitconfig.addChannel(variable, ['VRM1H'], *binning)
    VRM2H  = fitconfig.addChannel(variable, ['VRM2H'], *binning)
    VRM3H  = fitconfig.addChannel(variable, ['VRM3H'], *binning)

    VRL1  = fitconfig.addChannel(variable, ['VRL1'], *binning)
    VRL2  = fitconfig.addChannel(variable, ['VRL2'], *binning)
    VRL3  = fitconfig.addChannel(variable, ['VRL3'], *binning)
    VRL4  = fitconfig.addChannel(variable, ['VRL4'], *binning)

    VRE  = fitconfig.addChannel(variable, ['VRE'], *binning)

    validation_channels.append(VRM1L)
    validation_channels.append(VRM2L)
    validation_channels.append(VRM3L)
    validation_channels.append(VRM1H)
    validation_channels.append(VRM2H)
    validation_channels.append(VRM3H)
    validation_channels.append(VRL1)
    validation_channels.append(VRL2)
    validation_channels.append(VRL3)
    validation_channels.append(VRL4)
    validation_channels.append(VRE)



# Add theoretical systematics region specific
if do_mc_syst:

    # SR
    for sc in signal_channels:
        if 'SRL' in sc.name:
            wg_syst  = syst_wgamma_theo_srl
            tg_syst  = syst_tgamma_theo_srl
            zg_syst  = syst_zgamma_theo_srl
        elif 'SRH' in sc.name:
            wg_syst  = syst_wgamma_theo_srh
            tg_syst  = syst_tgamma_theo_srh
            zg_syst  = syst_zgamma_theo_srh

        sc.getSample('wgamma')     .addSystematic(wg_syst)
        sc.getSample('ttbarg')     .addSystematic(tg_syst)
        sc.getSample('zllgamma')   .addSystematic(zg_syst)
        sc.getSample('znunugamma') .addSystematic(zg_syst)

        sc.getSample('photonjet').addSystematic(syst_gamjet_flat_SR)


    # CR
    CRQ.getSample('wgamma').addSystematic(syst_wgamma_theo_crq)
    CRW.getSample('wgamma').addSystematic(syst_wgamma_theo_crw)
    CRT.getSample('wgamma').addSystematic(syst_wgamma_theo_crt)

    CRQ.getSample('ttbarg').addSystematic(syst_tgamma_theo_crq)
    CRW.getSample('ttbarg').addSystematic(syst_tgamma_theo_crw)
    CRT.getSample('ttbarg').addSystematic(syst_tgamma_theo_crt)

    CRQ.getSample('zllgamma').addSystematic(syst_zgamma_theo_crq)
    CRW.getSample('zllgamma').addSystematic(syst_zgamma_theo_crw)
    CRT.getSample('zllgamma').addSystematic(syst_zgamma_theo_crt)

    CRQ.getSample('znunugamma').addSystematic(syst_zgamma_theo_crq)
    CRW.getSample('znunugamma').addSystematic(syst_zgamma_theo_crw)
    CRT.getSample('znunugamma').addSystematic(syst_zgamma_theo_crt)

    # VR
    for vr in validation_channels:

        if 'VRL' in vr.name:
            vr.getSample('wgamma')    .addSystematic(syst_wgamma_theo_vrl)
            vr.getSample('zllgamma')  .addSystematic(syst_zgamma_theo_vrl)
            vr.getSample('znunugamma').addSystematic(syst_zgamma_theo_vrl)
            vr.getSample('ttbarg')    .addSystematic(syst_tgamma_theo_vrl)

        elif vr.name.endswith('L'):
            vr.getSample('wgamma')     .addSystematic(syst_wgamma_theo_srl)
            vr.getSample('zllgamma')   .addSystematic(syst_zgamma_theo_srl)
            vr.getSample('znunugamma') .addSystematic(syst_zgamma_theo_srl)
            vr.getSample('ttbarg')     .addSystematic(syst_tgamma_theo_srl)
        elif vr.name.endswith('H'):        
            vr.getSample('wgamma')     .addSystematic(syst_wgamma_theo_srh)
            vr.getSample('zllgamma')   .addSystematic(syst_zgamma_theo_srh)
            vr.getSample('znunugamma') .addSystematic(syst_zgamma_theo_srh)
            vr.getSample('ttbarg')     .addSystematic(syst_tgamma_theo_srh)


# Add CR/VR/SR 
fitconfig.addBkgConstrainChannels(constraint_channels)

if myFitType == FitType.Background: 
    if do_validation:
        validation_channels += signal_channels #--- Define SR as validation region.
        fitconfig.addValidationChannels(validation_channels)
    else:
        fitconfig.addValidationChannels(signal_channels)

else:
    fitconfig.addSignalChannels(signal_channels) #--- Define SR as signal region.


if myFitType == FitType.Discovery:

    discovery_sample = Sample('Discovery', ROOT.kViolet+5)
    discovery_sample.setNormByTheory()
    discovery_sample.setNormFactor('mu_SIG', 1., 0., 10.)

    fitconfig.addSamples(discovery_sample)
    fitconfig.setSignalSample(discovery_sample)


if myFitType == FitType.Exclusion:

    points = []
    
    try:
        sigSamples
    except NameError:
        sigSamples = None
    
    for sig in sigSamples:
        print "Adding fit config for sample %s" % sig
        exclfit = configMgr.addFitConfigClone(fitconfig, sig)

        sig_sample = Sample(sig, ROOT.kOrange+3) 
        sig_sample.setNormByTheory()
        sig_sample.setStatConfig(useStat)
        sig_sample.setNormFactor("mu_SIG", 1., 0., 5.)

        if do_signal_theory_unc:
            configMgr.fixSigXSec = True
            sig_sample.addSystematic(sigXsec) #--- Special uncertainty. Theory variations (creates extra files)

        exclfit.addSamples(sig_sample)
        exclfit.setSignalSample(sig_sample)
        exclfit.setSignalChannels(signal_channels)

