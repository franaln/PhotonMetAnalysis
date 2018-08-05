#! /usr/bin/env python2.7
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
from systable import systable

from webpage import create_webpage

today = datetime.datetime.today()

parser = argparse.ArgumentParser(description='do_analysis.py')
parser.add_argument('--tag', default='', help='Output name tag')
parser.add_argument('-i', '--input_hist', help='Input histograms')
parser.add_argument('-c', '--conf', help='HF config file')

parser.add_argument('--hist', action='store_true', help='Force histogram creation')
parser.add_argument('-f', '--fit', action='store_true', help='Do fit')
parser.add_argument('-t', '--tables', action='store_true', help='Do tables')
parser.add_argument('-p', '--plots', action='store_true', help='Do plots')
parser.add_argument('--allplots', action='store_true', help='Do all plots')
parser.add_argument('--val', action='store_true', help='Include Validation Regions')

parser.add_argument('--syst', action='store_true', help='Include all systematics')
parser.add_argument('--detsyst', action='store_true', help='Include detector systematics')
parser.add_argument('--ddsyst', action='store_true', help='Include DD systematics')
parser.add_argument('--mcsyst', action='store_true', help='Include MC systematics')

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
    ]


# Config
unblind = args.unblind

if args.syst:
    syst_str = ' --syst'
else:
    syst_str = ''
    if args.detsyst:
        syst_str += ' --detsyst'
    if args.ddsyst:
        syst_str += ' --ddsyst'
    if args.mcsyst:
        syst_str += ' --mcsyst'


do_fit    = args.fit
do_tables = args.tables
do_plots  = args.plots

if not do_fit and not do_tables and not do_plots:
    parser.print_usage()
    sys.exit(1)

srs = ['SRL200', 'SRL300', 'SRH']
crs = ['CRQ', 'CRW', 'CRT']
vrs = [
    'VRM1L', 'VRM2L', 'VRM3L', 
    'VRM1H', 'VRM2H', 'VRM3H', 
    'VRL1', 'VRL2', 'VRL3', 'VRL4', 
    'VRLW1', 'VRLT1', 'VRLW3', 'VRLT3',

    'VRE'
    ]

sr_str = ','.join(srs)
if args.val:
    regions_str = '%s,%s,%s' % (','.join(srs), ','.join(crs), ','.join(vrs))
else:
    regions_str = '%s,%s' % (','.join(srs), ','.join(crs))


# Results outpu dir
susy_dir = os.environ['SUSY_ANALYSIS']

results_dir    = '%s/results/analysis_%s' % (susy_dir, tag)
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
logfile_cmd = log_dir + '/commands.txt'

def run_cmd(*cmds):

    with open(logfile_cmd, 'a') as f:
        for cmd in cmds:
            f.write('%s\n' % cmd)

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
    'syst': syst_str,
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
if args.input_hist is not None:
    histograms_path = args.input_hist

else:
    histograms_txt_path = '%s/histograms.txt' % (histograms_dir)
    histograms_path = '%s/histograms.root' % (histograms_dir)

    samples = ','.join(mc_samples) + ',data,efake,jfake' # signal

    cmd = 'sphistograms.py -o %s -s %s -r %s --lumi data' % (histograms_txt_path, samples, regions_str) 
    cmd2 = 'txt2hist.py %s %s' % (histograms_txt_path, histograms_path)

    if unblind:
        cmd += ' --unblind'

    if syst_str:
        cmd += syst_str

    if not os.path.isfile(histograms_path) or args.hist:
        run_cmd(cmd)
        run_cmd(cmd2)



#--------------
# Bkg-only Fit
#--------------
if args.conf is not None:
    configfile = os.path.abspath(args.conf)
else:
    configfile = susy_dir + '/lib/PhotonMet_HistFitter_config.py'

fit_dir = '%s/bkgonly' % fits_dir
ws = fit_dir + "/BkgOnlyFit_combined_BasicMeasurement_model_afterFit.root"

cmd = 'run_bkgonly.py -i %s -o %s --sr %s -c %s --data data --log %s/bkgonly_fit.log' % (histograms_path, fit_dir, sr_str, configfile, log_dir)

if syst_str:
    cmd += ' --syst "%s"' % syst_str
