PhotonMetAnalysis
=================

## Requirements

ROOT, HistFitter, rootutils


## Install HistFitter

    git clone https://gitlab.cern.ch/HistFitter/HistFitter.git

    cd HistFitter
    git checkout tags/v0.54.0 -b v54

    git apply ../HistFitter_patch.diff ## fix fit strategy and add random seed to compute p0

    cd src
    make 
    cd ../..

    mkdir -p run/data run/config run/results
    cp HistFitter/config/HistFactorySchema.dtd run/config


## Setup

* Install [rootutils](https://github.com/franaln/rootutils) (or copy rootutils.py to lib/) 
    ```
    https://raw.githubusercontent.com/franaln/rootutils/master/rootutils/rootutils.py
    ```

* Setup ROOT/HistFitter...
    ```
    source setup.sh
    ```





