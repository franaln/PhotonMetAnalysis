# analysis: mini -> histograms -> fit -> tables / plots / limits

import os
import sys
import argparse
import subprocess
import datetime

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)

import analysis
import regions
from yieldstable import yieldstable, merge_tables
from webpage import create_webpage

today = datetime.datetime.today()

parser = argparse.ArgumentParser(description='do_analysis.py')
parser.add_argument('--tag', default='', help='Output name tag')

parser.add_argument('-f', '--fit', action='store_true', help='Do fit')
parser.add_argument('-t', '--tables', action='store_true', help='Do tables')
parser.add_argument('-p', '--plots', action='store_true', help='Do plots')

parser.add_argument('--syst', action='store_true', help='Include experimental systematics')
parser.add_argument('--unblind', action='store_true', help='Unblind Signal Regions! Use with caution, you could find SUSY')

args = parser.parse_args()


daytag = today.strftime('%Y%b%d')

tag = daytag + ('_'+args.tag if args.tag else '')

mc_samples = [
    'photonjet',
    'wgamma',
    'zllgamma', 
    'znunugamma',
    'ttbarg',
    'diphoton',
    'vgammagamma',
    ]


# Config
unblind = args.unblind
do_syst = args.syst

do_fit    = args.fit
do_tables = args.tables
do_plots  = args.plots

do_plot_sr = True
do_plot_cr = True
do_plot_vr = True

srs = ['SRiL', 'SRiH']
crs = ['CRQ', 'CRW', 'CRT']
vrs = [
    'VRM1L', 'VRM2L', 'VRM3L', 
    'VRM1H', 'VRM2H', 'VRM3H', 
    'VRL1', 'VRL2', 'VRL3', 'VRL4', 'VRZ',
    'VRLW1', 'VRLT1', 'VRLW3', 'VRLT3',
    ]

regions_str = '%s,%s,%s' % (','.join(srs), ','.join(crs), ','.join(vrs))

# Results outpu dir
susy_dir = os.environ['SUSY_ANALYSIS']

results_dir    = 'results/analysis_%s' % (tag)
log_dir        = '%s/log'        % results_dir
histograms_dir = '%s/histograms' % results_dir
fits_dir       = '%s/fits'       % results_dir
tables_dir     = '%s/tables'     % results_dir
plots_dir      = '%s/plots'      % results_dir
web_dir        = '%s/www'        % results_dir

os.system('mkdir -p %s' % results_dir)
os.system('mkdir -p %s' % log_dir)
os.system('mkdir -p %s' % histograms_dir)
os.system('mkdir -p %s' % fits_dir)
os.system('mkdir -p %s' % tables_dir)
os.system('mkdir -p %s' % plots_dir)
os.system('mkdir -p %s' % web_dir)


logfile = log_dir + '/analysis.txt'

