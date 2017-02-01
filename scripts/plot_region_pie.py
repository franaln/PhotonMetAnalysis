import ROOT

import pickle
import subprocess
from array import array
from rootutils import get_color

regions = ['SRiL', 'SRiH']
workspace = 'results/analysis_2017Jan31/fits/bkgonly/BkgOnlyFit_combined_BasicMeasurement_model_afterFit.root'

all_samples = [
    'photonjet',
    'wgamma',
    'zllgamma',
    'znunugamma',
    'ttbarg',
    'diphoton',
    'vgammagamma',
    'jfake',
    'efake', 
]

samples = ','.join(all_samples)

labels = [
    '#gamma + jets',
    'W#gamma',
    'Z#gamma',
    'tt#gamma',
    '#gamma#gamma/W#gamma#gamma/Z#gamma#gamma',
    'jet#rightarrow#gamma fakes',
    'e#rightarrow#gamma fakes',
    ]

colors = [
    '#E24A33',
    '#fcdd5d',
    '#f7fab4',
    #'#f7fac9',
    '#32b43c',
    '#ffa04d',
    #'#e5ac49',
    '#348ABD',
    '#a4cee6',
]

pickle_filename = "yield_all.pickle"

cmd = "YieldsTable.py -c %s -s %s -w %s -o yield_all.tex" % (",".join(regions), samples, workspace)
print cmd
subprocess.call(cmd, shell=True)
picklefile = open(pickle_filename,'rb')

mydict = pickle.load(picklefile)

results = []

for region in mydict["names"]:

    canvas = ROOT.TCanvas("", "", 300, 300)


    index = mydict["names"].index(region)

    n_obs = mydict["nobs"][index]
    n_exp = mydict["TOTAL_FITTED_bkg_events"][index]

    exp_syst = mydict["TOTAL_FITTED_bkg_events_err"][index]

    n_exp_components = {}

    for sam in samples.split(","):
        if "Fitted_events_"+sam in mydict:
            n_exp_components[sam] = mydict["Fitted_events_"+sam][index]
        else:
            n_exp_components[sam] = 0.

    merged_bkgs = []
    merged_bkgs.append(n_exp_components['photonjet'])
    merged_bkgs.append(n_exp_components['wgamma'])
    merged_bkgs.append(n_exp_components['zllgamma']+n_exp_components['znunugamma'])
    merged_bkgs.append(n_exp_components['ttbarg'])
    merged_bkgs.append(n_exp_components['diphoton']+n_exp_components['vgammagamma'])
    merged_bkgs.append(n_exp_components['jfake'])
    merged_bkgs.append(n_exp_components['efake'])


            
    color_array  = array('i', [ get_color(c) for c in colors ])
    number_array = array('f', merged_bkgs)
    labels_fix  = [ array( 'c', '%s\0' % label) for label in labels ]
    label_array = array( 'l', map( lambda x: x.buffer_info()[0], labels_fix ) )

    pie = ROOT.TPie(region, region, len(number_array), number_array, color_array, label_array)
    pie.SetRadius(0.3)
    pie.SetTitle('')
    pie.SetLabelFormat("%perc") #splitline{%txt}{%perc}")                                                                                              
    pie.Draw("<")
    
    legend = pie.MakeLegend(0.05,0.65,0.25,0.95)
    legend.SetFillColor(0)
    legend.SetBorderSize(0)
    legend.Draw()

    canvas.SaveAs('pie_'+region+'.pdf')



