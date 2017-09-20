# single photonutils.py
# common and usefull things

import os
import sys
import subprocess

# Directories
susy_dir = os.environ['SUSY_ANALYSIS']

# colours
colours = {
    'green':  '\033[92m',
    'red':    '\033[91m',
    'blue':   '\033[94m',
    'purple': '\033[95m',
    'endc':   '\033[0m',
}

# messages
def msg(text):
    print colours['green'] + '# ' + colours['endc'] + text

# files, directories
def mkdirp(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if os.path.isdir(path):
            pass
        else:
            raise
        
def rmdir(path):
    import shutil
    try:
        shutil.rmtree(path)
    except OSError as exc:
        pass


def run_cmd(cmd, logfile=None, stdout=False):

    print cmd

    if stdout and logfile is not None:
        cmd = '(set -o pipefail ; %s | tee %s)' % (cmd, logfile)
        
    elif logfile is not None:
        cmd = '%s > %s 2>&1' % (cmd, logfile)

    sc = os.system(cmd)

    # if sc != 0:
    #     print 'command sc != 0. exiting...'
    #     sys.exit(1)
            
    return sc


def run_HF_cmd(cmd):

    pass



def run_cmds_and_wait(*cmds):

    processes = []
    for cmd in cmds:
        print cmd
        p = subprocess.Popen(cmd, shell=True)
        processes.append(p)

    for p in processes:
        p.wait()
