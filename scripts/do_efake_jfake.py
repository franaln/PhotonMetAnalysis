#! /usr/bin/env python

import os

from samples import samples_dict

ptag = '2667'
version = '32'

mini_dir  = '/disk/falonso/mini2/'

data15 = samples_dict.get('data15')
data16 = samples_dict.get('data16')

for s in data15 + data16:

    short_name = '.'.join(s.split('.')[0:3])
    
    input_path = mini_dir + 'v' + version + '/' + '%s.mini.p%s.v%s_output.root' % (short_name, ptag, version)

    output_path_efake = input_path.replace('data15_13TeV', 'efake15').replace('data16_13TeV', 'efake16')
    output_path_jfake = input_path.replace('data15_13TeV', 'jfake15').replace('data16_13TeV', 'jfake16')

    # efake
    cmd = '$SUSY_ANALYSIS/macros/create_efake_mini %s %s' % (input_path, output_path_efake)

    print cmd
    os.system(cmd)

    # jfake
    cmd = '$SUSY_ANALYSIS/macros/create_jfake_mini %s %s' % (input_path, output_path_jfake)

    print cmd
    os.system(cmd)


