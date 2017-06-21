PhotonMetAnalysis
=================

## Requirements

ROOT, HistFitter, rootutils


## Install HistFitter

    # svn co svn+ssh://svn.cern.ch/reps/atlasphys-susy/Physics/SUSY/Analyses/HistFitter/tags/HistFitter-00-00-53 HistFitter
    git clone https://gitlab.cern.ch/HistFitter/HistFitter.git

    cd HistFitter
    git checkout tags/v0.54.0 -b v54

    patch -p0 -i ../HistFitter_fix_fit_strategy.diff

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





