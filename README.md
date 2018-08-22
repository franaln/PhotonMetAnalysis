PhotonMetAnalysis
=================

## Requirements

ROOT, HistFitter, rootutils


## Install HistFitter

    source setup.sh

    git clone https://gitlab.cern.ch/HistFitter/HistFitter.git (o ssh://git@gitlab.cern.ch:7999/HistFitter/HistFitter.git)

    cd HistFitter
    git checkout tags/v0.62.0 -b v62

    git apply ../HistFitter_patch.diff ## fix fit strategy and add random seed to compute p0

    cd src
    make 
    cd ../..

    mkdir -p run/data run/config run/results
    cp HistFitter/config/HistFactorySchema.dtd run/config


## Setup

    source setup.sh


## Update cross-section database (data/CrossSectionData.txt) from here:

    http://atlas.web.cern.ch/Atlas/GROUPS/DATABASE/GroupData/dev/PMGTools/PMGxsecDB_mc16.txt

