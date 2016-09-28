# mini -> histograms -> fit -> tables / plots / limits

import os
import sys
import subprocess
import datetime

from fitutils import get_normalization_factors
from yieldstable import yieldstable, merge_tables
from webpage import WebPage
import analysis
import regions

today = datetime.datetime.today()

daytag = today.strftime('%Y%b%d')
extratag = 'ds2_v41_crw1jet'

tag = daytag + ('_'+extratag if extratag else '')

mc_samples = analysis.backgrounds_mc

# Config
unblind = True
do_syst = False
do_plots = False

srs = ['SRi_L', 'SRi_H']
crs = ['CRQ', 'CRW', 'CRT']
vrs = ['VRM1', 'VRM2', 'VRM3', 'VRL1', 'VRL2', 'VRL3', 'VRL4', 'VRD1', 'VRD2', 'VRD3']

# Results outpu dir
susy_dir = os.environ['SUSY_ANALYSIS']

results_dir    = 'results/analysis_%s' % (tag)
log_dir        = '%s/log'        % results_dir
histograms_dir = '%s/histograms' % results_dir
fits_dir       = '%s/fits'       % results_dir
tables_dir     = '%s/tables'     % results_dir
plots_dir      = '%s/plots'      % results_dir
web_dir        = '%s/www'      % results_dir

os.system('mkdir -p %s' % results_dir)
os.system('mkdir -p %s' % log_dir)
os.system('mkdir -p %s' % histograms_dir)
os.system('mkdir -p %s' % fits_dir)
os.system('mkdir -p %s' % tables_dir)
os.system('mkdir -p %s' % plots_dir)
os.system('mkdir -p %s' % web_dir)


logfile_srl = log_dir + '/analysis_srl.txt'
logfile_srh = log_dir + '/analysis_srh.txt'

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
info = """
Date: %s
Mini version: %s
Lumi: %.2f
""" % (today.strftime('%d %b %Y'), ','.join(analysis.versions), (analysis.lumi_data15+analysis.lumi_data16))

with open(log_dir + '/info.txt', 'w+') as f:
    f.write(info)


#------------------
# Histograms (cuts)
#------------------
histograms_srl_path = '%s/histograms_srl.root' % (histograms_dir)
histograms_srh_path = '%s/histograms_srh.root' % (histograms_dir)

samples = ','.join(mc_samples) + ',signal,data,efake,jfake'

cmd_srl = 'sphistograms.py -o %s -s %s -r all -n L --lumi data' % (histograms_srl_path, samples) 
cmd_srh = 'sphistograms.py -o %s -s %s -r all -n H --lumi data' % (histograms_srh_path, samples)

if unblind:
    cmd_srl += ' --unblind'
    cmd_srh += ' --unblind'

if do_syst:
    cmd_srl += ' --syst'
    cmd_srh += ' --syst'

if not os.path.isfile(histograms_srl_path) or not os.path.isfile(histograms_srh_path):
    run_cmd(cmd_srl, cmd_srh)


#--------------
# Bkg-only Fit
#--------------
configfile = susy_dir + '/lib/PhotonMet_HistFitter_config.py'

fit_srl_dir = '%s/bkgonly_srl' % fits_dir
fit_srh_dir = '%s/bkgonly_srh' % fits_dir

cmd_srl = 'run_bkgonly.py -i %s -o %s --sr SRiL -c %s --val --data data --log %s/bkgonly_fit_srl.log' % (histograms_srl_path, fit_srl_dir, configfile, log_dir)
cmd_srh = 'run_bkgonly.py -i %s -o %s --sr SRiH -c %s --val --data data --log %s/bkgonly_fit_srh.log' % (histograms_srh_path, fit_srh_dir, configfile, log_dir)

if do_syst:
    cmd_srl += ' --syst'
    cmd_srh += ' --syst'

run_cmd(cmd_srl)
run_cmd(cmd_srh)

ws_srl = fit_srl_dir + "/BkgOnlyFit_combined_BasicMeasurement_model_afterFit.root"
ws_srh = fit_srh_dir + "/BkgOnlyFit_combined_BasicMeasurement_model_afterFit.root"

mus_srl = get_normalization_factors(ws_srl)
mus_srh = get_normalization_factors(ws_srh)


#-------
# Tables
#-------

backgrounds_str = 'photonjet,wgamma,[zllgamma,znunugamma],ttbarg,efake,jfake,[diphoton,vgammagamma]' 
        