if args.val:
    cmd += ' --val'

cmd += ' --hf "-D corrMatrix -m ALL"' 

if do_fit:
    run_cmd(cmd)



#-------
# Tables
#-------
backgrounds_str = 'photonjet,wgamma,[zllgamma,znunugamma],ttbarg,efake,jfake,diphoton'

if args.val:
    all_regions_str = 'CRQ,CRW,CRT,VRM1L,VRM2L,VRM3L,VRM1H,VRM2H,VRM3H,VRL1,VRL2,VRL3,VRL4,VRE,' + sr_str
else:
    all_regions_str = 'CRQ,CRW,CRT,' + sr_str

# Yields tables
if do_tables:
    ## CR
    yieldstable(ws, backgrounds_str, 'CRQ,CRW,CRT', tables_dir+'/table_cr.tex', 'Control Regions', is_cr=True)

    ## VR
    if args.val:
        yieldstable(ws, backgrounds_str, 'VRM1L,VRM2L,VRM3L,VRM1H,VRM2H,VRM3H', tables_dir+'/table_vrm.tex', 'VRM')

        yieldstable(ws, backgrounds_str, 'VRL1,VRL2,VRL3,VRL4', tables_dir+'/table_vrl.tex', 'VRL')
        # yieldstable(ws, backgrounds_str, 'VRLW1,VRLT1,VRLW3,VRLT3', tables_dir+'/table_vrlwt.tex', 'VRLWT')
        
        yieldstable(ws, backgrounds_str, 'VRE', tables_dir+'/table_vre.tex', 'Fakes VR')

    ## SR
    yieldstable(ws, backgrounds_str, sr_str, tables_dir+'/table_sr.tex', 'Signal Regions', unblind=unblind)

    ## All (for pull plot)
    if args.val:
        yieldstable(ws, backgrounds_str.replace('[', '').replace(']', ''), all_regions_str, tables_dir+'/table_all.tex', 'All Regions', unblind=unblind)


# Pull plot
if do_tables and args.val:
    cmd  = 'plot_region_pull.py --pickle %s -r %s -o %s --ext "pdf,png"' % (tables_dir+'/table_all.pickle', all_regions_str, plots_dir)  + (' --unblind' if unblind else '')
    run_cmd(cmd)


# Systematics tables
if do_tables and syst_str:

    systable(ws, '', 'SRL200', '%s/table_syst_srl200.tex' % tables_dir)
    systable(ws, '', 'SRL300', '%s/table_syst_srl300.tex' % tables_dir)
    systable(ws, '', 'SRH',    '%s/table_syst_srh.tex' % tables_dir)

    systable(ws, '', 'CRQ', '%s/table_syst_crq.tex' % tables_dir)
    systable(ws, '', 'CRW', '%s/table_syst_crw.tex' % tables_dir)
    systable(ws, '', 'CRT', '%s/table_syst_crt.tex' % tables_dir)

    systable(ws, 'photonjet',             'SRL200,SRL300,SRH', '%s/table_syst_phohonjet.tex' % tables_dir)
    systable(ws, 'wgamma',                'SRL200,SRL300,SRH', '%s/table_syst_wgamma.tex' % tables_dir)
    systable(ws, 'zllgamma',              'SRL200,SRL300,SRH', '%s/table_syst_zllgamma.tex' % tables_dir)
    systable(ws, 'znunugamma',            'SRL200,SRL300,SRH', '%s/table_syst_znunugamma.tex' % tables_dir)
    systable(ws, 'ttbarg',                'SRL200,SRL300,SRH', '%s/table_syst_ttbarg.tex' % tables_dir)
    systable(ws, 'efake',                 'SRL200,SRL300,SRH', '%s/table_syst_efake.tex' % tables_dir)
    systable(ws, 'jfake',                 'SRL200,SRL300,SRH', '%s/table_syst_jfake.tex' % tables_dir)
    systable(ws, 'diphoton',              'SRL200,SRL300,SRH', '%s/table_syst_diphoton.tex' % tables_dir)

    if args.val:
        systable(ws, '', 'VRL1', '%s/table_syst_vrl1.tex' % tables_dir)
        systable(ws, '', 'VRL2', '%s/table_syst_vrl2.tex' % tables_dir)
        systable(ws, '', 'VRL3', '%s/table_syst_vrl3.tex' % tables_dir)
        systable(ws, '', 'VRL4', '%s/table_syst_vrl4.tex' % tables_dir)
        systable(ws, '', 'VRM1L', '%s/table_syst_vrm1l.tex' % tables_dir)
        systable(ws, '', 'VRM1H', '%s/table_syst_vrm1h.tex' % tables_dir)
        systable(ws, '', 'VRM2L', '%s/table_syst_vrm2l.tex' % tables_dir)
        systable(ws, '', 'VRM2H', '%s/table_syst_vrm2h.tex' % tables_dir)
        systable(ws, '', 'VRM3L', '%s/table_syst_vrm3l.tex' % tables_dir)
        systable(ws, '', 'VRM3H', '%s/table_syst_vrm3h.tex' % tables_dir)



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
# if do_plots:

