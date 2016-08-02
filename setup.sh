#!/bin/bash
 
setupATLAS
localSetupROOT 6.04.14-x86_64-slc6-gcc49-opt

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

