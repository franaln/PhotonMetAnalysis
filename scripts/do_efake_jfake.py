#! /usr/bin/env python

import os
from samples import data

version = '20'

mini_dir  = '/ar/pcunlp001/raid/falonso/mini2/'


for s in data:
    
    input_path = mini_dir + 'v' + version + '/' + '%s.mini_v%s_output.root' % ('.'.join(s.split('.')[0:3]), version)

    output_path_efake = input_path.replace('data15_13TeV', 'efake')
    output_path_jfake = input_path.replace('data15_13TeV', 'jfake')

    # efake
    cmd = './macros/create_efake_mini %s %s' % (input_path, output_path_efake)

    print cmd
    os.system(cmd)

    # # jfake
    # cmd = './macros/create_jfake_mini %s %s' % (input_path, output_path_jfake)

    # print cmd
    # os.system(cmd)