#     cmd = 'draw.py -r SRL,SReL2,SReH -l data --data data -o %s --signal --n1 --ext "pdf,png" --save %s/histograms_plots_sr.root' % (plots_dir, histograms_dir) + after_cmd

#     if not unblind:
#         cmd += ' -v met_et,meff --blind'
#     else:
#         cmd += ' -v %s --ratio none' % variables_str
        
#     run_cmd(cmd)


## CR
if do_plots:
    cmd = 'draw.py -v %s -r CRQ,CRW,CRT -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_cr.root' % (variables_str, plots_dir, histograms_dir) + after_cmd

    run_cmd(cmd)

## VRM
if do_plots:
    if args.allplots:
        cmd_vrml = 'draw.py -v %s -r VRM1L,VRM2L,VRM3L -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_vrml.root' % (variables_str, plots_dir, histograms_dir) + after_cmd
        cmd_vrmh = 'draw.py -v %s -r VRM1H,VRM2H,VRM3H -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_vrmh.root' % (variables_str, plots_dir, histograms_dir) + after_cmd
    else:
        cmd_vrml = 'draw.py -v %s -r VRM1L -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_vrml.root' % (variables_str, plots_dir, histograms_dir) + after_cmd
        cmd_vrmh = 'draw.py -v %s -r VRM1H -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_vrmh.root' % (variables_str, plots_dir, histograms_dir) + after_cmd

    run_cmd(cmd_vrml, cmd_vrmh)

# VRL
if do_plots:
    if args.allplots:
        cmd_vrl1 = 'draw.py -v %s -r VRL1,VRL2     -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_vrl1.root' % (variables_str, plots_dir, histograms_dir) + after_cmd
        cmd_vrl2 = 'draw.py -v %s -r VRL3,VRL4     -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_vrl2.root' % (variables_str, plots_dir, histograms_dir) + after_cmd
    else:
        cmd_vrl1 = 'draw.py -v %s -r VRL1 -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_vrl1.root' % (variables_str, plots_dir, histograms_dir) + after_cmd
        cmd_vrl2 = 'draw.py -v %s -r VRL3 -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_vrl2.root' % (variables_str, plots_dir, histograms_dir) + after_cmd

    run_cmd(cmd_vrl1, cmd_vrl2)


    cmd_vre = 'draw.py -v %s -r VRE -l data --data data -o %s --ext "pdf,png" --save %s/histograms_plots_vre.root --sepfakes' % (variables_str, plots_dir, histograms_dir) + after_cmd
    run_cmd(cmd_vre)


# Signal contamination
if do_plots and args.allplots:
    run_cmd('draw_signal_contamination.py -r %s -o %s --ext "pdf,png"' % (all_regions_str, plots_dir))


#--------
# Webpage
#--------
create_webpage(results_dir, web_dir, info_dict, regions=['SR',] + crs + vrs)

# # copy webpage
# wwwdir = '~/work/www/Susy/PhotonMetAnalysis/'

# # if not os.path.isdir(wwwdir+'analysis_%s' % tag):
# #     os.sytem('cp -r results/analysis_2016Oct03_test_vrm/www/ ~/work/www/Susy/PhotonMetAnalysis/analysis_2016Oct03_test_vrm


