#! /usr/bin/env python

import os
import sys
import shutil
import argparse
import datetime
import ROOT

from utils import mkdirp, run_cmd

from miniutils import lumi_dict

def do_bkgonlyfit(configfile, input_file, output_dir, region, data, do_validation=False, syst='', usemc=False, logfile=None, hf_options=None):

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
        results_dir = 'results/PhotonMetAnalysis_bkgonly%s' % opttag
    else:
        results_dir = 'results/PhotonMetAnalysis_bkgonly'

    lumi = 0.
    for year in data.split('+'):
        lumi += lumi_dict.get(year, 0.)

    options = '-i %s --sr %s --rm --lumi %.2f' % (input_file, region, lumi)
    if do_validation:
        options += ' --val'
    if do_syst:
        options += syst
    if usemc:
        options += ' --mc'

    if args.data != 'data':
        options += ' --data %s' % data

    hf_extra_options = ''
    if hf_options is not None:
        hf_extra_options = args.hf_options

    cmd = 'HistFitter.py -u \'"%s"\' -w -f -V -F bkg %s %s' % (options, hf_extra_options, configfile)
    run_cmd(cmd, logfile='hf.log', stdout=True)

    # mv logfile
    if args.logfile is not None:
        os.system('mv hf.log %s' % os.path.join(old_pwd, logfile))

    # mv from results dir to output dir    
    mv_cmd = 'cp %s/* %s/' % (results_dir, output_dir)
    os.system(mv_cmd)

    os.chdir(old_pwd)



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='do_bkgonlyfit')
    
    parser.add_argument('-i', dest='input', help='Input file with histograms')
    parser.add_argument('-o', dest='output', help='Output directory for results')
    parser.add_argument('--sr', dest='signal_region', help='SRL, SRH, SRinclL or SRinclH')
    parser.add_argument('-c', dest='configfile', help='HF configfile')
    parser.add_argument('--hf',  dest='hf_options', help='HF extra options')
    parser.add_argument('--log',  dest='logfile', default='histfitter.log', help='Logfile')
    parser.add_argument('--syst', help='Systematics options to pass to HF')

    parser.add_argument('--val', action='store_true', dest='do_validation', help='Do validation')
    parser.add_argument('--mc', action='store_true', help='Use MC backgrounds')
    parser.add_argument('--data', help='2015+2016 or 2017')


    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)
    
    args = parser.parse_args()
    
    configfile  = os.path.abspath(args.configfile)
    input_file  = os.path.abspath(args.input)
    output_dir  = os.path.abspath(args.output)
    region      = args.signal_region


    do_bkgonlyfit(configfile, input_file, output_dir, region, args.data, args.val, args.syst, args.mc, logfile=args.logfile, hf_options=args.hf_options)
            
