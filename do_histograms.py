# mini -> histograms

import os
import subprocess

from utils import run_cmds_and_wait

import analysis

version = '34'
daytag = '10jul'

mc_samples = analysis.backgrounds_mc
regions = analysis.sr_regions + analysis.cr_regions + analysis.vr_regions


# Results outpu dir
histograms_dir = '%s/histograms' % os.environ['SUSY_ANALYSIS']


# Create "cuts" histograms

## 1fb histograms for MC
histograms_1fb_srl_path = '%s/histograms_v%s_%s_srl_1fb.root' % (histograms_dir, version, daytag)
histograms_1fb_srh_path = '%s/histograms_v%s_%s_srh_1fb.root' % (histograms_dir, version, daytag)

cmd_srl = 'sphistograms.py -o %s -s %s -r %s -n L --version %s --dosyst' % (histograms_1fb_srl_path, ','.join(mc_samples), regions, version)
cmd_srh = 'sphistograms.py -o %s -s %s -r %s -n H --version %s --dosyst' % (histograms_1fb_srh_path, ','.join(mc_samples), regions, version)

run_cmds_and_wait(cmd_srl, cmd_srh)

cmd_srl = 'sphistograms.py -o %s -s signal -r %s -n L --version %s --dosyst' % (histograms_1fb_srl_path, regions, version)
cmd_srh = 'sphistograms.py -o %s -s signal -r %s -n H --version %s --dosyst' % (histograms_1fb_srh_path, regions, version)

run_cmds_and_wait(cmd_srl, cmd_srh)


## Scale 1fb histograms to 2015 and 2016 lumi
histograms_2015_srl_path = '%s/histograms_v%s_%s_srl_2015.root' % (histograms_dir, version, daytag)
histograms_2016_srl_path = '%s/histograms_v%s_%s_srl_2016.root' % (histograms_dir, version, daytag)

cmd_2015 = 'sphistograms.py -i %s -o %s --lumi data15' % (histograms_1fb_srl_path, histograms_2015_srl_path)
cmd_2016 = 'sphistograms.py -i %s -o %s --lumi data16' % (histograms_1fb_srl_path, histograms_2016_srl_path)
    
run_cmds_and_wait(cmd_2015, cmd_2016)

histograms_2015_srh_path = '%s/histograms_v%s_%s_srh_2015.root' % (histograms_dir, version, daytag)
histograms_2016_srh_path = '%s/histograms_v%s_%s_srh_2016.root' % (histograms_dir, version, daytag)

cmd_2015 = 'sphistograms.py -i %s -o %s --lumi data15' % (histograms_1fb_srh_path, histograms_2015_srh_path)
cmd_2016 = 'sphistograms.py -i %s -o %s --lumi data16' % (histograms_1fb_srh_path, histograms_2016_srh_path)
    
run_cmds_and_wait(cmd_2015, cmd_2016)


## Add data and data-driven hisotgrams
cmd_srl_2015 = 'sphistograms.py -o %s -s data15,efake15,jfake15 --unblind -r %s -n L --dosyst' % (histograms_2015_srl_path, regions)
cmd_srl_2016 = 'sphistograms.py -o %s -s data16,efake16,jfake16 --unblind -r %s -n L --dosyst' % (histograms_2016_srl_path, regions)

run_cmds_and_wait(cmd_srl_2015, cmd_srl_2016)

cmd_srh_2015 = 'sphistograms.py -o %s -s data15,efake15,jfake15 --unblind -r %s -n H --dosyst' % (histograms_2015_srh_path, regions)
cmd_srh_2016 = 'sphistograms.py -o %s -s data16,efake16,jfake16 --unblind -r %s -n H --dosyst' % (histograms_2016_srh_path, regions)

run_cmds_and_wait(cmd_srh_2015, cmd_srh_2016)


## Sum 2015+2016 histograms
histograms_all_srl_path = '%s/histograms_v%s_%s_srl_all.root' % (histograms_dir, version, daytag)
histograms_all_srh_path = '%s/histograms_v%s_%s_srh_all.root' % (histograms_dir, version, daytag)

cmd_srl = 'sphistograms.py --sum %s,%s -o %s' % (histograms_2015_srl_path, histograms_2016_srl_path, histograms_all_srl_path)
cmd_srh = 'sphistograms.py --sum %s,%s -o %s' % (histograms_2015_srh_path, histograms_2016_srh_path, histograms_all_srh_path)

run_cmds_and_wait(cmd_srl, cmd_srh)














