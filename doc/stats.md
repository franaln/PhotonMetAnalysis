Bkg-only fit
============

                       -c   +------------------+   -f     +-----------+  -t
                     +----> | cuts histograms  +--------> | workspace +------> Tables
                     |      +------------------+   Fit    +-----+-----+
  +--------------+   |                                          |
  | mini ntuples +---+                                          | mu (CR -> SR)
  +--------------+   |                                          |
     |- Data         |      +------------------+                |        -p
     |- MC           +----> | plots histograms +----------------+------------> Plots
     |- Fakes          -d   +------------------+



- Create histograms

    analysis.py -v XXX -o OUTPUT_DIR --data 2017 -c -d

- Bkg-only fit

    analysis.py -v XXX -o OUTPUT_DIR --data 2017 -f

- Tables

    analysis.py -v XXX -o OUTPUT_DIR --data 2017 -t

- Plots

    analysis.py -v XXX -o OUTPUT_DIR --data 2017 -p


Discovery significance
======================

XXX


Model independent limit 
=======================

1. Run the jobs in batch

    ```
    run_ul_batch.py -i ${histograms} -c ${configfile} -o OUTPUT_DIR  --sr SRL --ntoys 5000 --queue 2nd -l 36.1 --npoints 15 --mumax 15
    ```

2. Get the table/plot for one or more HTR:

    ```
    plot_upper_limit.py -i ... -o ...
    ```

Exclusion limits (batch)
========================

## Single SR

1. Send jobs to batch:

    ```
    run_excl_batch.py -i histograms.root -o output_dir --sr SR --data data --ntoys 5000 --queue 8nh 
    ```

2. Merge batch output (different runs and different points)

    ```
    merge_hypotest.py output_dir input_dir1 input_dir2 ...
    ``` 

3. Create list and contours

    ```
    plot_exclusion.py --list --cont PATH
    ```

4. Create exclusion plot

* Using custom script

* Using the default plot

    ```
    plot_exclusion.py --plot PATH
    ```


## Combine SRs

    plot_exclusion.py --combine 


Model dependent UL
==================

1. Send jobs to batch

    ```
    run_excl_batch.py  -i histograms.root -o output_dir --sr SR --data data --ntoys 5000 --queue 8nh  --npoints 15 --ul
    ```
2. Merge jobs (we need to merge the Output_upperlimit.root files for all the signal points)

    ```
    hadd upper_limit_SR.root SR_GGM_XXX/Output_upperlimit.root SR_GGM_YYY/Output_upperlimit.root ...
    ```

2. Or create a json with the UL values for each point (better when the size of the files is big, e.g. usings toys)

    ```
    merge_ul.py upper_limit_SR.json SR_GGM_XXX SR_GGM_YYY ...
    ```


Discovery
=========