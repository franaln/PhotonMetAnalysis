
import os
import ROOT

import YieldsTable
from prettytable import PrettyTable
from latextable import LatexTable

labels_dict = {
    'wgamma': 'W + $\gamma$',
    'ttbarg': '$t\\bar{t}$ + $\gamma$',
    'topgamma': 'single-$t$ + $\gamma$',
    'diboson': 'Dibosons',
    'wjets': 'W + jets',
    'ttbar': '$t\\bar{t}$',
    'zjets': 'Z + jets',
    'zllgamma': 'Z($\\rightarrow\ell\ell$) + $\gamma$',
    'znunugamma': 'Z($\\rightarrow\\nu\\nu$) + $\gamma$',
    'photonjet': '$\\gamma$ + jet',
    'vqqgamma': 'V($\\to$ qq)$+\\gamma$',
    'group_zllgamma_znunugamma': 'Z + $\gamma$',

    'efake15': '$e\\rightarrow\\gamma$ fakes',
    'jfake15': '$j\\rightarrow\\gamma$ fakes',

    'efake16': '$e\\rightarrow\\gamma$ fakes',
    'jfake16': '$j\\rightarrow\\gamma$ fakes',

    'efake': '$e\\rightarrow\\gamma$ fakes',
    'jfake': '$j\\rightarrow\\gamma$ fakes',
    }



def yieldstable(workspace, samples, channels, output_name, table_name, normalization_factors=None, latex=True):

    regions_list = channels.split(",")
    samples_list = samples.split(",")
    
    # from cmdLineUtils import cmdStringToListOfLists
    # sample_list_tmp = cmdStringToListOfLists(samples)

    # samples_list = []
    # for isam, sample in enumerate(sample_list_tmp):
    #     sampleName = YieldsTable.getName(sample)
    #     samples_list.append(sampleName)


       # call the function to calculate the numbers, or take numbers from pickle file  
    import pickle
    if workspace.endswith(".pickle"):
        print "READING PICKLE FILE"
        f = open(workspace, 'r')
        m = pickle.load(f)
        f.close()
    else:
        m = YieldsTable.latexfitresults(workspace, regions_list, samples_list, 'obsData') #, showSumA=False, doAsym=False, blinded=False, splitBins=False)
        # f = open(output_name.replace(".tex",".pickle"), 'w')
        # pickle.dump(m3, f)
        # f.close()

    regions_names = [ region.replace("_cuts", "").replace('_','\_') for region in m['names'] ]

    field_names = [table_name,] + regions_names
    align = ['l',] + [ 'r' for i in regions_names ]

    if latex:
        table = LatexTable(field_names, align=align, env=True)
    else:
        table = PrettyTable(field_names)

    #  number of observed events
    row = ['Observed events',] + [ '%d' % n for n in m['nobs'] ]
    table.add_row(row)
    table.add_line()

    #print the total fitted (after fit) number of events
    # if the N_fit - N_error extends below 0, make the error physical , meaning extend to 0
  
    row = ['Fitted bkg events', ]

    for index, n in enumerate(m['TOTAL_FITTED_bkg_events']):

        if (n - m['TOTAL_FITTED_bkg_events_err'][index]) > 0. :
            row.append('$%.2f \pm %.2f$' % (n, m['TOTAL_FITTED_bkg_events_err'][index]))

        else:
            print "WARNING:   negative symmetric error after fit extends below 0. for total bkg pdf:  will print asymmetric error w/ truncated negative error reaching to 0."
            row.append('$%.2f_{-%.2f}^{+%.2f}$' % (n, n, m['TOTAL_FITTED_bkg_events_err'][index]))

    table.add_row(row)
    table.add_line()

    if all([r.startswith('CR') for r in regions_names]) and normalization_factors is not None:

        row = ['Normalization factors',]
        for region in regions_names:
            row.append('$%.2f \pm %.2f$' % normalization_factors[region])

        table.add_row(row)
        table.add_line()


    map_listofkeys = m.keys()

    # print fitted number of events per sample
    # if the N_fit - N_error extends below 0, make the error physical , meaning extend to 0
    for sample in samples_list:
        for name in map_listofkeys:

            row = []

            if not "Fitted_events_" in name: 
                continue

            sample_name = name.replace("Fitted_events_", "")
            if sample_name != sample:
                continue
        
            sample_name = labels_dict.get(sample_name, sample_name)
            sample_name = sample_name.replace("_","\_")
            
            row.append('Fitted %s events' % sample_name)

            for index, n in enumerate(m[name]):

                if ((n - m['Fitted_err_'+sample][index]) > 0.) or not abs(n) > 0.00001:
                    row.append('$%.2f \\pm %.2f$' % (n, m['Fitted_err_'+sample][index]))

                else:
                    print "WARNING:   negative symmetric error after fit extends below 0. for sample", sample, "    will print asymmetric error w/ truncated negative error reaching to 0."
                    row.append('$%.2f_{-%.2f}^{+%.2f}$' % (n, n, m['Fitted_err_'+sample][index]))


            table.add_row(row)
  
    table.add_line()

    # print the total expected (before fit) number of events
    # if the N_fit - N_error extends below 0, make the error physical , meaning extend to 0
    row = ['MC exp. SM events',]
            
    for index, n in enumerate(m['TOTAL_MC_EXP_BKG_events']):
        row.append('$%.2f$' % n)

    table.add_row(row)
    table.add_line()

    map_listofkeys = m.keys()

    # print expected number of events per sample
    # if the N_fit - N_error extends below 0, make the error physical , meaning extend to 0
    for sample in samples_list:
        for name in map_listofkeys:

            row = []
            if "MC_exp_events_" in name  and sample in name:

                sample_name = name.replace("MC_exp_events_","")

                if sample_name != sample:
                  continue

                sample_name = labels_dict.get(sample_name, sample_name)
                sample_name = sample_name.replace("_","\_")
              
                if sample not in ['efake', 'jfake']:
                    row.append('MC exp. %s events' % sample_name)
                else: 
                    row.append('%s events' % sample_name)

                for index, n in enumerate(m[name]):
                    row.append('$%.2f$' % n)

                table.add_row(row)


    table.add_line()

    table.save_tex(output_name)








