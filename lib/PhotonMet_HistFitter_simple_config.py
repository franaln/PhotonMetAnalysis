from configManager import configMgr
from configWriter import fitConfig, Measurement, Channel, Sample
from systematic import Systematic
from math import sqrt

import os

# Setup for ATLAS plotting
from ROOT import gROOT
import ROOT

##########################
# Options
parser = argparse.ArgumentParser('PhotonMet_HistFitter_simple_config')

parser.add_argument("--m3", type=int, default=0)
parser.add_argument("--mu", type=int, default=0)

parser.add_argument("--nobs", type=float, default=0.)
parser.add_argument("--nsig", type=float)
parser.add_argument("--nbkg", type=float)
parser.add_argument("--sigb", type=float)

parser.add_argument("--ntoys", type=int, default=5000)

userArg = [ i.replace('"', '') for i in configMgr.userArg.split() ]
args = parser.parse_args(userArg)
print "Parsed user args %s" % str(args)


# Set observed and expected number of events in counting experiment
ndata     =  args.nobs 	# Number of events observed in data
nbkg      =  args.nbkg	# Number of predicted bkg events
nsig      =  args.nsig  # Number of predicted signal events
nbkgErr   =  sqrt(nbkg)	# (Absolute) Statistical error on bkg estimate *from limited MC statistics*
nsigErr   =  sqrt(nsig)	# (Absolute) Statistical error on signal estimate *from limited MC statistics*
lumiError = 0.032 	# Relative luminosity uncertainty

# Set uncorrelated systematics for bkg and signal (1 +- relative uncertainties)
ucb = Systematic("uncorrl_bkg", None, 1+args.sigb, 1-args.sigb, "user", "userOverallSys")  # 30% error up and down

##########################

# Setting the parameters of the hypothesis test
if args.m3 != 0 and args.mu != 0:
    configMgr.doExclusion = True # True=exclusion, False=discovery
else:
    configMgr.doExclusion = False # True=exclusion, False=discovery

configMgr.nTOYs = args.ntoys
configMgr.calculatorType = 0 # 2=asymptotic calculator, 0=frequentist calculator
configMgr.testStatType = 3   # 3=one-sided profile likelihood test statistic (LHC default)
configMgr.nPoints = 1       # number of values scanned of signal-strength for upper-limit determination of signal strength.
configMgr.writeXML = True

##########################

# Give the analysis a name
configMgr.analysisName = "PhotonMetAnalysis_Simple"
configMgr.outputFileName = "results/%s_Output.root" % configMgr.analysisName

# Define cuts
configMgr.cutsDict["SR"] = "1."

# Define weights
configMgr.weights = "1."

# Define samples
bkgSample = Sample("Bkg", ROOT.kGreen-9)
bkgSample.setStatConfig(True)
bkgSample.buildHisto([nbkg], "SR", "cuts", 0.5)
bkgSample.addSystematic(ucb)

sigSample = Sample("GGM_GG_bhmix_%d_%d" % (args.m3, args.mu), ROOT.kOrange+3)
sigSample.setNormFactor("mu_SIG", 1., 0., 10.)
#sigSample.setStatConfig(True)
sigSample.setNormByTheory()
sigSample.buildHisto([nsig], "SR", "cuts", 0.5)

dataSample = Sample("Data", ROOT.kBlack)
dataSample.setData()
dataSample.buildHisto([ndata], "SR", "cuts", 0.5)

# Define top-level
ana = configMgr.addFitConfig("Disc")
ana.addSamples([bkgSample, sigSample, dataSample])
ana.setSignalSample(sigSample)

# Define measurement
meas = ana.addMeasurement(name="NormalMeasurement", lumi=1.0, lumiErr=lumiError)
meas.addPOI("mu_SIG")
meas.addParamSetting("Lumi", True)

# Add the channel
chan = ana.addChannel("cuts", ["SR"], 1, 0.5, 1.5)
ana.setSignalChannels([chan])

# These lines are needed for the user analysis to run
# Make sure file is re-made when executing HistFactory
if configMgr.executeHistFactory:
    if os.path.isfile("data/%s.root" % configMgr.analysisName):
        os.remove("data/%s.root" % configMgr.analysisName) 


