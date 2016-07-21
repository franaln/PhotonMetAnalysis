#! /usr/bin/env python

import os
import sys
import shutil
import argparse
import datetime
import ROOT

from utils import mkdirp, run_cmd

def main():

    parser = argparse.ArgumentParser(description='run bkgonly')
    
    parser.add_argument('-i', dest='input', help='Input file with histograms')
    parser.add_argument('-o', dest='output', help='Output directory for results')
    parser.add_argument('--sr', dest='signal_region', help='SRL, SRH, SRinclL or SRinclH')
    parser.add_argument('-c', dest='configfile', help='HF configfile')
    parser.add_argument('--hf',  dest='hf_options', help='HF extra options')
    parser.add_argument('--log',  dest='logfile', default='histfitter.log', help='Logfile')

    parser.add_argument('--val', action='store_true', dest='do_validation', help='Do validation')
    parser.add_argument('--mc', action='store_true', help='Use MC backgrounds')
    parser.add_argument('--syst', action='store_true', help='Do systematics')
    parser.add_argument('--data', default='data', help='data|data15|data16')

    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)
    
    args = parser.parse_args()
    
    configfile = os.path.abspath(args.configfile)
    histograms_file = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output)
    region = args.signal_region
    
    if not os.path.exists(output_dir):
        mkdirp(output_dir)

    # move to analysis directory
    old_pwd = os.getenv('PWD')
    susy_dir = os.environ['SUSY_ANALYSIS']
    os.chdir(susy_dir + '/run')

    # Run HistFitter
    opttag = ''
    if args.mc:
        opttag += '_mc'
    if not args.syst:
        opttag += '_nosys'

    if opttag:
        results_dir = 'results/PhotonMetAnalysis_bkgonly%s_%s' % (opttag, region)
    else:
        results_dir = 'results/PhotonMetAnalysis_bkgonly_%s' % region

    options = '-i %s --sr %s --rm' % (histograms_file, region)
    if args.do_validation:
        options += ' --val'
    if args.mc:
        options += ' --mc'
    if args.syst:
        options += ' --syst'
    if args.data != 'data':
        options += ' --data %s' % args.data

    hf_extra_options = ''
    if args.hf_options is not None:
        hf_extra_options = args.hf_options

    cmd = 'HistFitter.py -u \'"%s"\' -w -f -V -F bkg %s %s' % (options, hf_extra_options, configfile)
    run_cmd(cmd, logfile=output_dir+'/'+args.logfile)

    # mv from results dir to output dir    
    mv_cmd = 'cp %s/* %s/' % (results_dir, output_dir)
    os.system(mv_cmd)

    os.chdir(old_pwd)

            


if __name__ == '__main__':
    main()
