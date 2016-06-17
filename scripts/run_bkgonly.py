#! /usr/bin/env python

import os
import sys
import shutil
import argparse
import datetime
import ROOT

from utils import mkdirp, rmdir
from yieldstable import yieldstable


def run_cmd(cmd, logfile):
    print cmd
    
    cmd = '(set -o pipefail ; %s | tee %s)' % (cmd, logfile)
    sc = os.system(cmd)

    if sc != 0:
        print 'command sc != 0. exiting...'
        sys.exit(1)

def get_normalization_factors(workspace):

    mu_dict = dict()

    # get mus from workspace
    if not os.path.isfile(workspace):
        print 'Workspace does not exist'
        return mu_dict

    rf = ROOT.TFile(workspace)

    w = rf.Get('w')

    for name in ('q', 'w', 't'):
        mu = w.var('mu_'+name)
        mu_dict['CR%s' % name.upper()] = (mu.getValV(), mu.getError())

    rf.Close()

    return mu_dict


def main():

    parser = argparse.ArgumentParser(description='run bkgonly')
    
    parser.add_argument('-i', dest='input', help='Input file with histograms')
    parser.add_argument('-o', dest='output', help='Output directory for results')
    parser.add_argument('-n', dest='region', help='L or H')
    parser.add_argument('-c', dest='configfile', help='HF configfile')

    parser.add_argument('--val', action='store_true', dest='do_validation', help='Do validation')
    parser.add_argument('--mc', action='store_true', help='Use MC backgrounds')
    parser.add_argument('--dosyst', action='store_true', help='Do systematics')

    parser.add_argument('--fit',    action='store_true', help='Do fit')
    parser.add_argument('--tables', action='store_true', help='Do tables')
    parser.add_argument('--plots',  action='store_true', help='Do plots')

    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)
    
    args = parser.parse_args()
    
    configfile = args.configfile #"PhotonMet_HistFitter_config.py"
    histograms_file = args.input
    region = 'SR%s' % args.region

    ## backgrounds
    if args.mc:
        backgrounds = [
            'photonjet',
            'wgamma',
            'zllgamma', 
            'znunugamma',
            'ttbar', 'ttbarg',
            'zjets', 'wjets',
            'multijet',
            ]
    else:
        backgrounds = [
            'photonjet',
            'wgamma',
            'zllgamma', 
            'znunugamma',
            'ttbarg',
            'jfake',
            'efake',
            ]
    

    # Output dir
    if args.output is not None:
        output_dir = args.output
    else:
        output_dir = 'run_%s' % datetime.datetime.strftime(datetime.datetime.now(), '%d%b_%H%M%S')

    mkdirp(output_dir)
    mkdirp(output_dir+'/fit')
    mkdirp(output_dir+'/plots')
    mkdirp(output_dir+'/tables')


    # # move to analysis directory
    # old_pwd = os.getenv('PWD')
    # susy_dir = os.environ['SUSY_ROOT']
    # os.chdir(susy_dir + '/analysis')

    # Run HistFitter
    if args.fit:

        if args.mc:
            results_dir = 'results/PhotonMetAnalysis_bkgonly_mc_%s' % region
        else:
            results_dir = 'results/PhotonMetAnalysis_bkgonly_%s' % region

        options = '-i %s --sr %s' % (histograms_file, region)
        if args.do_validation:
            options += ' --val'
        if args.mc:
            options += ' --mc'
        if args.dosyst:
            options += ' --syst'


        cmd = 'HistFitter.py -u \'"%s"\' -w -f -V -F bkg %s' % (options, configfile)
        run_cmd(cmd, output_dir+'/hf.log')

        # mv from results dir to output dir    
        mv_cmd = 'cp %s/* %s/' % (results_dir, output_dir+'/fit')
        os.system(mv_cmd)


    # Get normalization factors
    ws = "%s/fit/BkgOnlyFit_combined_BasicMeasurement_model_afterFit.root" % output_dir
    backgrounds_str = ','.join(backgrounds)
    
    norm_factors = get_normalization_factors(ws)

    # create yields tables
    if args.tables:

        ## CR
        yieldstable(ws, backgrounds_str, 'CRQ,CRW,CRT', output_dir+'/tables/table_cr.tex', 'CR for SR%s' % args.region, normalization_factors=norm_factors)

        ## VR
        if args.do_validation:

            yieldstable(ws, backgrounds_str, 'VRM1,VRM2,VRM3',       output_dir+'/tables/table_vrm.tex', 'VR for SR%s' % args.region)
            yieldstable(ws, backgrounds_str, 'VRD1,VRD2,VRD3',       output_dir+'/tables/table_vrd.tex', 'VR for SR%s' % args.region)
            yieldstable(ws, backgrounds_str, 'VRL1,VRL2,VRL3,VRL4',  output_dir+'/tables/table_vrl.tex', 'VR for SR%s' % args.region)

        ## SR
        yieldstable(ws, backgrounds_str, 'SR', output_dir+'/tables/table_sr.tex', 'Signal Region')

        # systematics tables
        if args.dosyst:
            cmd1 = 'SysTable.py -w ' + ws + ' -c SR -o %s -%%' % (output_dir+'/tables/table_syst_sr.tex')
            cmd2 = 'SysTable.py -w ' + ws + ' -c CRQ,CRW,CRT -o %s -%%' % (output_dir+'/tables/table_syst_cr.tex')

            os.system(cmd1)
            os.system(cmd2)




    # Plots
    if args.plots:

        cr_str = ','.join([ reg+'_'+args.region for reg in ['CRQ', 'CRW', 'CRT'] ])

        cmd_cr = 'draw.py -v met_et,meff,ph_pt,rt4,ht,dphi_jetmet -r %s -o %s' % (cr_str, output_dir)

        muq = '%f,%f' % norm_factors['CRQ']
        muw = '%f,%f' % norm_factors['CRW']
        mut = '%f,%f' % norm_factors['CRT']

        after_cmd = ' --after --muq %s --muw %s --mut %s' % (muq, muw, mut)

        os.system(cmd_cr)
        os.system(cmd_cr+after_cmd)

        if args.do_validation:

            # cr_str = ','.join([ reg+'_'+args.n for reg in ['VR1,VR2,VR3,VR4,VR5,VR6,VR7,VR8,VR9,VR10,VR11,VR12', 'CRW', 'CRT'] ])

            vr_str = 'VRL1_%s,VRD1_%s,VRM1_%s' % (args.region, args.region, args.region)

            cmd_vr = 'draw.py -v ph_pt,met_et,ht,meff -r %s -o %s' % (vr_str, output_dir)
            os.system(cmd_vr+after_cmd)


    #os.chdir(old_pwd)
    print 'results saved in -> %s' % output_dir


if __name__ == '__main__':
    main()