# Yields tables
## CR
yieldstable(ws_srl, backgrounds_str, 'CRQ,CRW,CRT', tables_dir+'/table_cr_srl.tex', 'CR for SRL', is_cr=True)
yieldstable(ws_srh, backgrounds_str, 'CRQ,CRW,CRT', tables_dir+'/table_cr_srh.tex', 'CR for SRH', is_cr=True)

## VR
yieldstable(ws_srl, backgrounds_str, 'VRM1,VRM2,VRM3',      tables_dir+'/table_vrm_srl.tex', 'VR for SRL')
yieldstable(ws_srl, backgrounds_str, 'VRL1,VRL2,VRL3,VRL4', tables_dir+'/table_vrl_srl.tex', 'VR for SRL')
yieldstable(ws_srl, backgrounds_str, 'VRD1,VRD2,VRD3',      tables_dir+'/table_vrd_srl.tex', 'VR for SRL')

yieldstable(ws_srh, backgrounds_str, 'VRM1,VRM2,VRM3',      tables_dir+'/table_vrm_srh.tex', 'VR for SRH')
yieldstable(ws_srh, backgrounds_str, 'VRL1,VRL2,VRL3,VRL4', tables_dir+'/table_vrl_srh.tex', 'VR for SRH')
yieldstable(ws_srh, backgrounds_str, 'VRD1,VRD2,VRD3',      tables_dir+'/table_vrd_srh.tex', 'VR for SRH')

## SR
yieldstable(ws_srl, backgrounds_str, 'SRi', tables_dir+'/table_sr_srl.tex', 'Signal Region', unblind=unblind)
yieldstable(ws_srh, backgrounds_str, 'SRi', tables_dir+'/table_sr_srh.tex', 'Signal Region', unblind=unblind)

# Systematics tables
cmd1 = 'SysTable.py -w ' + ws_srl + ' -c SRi              -o %s/table_syst_sr_srl.tex -%%' % tables_dir
cmd2 = 'SysTable.py -w ' + ws_srl + ' -c CRQ,CRW,CRT      -o %s/table_syst_cr_srl.tex -%%'  % tables_dir
cmd3 = 'SysTable.py -w ' + ws_srl + ' -c SRi              -o %s/table_syst_sr_bkgs_srl.tex -%% -s photonjet,ttbarg,wgamma' % tables_dir
            
run_cmd(cmd1)
run_cmd(cmd2)
run_cmd(cmd3)

# Merge tables
# SR
merge_tables(tables_dir+'/table_sr_srl.tex', tables_dir+'/table_sr_srh.tex', tables_dir+'/table_sr_srl_srh.tex')

# CR
merge_tables(tables_dir+'/table_cr_srl.tex', tables_dir+'/table_cr_srh.tex', tables_dir+'/table_cr_srl_srh.tex')

# VR
merge_tables(tables_dir+'/table_vrm_srl.tex', tables_dir+'/table_vrm_srh.tex', tables_dir+'/table_vrm_srl_srh.tex')
merge_tables(tables_dir+'/table_vrl_srl.tex', tables_dir+'/table_vrl_srh.tex', tables_dir+'/table_vrl_srl_srh.tex')
merge_tables(tables_dir+'/table_vrd_srl.tex', tables_dir+'/table_vrd_srh.tex', tables_dir+'/table_vrd_srl_srh.tex')



#-------
# Plots
#-------

variables = [
    # 'ph_n',
    'ph_pt[0]',
    'ph_etas2[0]',
    # 'ph_phi[0]',

    'jet_n',
    # 'bjet_n',
    'jet_pt',
    # 'jet_pt[0]',
    # 'jet_pt[1]',
    
    'met_et',
    # 'met_phi'
    # 'met_sumet',
    #'tst_et',
    # 'tst_phi',

    'ht',
    'meff',

    'dphi_jetmet',
    'dphi_gammet',
    'dphi_gamjet',
]


muq_l = '%f,%f' % mus_srl['CRQ']
muw_l = '%f,%f' % mus_srl['CRW']
mut_l = '%f,%f' % mus_srl['CRT']

muq_h = '%f,%f' % mus_srh['CRQ']
muw_h = '%f,%f' % mus_srh['CRW']
mut_h = '%f,%f' % mus_srh['CRT']

# Distributions
after_cmd_srl = ' --after --muq %s --muw %s --mut %s' % (muq_l, muw_l, mut_l)
after_cmd_srh = ' --after --muq %s --muw %s --mut %s' % (muq_h, muw_h, mut_h)

variables_str = ','.join(variables)


