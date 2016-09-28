#! /usr/bin/env python

import sys
import os
import argparse
import subprocess

from mass_dict import mass_dict


pwd = os.getcwd().strip()+"/"
hf_dir = os.getenv('HISTFITTER')


def write_and_submit_job(jobdir, logdir, resultsdir, configfile, options, point, region, queue, do_submission=False):

    job_name = '%s_%s' % (region, point)

    filename = jobdir + '/job_' + job_name + '.sh'

    f = open(filename, 'w')

    f.write("""#! /bin/bash

echo '======================'
echo 'Configuring HistFitter'
echo '======================'

XCWD=$PWD

cd /afs/cern.ch/work/f/falonso/Susy/Run2/PhotonMetAnalysis

source setup.sh

cd $XCWD

/bin/mkdir -pv results
/bin/mkdir -pv data
/bin/mkdir -pv config
/bin/cp %s/config/HistFactorySchema.dtd config/

/bin/ls -ltr
echo $ROOTSYS
echo $HISTFITTER
hostname

""" % hf_dir)

    f.write(""" 
echo '========================'
echo ' Running HistFitter now'
echo '========================'
""")

    cmd = 'HistFitter.py -u \'"%s"\' -w -f -F excl -p -g %s %s' % (options, point, configfile)

    f.write("echo " + cmd + " \n\n")
    f.write(cmd+" \n\n")

    f.write("sleep 2\n\n")
    
    job_results_dir = os.path.join(resultsdir, job_name)

    f.write('ls results/\n')
    f.write('/bin/cp -r results/ ' + job_results_dir + '\n')

    f.close()

    subprocess.call("chmod u+x " + filename, shell=True)

    logfile = logdir + "/job_" + job_name + '.log'
    errfile = logfile

    cmd = 'bsub -q ' + queue + ' -e ' + errfile + ' -o ' + logfile + ' -J ' + job_name + ' ' + filename

    print cmd
    if do_submission:
        subprocess.call(cmd, shell=True)




def main():

    parser = argparse.ArgumentParser(description='run limit (batch)')

    parser.add_argument('-i', dest='histfile', help='Input file with histograms', required=True)
    parser.add_argument('-o', dest='output', help='Output directory for results', required=True)
    parser.add_argument('-c', dest='configfile', default=os.path.join(os.environ['SUSY_ANALYSIS'], 'lib/PhotonMet_HistFitter_config.py'), help='HF configfile')
    parser.add_argument('--sr', dest='region', help='SRL, SRH, SRinclL or SRinclH', required=True)
    parser.add_argument('--hf',  dest='hf_options', help='HF extra options')
    parser.add_argument('--queue',  default='8nh', help='Batch queue (8nh|1nd|...)')
    parser.add_argument('--nosyst', action='store_true', help='No systematics')
    parser.add_argument('--data', default='data', help='data|data15|data16')
    parser.add_argument('--asimov',  action='store_true', help='Use asimov aprox.')
    parser.add_argument('--ntoys',  default='5000', help='Number of toys (By default use toys)')
    parser.add_argument('--dry', action='store_true', help='Dry run (not submit to batch)')
    parser.add_argument('--sigxs',  action='store_true', help='')
    parser.add_argument('--only', help='Point as 1600_450')
    parser.add_argument('--exclude', help='Point as 1600_450')
    parser.add_argument('--failed', help='')

    args = parser.parse_args()


    histfile = os.path.abspath(args.histfile)

    outdir = os.path.abspath(args.output)

    jobdir     = os.path.join(outdir, 'jobs')
    logdir     = os.path.join(outdir, 'logs')
    resultsdir = os.path.join(outdir, 'results')

    os.system('mkdir -p %s %s %s' % (jobdir, logdir, resultsdir))

    if args.asimov:
        options = '-i %s --sr %s --asimov --syst --data %s' % (histfile, args.region, args.data)
    else:
        options = '-i %s --sr %s --ntoys %s --syst --data %s' % (histfile, args.region, args.ntoys, args.data)

    if args.sigxs:
        options += ' --sigxs'

    requested_points = []
    excluded_points  = []
    if args.only is not None:
        requested_points = args.only.split(',')
    if args.exclude is not None:
        excluded_points = args.exclude.split(',')

    if args.failed is not None:
        lines = [ l.strip() for l in open(args.failed).read().split('\n') if l ]
        
        requested_points.extend(lines)

    for (m3, mu) in mass_dict.iterkeys():

        point = '%d_%d' % (m3, mu)

        if requested_points and point not in requested_points:
            continue

        if point in excluded_points:
            continue

        write_and_submit_job(jobdir, logdir, resultsdir, args.configfile, options, point, args.region, args.queue, not args.dry)


if __name__ == '__main__':
    main()
