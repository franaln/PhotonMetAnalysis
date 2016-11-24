PhotonMetAnalysis
=================

## Code

* lib:     python libraries used by scripts and to configure analysis
* scripts: get_yields.py, get_cutflow.py, draw.py, sphistograms.py and HistFitter scripts


## Install HistFitter

    svn co svn+ssh://svn.cern.ch/reps/atlasphys-susy/Physics/SUSY/Analyses/HistFitter/tags/HistFitter-00-00-53 HistFitter

    cd HistFitter
    patch -p0 -i ../HistFitter_fix_fit_strategy.diff

    cd src
    make 
    cd ../..

    mkdir -p run/data run/config run/results
    cp HistFitter/config/HistFactorySchema.dtd run/config

## Run Analysis

* Install rootutils 

* Setup ROOT/HistFitter...
    ```
    source setup.sh
    ```