## preselection
# cmd = 'draw.py -v %s -r presel -l data --data data -o %s --n1 --ext "pdf,png"' % (variables_str, plots_dir) 
# run_cmd(cmd)

## SR
cmd_srl = 'draw.py -v %s -r SRi_L -l data --data data -o %s --signal --n1 --ext "pdf,png"' % (variables_str, plots_dir) + after_cmd_srl
cmd_srh = 'draw.py -v %s -r SRi_H -l data --data data -o %s --signal --n1 --ext "pdf,png"' % (variables_str, plots_dir) + after_cmd_srh

if do_plots and unblind:
    run_cmd(cmd_srl, cmd_srh)


## CR
cmd_srl = 'draw.py -v %s -r CRQ_L,CRW_L,CRT_L -l data --data data -o %s --ext "pdf,png"' % (variables_str, plots_dir) + after_cmd_srl
cmd_srh = 'draw.py -v %s -r CRQ_H,CRW_H,CRT_H -l data --data data -o %s --ext "pdf,png"' % (variables_str, plots_dir) + after_cmd_srh

if do_plots:
    run_cmd(cmd_srl)
    run_cmd(cmd_srh)

## vr
cmd_srl = 'draw.py -v %s -r VRM1_L,VRM2_L,VRM3_L -l data --data data -o %s --ext "pdf,png"' % (variables_str, plots_dir) + after_cmd_srl
cmd_srh = 'draw.py -v %s -r VRM1_H,VRM2_H,VRM3_H -l data --data data -o %s --ext "pdf,png"' % (variables_str, plots_dir) + after_cmd_srh

if do_plots:
    run_cmd(cmd_srl)
    run_cmd(cmd_srh)

cmd_srl = 'draw.py -v %s -r VRL1_L,VRL2_L,VRL3_L,VRL4_L -l data --data data -o %s --ext "pdf,png"' % (variables_str, plots_dir) + after_cmd_srl
cmd_srh = 'draw.py -v %s -r VRL1_H,VRL2_H,VRL3_H,VRL4_H -l data --data data -o %s --ext "pdf,png"' % (variables_str, plots_dir) + after_cmd_srh

if do_plots:
    run_cmd(cmd_srl)
    run_cmd(cmd_srh)

cmd_srl = 'draw.py -v %s -r VRD1_L,VRL2_L,VRD3_L -l data --data data -o %s --ext "pdf,png"' % (variables_str, plots_dir) + after_cmd_srl
cmd_srh = 'draw.py -v %s -r VRD1_H,VRD2_H,VRD3_H -l data --data data -o %s --ext "pdf,png"' % (variables_str, plots_dir) + after_cmd_srh

if do_plots:
    run_cmd(cmd_srl)
    run_cmd(cmd_srh)

# Region pulls
cmd_srl_all  = 'plot_region_pull.py --ws %s -r CRQ,CRW,CRT,VRM1,VRM2,VRM3,VRL1,VRL2,VRL3,VRL4,VRD1,VRD2,VRD3,SRi -n L --data data -o %s --ext "pdf,png"' % (ws_srl,  plots_dir)  + (' --unblind' if unblind else '')
cmd_srh_all  = 'plot_region_pull.py --ws %s -r CRQ,CRW,CRT,VRM1,VRM2,VRM3,VRL1,VRL2,VRL3,VRL4,VRD1,VRD2,VRD3,SRi -n H --data data -o %s --ext "pdf,png"' % (ws_srh,  plots_dir)  + (' --unblind' if unblind else '')

if do_plots:
    run_cmd(cmd_srl_all, cmd_srh_all)

#--------
# Webpage
#--------
page = WebPage(web_dir, 'Photon + jets + MET analysis')

# Info
page.add('Date: %s' % today.strftime('%d %b %Y'))
page.add('Mini version: %s' % ','.join(analysis.versions))
page.add('Lumi: %.2f pb-1' % (analysis.lumi_data15+analysis.lumi_data16))
page.add('Systematics: %s (theoretical syst always used)' % do_syst)


# Tables
page.add_section('Tables')
page.add_yields_table(tables_dir+'/table_cr_srl_srh.html')
page.add_yields_table(tables_dir+'/table_vrm_srl_srh.html')
page.add_yields_table(tables_dir+'/table_vrl_srl_srh.html')
page.add_yields_table(tables_dir+'/table_vrd_srl_srh.html')
page.add_yields_table(tables_dir+'/table_sr_srl_srh.html')

# Plots
if do_plots:
    page.add_section('Plots')
    page.add_plots_table(['SRi',] + crs + vrs, plots_dir)

page.save()