def run_cmd(*cmds):

    if len(cmds) == 1:
        #cmd = '(set -o pipefail ; %s | tee %s)' % (cmds[0], logfile)
        subprocess.call(cmds[0], shell=True)

    else:
        processes = []
        for cmd in cmds:
            print cmd
            p = subprocess.Popen(cmd, shell=True, universal_newlines=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            processes.append(p)
            
        for p in processes:
            ret_code = p.wait()

        # counter = 0
        # for cmd, p in zip(cmds, processes):
        #     output = p.stdout.read()

        #     if counter == 0:
        #         logfile = logfile_srl
        #     else:
        #         logfile = logfile_srh

        #     with open(logfile, 'a') as f:
        #         f.write('\n## '+cmd+'\n\n')
        #         f.write(output)

        #     counter += 1

    return




#------------------
# Log configuration
#------------------
info_dict = {
    'date': today.strftime('%d %b %Y'),
    'version': ','.join(analysis.versions),
    'lumi': (analysis.lumi_data), 
    'syst': do_syst,
    }

with open(log_dir + '/info.txt', 'w+') as f:
    f.write("""
Date: {date}
Mini version: {version}
Lumi: {lumi:.2f}
Syst: {syst}
""".format(**info_dict))

with open(log_dir + '/selection.txt', 'w+') as f:
    for reg in srs+crs+vrs:
        f.write('%s: %s\n' % (reg, getattr(regions, reg)))




#------------------
# Create Histograms
#------------------
histograms_path = '%s/histograms.root' % (histograms_dir)

samples = ','.join(mc_samples) + ',data,efake,jfake' # signal

cmd = 'sphistograms.py -o %s -s %s -r %s --lumi data' % (histograms_path, samples, regions_str) 

if unblind:
    cmd += ' --unblind'

if do_syst:
    cmd += ' --syst'

if not os.path.isfile(histograms_path):
    run_cmd(cmd)


#--------------
# Bkg-only Fit
#--------------
configfile = susy_dir + '/lib/PhotonMet_HistFitter_config.py'

fit_dir = '%s/bkgonly' % fits_dir
ws = fit_dir + "/BkgOnlyFit_combined_BasicMeasurement_model_afterFit.root"

cmd = 'run_bkgonly.py -i %s -o %s --sr SRiL,SRiH -c %s --val --data data --log %s/bkgonly_fit.log' % (histograms_path, fit_dir, configfile, log_dir)

if do_syst:
    cmd += ' --syst'

if do_fit:
    run_cmd(cmd)



#-------
# Tables
#-------

backgrounds_str = 'photonjet,wgamma,[zllgamma,znunugamma],ttbarg,efake,jfake,[diphoton,vgammagamma]' 
        
# Yields tables
if do_tables:
    ## CR
    yieldstable(ws, backgrounds_str, 'CRQ,CRW,CRT', tables_dir+'/table_cr.tex', 'Control Regions', is_cr=True)

    ## VR
    yieldstable(ws, backgrounds_str, 'VRM1L,VRM2L,VRM3L,VRM1H,VRM2H,VRM3H', tables_dir+'/table_vrm.tex', 'VRM')

    yieldstable(ws, backgrounds_str, 'VRL1,VRL2,VRL3,VRL4,VRZ', tables_dir+'/table_vrl.tex', 'VRL/VRZ')
    yieldstable(ws, backgrounds_str, 'VRLW1,VRLT1,VRLW3,VRLT3', tables_dir+'/table_vrlwt.tex', 'VRLWT')

    ## SR
    yieldstable(ws, backgrounds_str, 'SRiL,SRiH', tables_dir+'/table_sr.tex', 'Signal Regions', unblind=unblind)


# Systematics tables
# cmd1 = 'SysTable.py -w ' + ws + ' -c SRiL,SRiH        -o %s/table_syst_sr.tex -%%' % tables_dir
# cmd2 = 'SysTable.py -w ' + ws + ' -c CRQ,CRW,CRT      -o %s/table_syst_cr.tex -%%'  % tables_dir
# cmd3 = 'SysTable.py -w ' + ws + ' -c SRiL,SRiH        -o %s/table_syst_sr_bkgs.tex -%% -s photonjet,ttbarg,wgamma' % tables_dir
            
# run_cmd(cmd1)
# run_cmd(cmd2)
# run_cmd(cmd3)

# # Merge tables
# # SR
# merge_tables(tables_dir+'/table_sr_srl.tex', tables_dir+'/table_sr_srh.tex', tables_dir+'/table_sr_srl_srh.tex')

# # # CR
# # merge_tables(tables_dir+'/table_cr_srl.tex', tables_dir+'/table_cr_srh.tex', tables_dir+'/table_cr_srl_srh.tex')

# # VR
# merge_tables(tables_dir+'/table_vrm_srl.tex', tables_dir+'/table_vrm_srh.tex', tables_dir+'/table_vrm_srl_srh.tex')
# # # merge_tables(tables_dir+'/table_vre_srl.tex', tables_dir+'/table_vre_srh.tex', tables_dir+'/table_vre_srl_srh.tex')
# # merge_tables(tables_dir+'/table_vrl_srl.tex', tables_dir+'/table_vrl_srh.tex', tables_dir+'/table_vrl_srl_srh.tex')



#-------
# Plots
#-------

variables = [
    'ph_pt[0]',
    'jet_n',
    'bjet_n',
    'jet_pt[0]',
    'jet_pt[1]',
    'met_et',
    'ht',
    'meff',
    'dphi_jetmet',
    'dphi_gammet',
    'dphi_gamjet',
    'rt4',
]

variables_str = ','.join(variables)

# Distributions plots
after_cmd = ' --ws %s' % ws

## SR
cmd = 'draw.py -r SRiL,SRiH -l data -o %s --signal --n1 --ext "pdf,png" --save %s/histograms_plots_sr.root' % (plots_dir, histograms_dir) + after_cmd

if not unblind:
    cmd += ' -v met_et,meff --blind'
else:
    cmd += ' -v %s --ratio none' % variables_str

if do_plot_sr:
    run_cmd(cmd)


## CR
cmd = 'draw.py -v %s -r CRQ,CRW,CRT -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_cr.root' % (variables_str, plots_dir, histograms_dir) + after_cmd

if do_plot_cr:
    run_cmd(cmd)

## VRM
cmd_vrml = 'draw.py -v %s -r VRM1L,VRM2L,VRM3L -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_vrml.root' % (variables_str, plots_dir, histograms_dir) + after_cmd
cmd_vrmh = 'draw.py -v %s -r VRM1H,VRM2H,VRM3H -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_vrmh.root' % (variables_str, plots_dir, histograms_dir) + after_cmd

if do_plot_vr:
    run_cmd(cmd_vrml, cmd_vrmh)

# VRL
cmd_vrl1 = 'draw.py -v %s -r VRL1,VRL2     -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_vrl1.root' % (variables_str, plots_dir, histograms_dir) + after_cmd
cmd_vrl2 = 'draw.py -v %s -r VRL3,VRL4,VRZ -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_vrl2.root' % (variables_str, plots_dir, histograms_dir) + after_cmd

if do_plot_vr:
    run_cmd(cmd_vrl1, cmd_vrl2)

# Region pulls
all_regions_str = 'CRQ,CRW,CRT,VRM1L,VRM2L,VRM3L,VRM1H,VRM2H,VRM3H,VRL1,VRL2,VRL3,VRL4,SRiL,SRiH'
cmd  = 'plot_region_pull.py --ws %s -r %s -o %s --ext "pdf,png"' % (ws, all_regions_str, plots_dir)  + (' --unblind' if unblind else '')

if do_plots:
    run_cmd(cmd)

# Signal contamination
if do_plots:
    run_cmd('draw_signal_contamination.py -r %s -o %s --ext "pdf,png"' % (all_regions_str, plots_dir))


#--------
# Webpage
#--------
create_webpage(results_dir, web_dir, info_dict, regions=['SRi',] + crs + vrs)

# # copy webpage
# wwwdir = '~/work/www/Susy/PhotonMetAnalysis/'

# # if not os.path.isdir(wwwdir+'analysis_%s' % tag):
# #     os.sytem('cp -r results/analysis_2016Oct03_test_vrm/www/ ~/work/www/Susy/PhotonMetAnalysis/analysis_2016Oct03_test_vrm


