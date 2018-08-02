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

* Install [rootutils](https://github.com/franaln/rootutils) (or copy rootutils.py to lib/) 
    ```
    https://raw.githubusercontent.com/franaln/rootutils/master/rootutils/rootutils.py
    ```

* Setup ROOT/HistFitter...
    ```
    source setup.sh
    ```


## Analysis framework

                             +-------------------+     Data
                             |    Mini ntuples   |     MC
                             +---------+---------+     Fakes
                                       |
                                       |
                    Regions, xs, ...   |
                 +-------------------------------------+
                 |                                     |
       +---------+-----------+                   +-----+------+
       | Events              |                   | Histograms |
       | (1-bin histograms)  |                   +-----+------+
       +---------+-----------+                         |
                 |                                     |
       +---------+-----------+                         |
       | Bkg-only fit        |                         |
       | (HistFitter)        |                         |
       +---------+-----------+                         |
                 |                                     |
                 |   Scale factors                     |
                 +-------------------------------------+
                 |                                     |
       +---------+-----------+                   +-----+-----------------------+
       | Tables with         |                   | Plots of relevant variables |
       | expected events     |                   | in CRs, VRs and SRs         |
       | in CRs, VRs, SRs    |                   +-----------------------------+
       +---------------------+
