#!/bin/bash
 
setupATLAS
localSetupROOT 6.04.02-x86_64-slc6-gcc48-opt

export SUSY_ROOT=$PWD

export PATH=$SUSY_ROOT/scripts:$PATH
#export LD_LIBRARY_PATH=$SUSY_ROOT/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$SUSY_ROOT/lib:$PYTHONPATH
 
# setup rootcore
# source $SUSY_ROOT/lib/RootCore/scripts/setup.sh
# export ROOTCORE_NCPUS=4
 
# setup HistFitter
# export HISTFITTER=$SUSY_ROOT/lib/HistFitter
# export PATH=$HISTFITTER/bin:$HISTFITTER/scripts:${PATH}
# export LD_LIBRARY_PATH=$HISTFITTER/lib:${LD_LIBRARY_PATH}
# export PYTHONPATH=$HISTFITTER/python:$HISTFITTER/scripts:$HISTFITTER/macros:$HISTFITTER/lib:$PYTHONPATH

# setup pyAMI
# source /cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/pyAmi/current/setup.sh
# source /cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/user/pyAmiGridSetup.sh

