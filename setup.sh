#!/bin/bash
 
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
alias setupATLAS='source $ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh'

setupATLAS
localSetupROOT 6.12.06-x86_64-slc6-gcc62-opt

export SUSY_ANALYSIS=$PWD

export PATH=$SUSY_ANALYSIS/scripts:$PATH
export PYTHONPATH=$SUSY_ANALYSIS/lib:$SUSY_ANALYSIS/config:$PYTHONPATH
 
# setup HistFitter
if [ -d "$SUSY_ANALYSIS/HistFitter" ] ; then
    cd $SUSY_ANALYSIS/HistFitter
    . setup_afs.sh
    cd -
else
    echo Download and compile HistFitter!!!
fi

cd $SUSY_ANALYSIS