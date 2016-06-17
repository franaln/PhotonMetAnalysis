PhotonMetAnalysis
=================

## Code

* lib/: python libraries used by scripts. Most of the "magic" is in "miniutils.py"
* scripts/: get_yields.py, get_cutflow.py, draw.py, sphistograms.py and HistFitter scripts
* macros/: some c++ macros (to run over mini ntuples faster...)


## Install HistFitter

    svn co svn+ssh://svn.cern.ch/reps/atlasphys-susy/Physics/SUSY/Analyses/HistFitter/tags/HistFitter-00-00-52 HistFitter

    cd HistFitter/src
    make 
    cd -

    mkdir -p run/data run/config run/results
    cp HistFitter/config/HistFactorySchema.dtd run/config

## Run HistFitter

* Run from "run" directory
* Use "PhotonMet_HistFitter_config.py" configfile
* There are some scripts to help you:

    run_bkgonly.py -i [histograms_file] -o [output_dir] ...
