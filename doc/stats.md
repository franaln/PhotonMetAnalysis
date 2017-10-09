Discovery significance
======================


Model independent limit 
=======================

1. Run the jobs in batch

    ```
    run_ul_batch.py -i ${histograms} -c ${configfile} -o OUTPUT_DIR  --sr SRL --ntoys 5000 --queue 2nd -l 36.1 --npoints 15 --mumax 15
    ```

# 2. Merge different jobs

#     ```
#     merge_indp_ul.py output_merged.root UpperLimitTable_nToys5000.texhtiResult_poi_mu_SIG_ntoys_5000_calctype_0_nPoints_15.root ...
#     ``` 


2. Get the table/plot for one or more HTR:

    ```
    plot_upper_limit.py -i ... -o ...
    ```

Exclusion limits (batch)
========================

## Single SR

1. Send jobs to batch:

    ```
    run_limit_batch.py -i histograms.root -o output_dir --sr SR --data data --ntoys 5000 --queue 8nh 
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

    * Using deafult plot

    ```
    plot_exclusion.py --plot PATH
    ```


## Combine SRs

    ``` 
    plot_exclusion.py --combine 
    ```

