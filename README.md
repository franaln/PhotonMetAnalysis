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



## Analysis framework

                           +-------------------+   [ Data
                           |    Mini ntuples   |---[ MC
                           +---------+---------+   [ Fakes
                                     |
                                     |
                regions, XS, ...     |
               +-------------------------------------+
               |                                     |
     +---------+-----------+                   +-----+---------------+
     | Events (1-bin       |                   | Variable histograms |
     | "cuts" histograms)  |                   +-----+---------------+
     +---------+-----------+                         |
               |                                     |
     +---------+-----------+                         |
     | Bkg-only fit        |                         |
     | (using HistFitter)  |                         |
     +---------+-----------+                         |
               |                                     |
               | CR->SR scale factors                |
               +-------------------------------------+
               |                                     |
     +---------+-------------+                   +-----+-----------------------+
     | Tables with expected  |                   | Plots of relevant variables |
     | events andsystematics |                   | in all regions              |
     | in all regions        |                   +-----------------------------+
     +-----------------------+
