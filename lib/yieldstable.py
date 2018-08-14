import os
import ROOT
try:
    import cPickle as pickle
except:
    import pickle
from prettytable import PrettyTable, from_html_one
from latextable import LatexTable

ROOT.gSystem.Load('%s/lib/libSusyFitter.so' % os.getenv('HISTFITTER'))
ROOT.gInterpreter.ProcessLine('#include "{0}/src/Utils.h" '.format(os.getenv('HISTFITTER')))
from ROOT import Util

from cmdLineUtils import getPdfInRegions, getName, getPdfInRegionsWithRangeName, cmdStringToListOfLists
from fitutils import get_normalization_factors

labels_latex_dict = {
    'wgamma': '$W\gamma$',
    'ttgamma': '$t\\bar{t}\gamma$',
    'topgamma': 'single-$t$ + $\gamma$',
    'diboson': 'Dibosons',
    'wjets': 'W + jets',
    'ttbar': '$t\\bar{t}$',
    'zjets': 'Z + jets',
    'zllgamma': '$Z(\\rightarrow\ell\ell)\gamma$',
    'znunugamma': '$Z(\\rightarrow\\nu\\nu)\gamma$',
    'photonjet': '$\\gamma$ + jets',
    'vqqgamma': 'V($\\to$ qq)$+\\gamma$',
    'group_zllgamma_znunugamma': '$Z\gamma$',
    'group_diphoton_vgammagamma': '$\gamma\gamma / W\gamma\gamma / Z\gamma\gamma$',
    'diphoton': '$\gamma\gamma / W\gamma\gamma / Z\gamma\gamma$',

    'efake': '$e\\rightarrow\\gamma$ fakes',
    'jfake': '$j\\rightarrow\\gamma$ fakes',
    }

def latexfitresults(filename, region_list, sample_list):


    f = ROOT.TFile.Open(filename)
    w = f.Get('w')

    doAsym = True

    if w is None:
        print "ERROR : Cannot open workspace : w"
        sys.exit(1)

    resultAfterFit = w.obj('RooExpandedFitResult_afterFit')
    if resultAfterFit is None:
        print("ERROR : Cannot open fit result after fit RooExpandedFitResult_afterFit")
        sys.exit(1)

    resultBeforeFit = w.obj('RooExpandedFitResult_beforeFit')
    if resultBeforeFit is None:
        print("ERROR : Cannot open fit result before fit RooExpandedFitResult_beforeFit")
        sys.exit(1)

    # pick up dataset from workspace
    data_set = w.data('obsData')
      
    # pick up channel category (RooCategory) from workspace
    regionCat = w.obj("channelCat")

    # find full (long) name list of regions (i.e. short=SR3J, long=SR3J_meffInc30_JVF25pt50)
    regionFullNameList = [ Util.GetFullRegionName(regionCat, region) for region in region_list ]

    # load afterFit workspace snapshot (=set all parameters to values after fit)
    snapshot =  'snapshot_paramsVals_RooExpandedFitResult_afterFit'
    w.loadSnapshot(snapshot)

    if not w.loadSnapshot(snapshot):
        print "ERROR : Cannot load snapshot : ", snapshot
        sys.exit(1)

    # define set, for all names/yields to be saved in
    tablenumbers = dict()

    tablenumbers['names'] = region_list

    # make a list of channelCat calls for every region
    regionCatList = [ 'channelCat==channelCat::' + region.Data() for region in regionFullNameList ]
  
    # retrieve number of observed (=data) events per region
    regionDatasetList = [data_set.reduce(regioncat) for regioncat in regionCatList]
    for index, data in enumerate(regionDatasetList):
        data.SetName("data_" + region_list[index])
        data.SetTitle("data_" + region_list[index])
    
    nobs_regionList = [ data.sumEntries() for data in regionDatasetList ]

    tablenumbers['nobs'] = nobs_regionList


    # FROM HERE ON OUT WE CALCULATE THE FITTED NUMBER OF EVENTS __AFTER__ THE FIT
    
    #get a list of pdf's and variables per region
    pdfinRegionList = [ Util.GetRegionPdf(w, region) for region in region_list ]
    varinRegionList = [ Util.GetRegionVar(w, region) for region in region_list ] 
  
    varNbinsInRegionList      = [] 
    varBinLowInRegionList     = []  
    varBinHighInRegionList    = [] 
    rangeNameBinsInRegionList = [] 
  
    #  get a list of RooRealSumPdf per region (RooRealSumPdf is the top-pdf per region containing all samples)
    rrspdfinRegionList = []
    for index, pdf in enumerate(pdfinRegionList):
        if not pdf:
            print "WARNING: pdf is NULL for index {0}".format(index)
            continue

        prodList = pdf.pdfList()
        foundRRS = 0

        for idx in range(prodList.getSize()):
            if prodList[idx].InheritsFrom("RooRealSumPdf"):
                rrspdfInt =  prodList[idx].createIntegral(ROOT.RooArgSet(varinRegionList[index]))
                rrspdfinRegionList.append(rrspdfInt)
                foundRRS += 1

        if foundRRS > 1 or foundRRS == 0:
            print " \n\n WARNING: ", pdf.GetName(), " has ", foundRRS, " instances of RooRealSumPdf"
            print pdf.GetName(), " component list:", prodList.Print("v")
    
    # calculate total pdf number of fitted events and error
    nFittedInRegionList      = [ pdf.getVal() for index, pdf in enumerate(rrspdfinRegionList)]
    pdfFittedErrInRegionList = [ Util.GetPropagatedError(pdf, resultAfterFit, doAsym) for pdf in rrspdfinRegionList]

    tablenumbers['TOTAL_FITTED_bkg_events']     = nFittedInRegionList
    tablenumbers['TOTAL_FITTED_bkg_events_err'] = pdfFittedErrInRegionList
 
    # calculate the fitted number of events and propagated error for each requested sample, by splitting off each sample pdf
    for isam, sample in enumerate(sample_list):

        sampleName = getName(sample)

        nSampleInRegionVal = []
        nSampleInRegionError = []
        sampleInAllRegions = ROOT.RooArgSet()
        
        for ireg, region in enumerate(region_list):
            sampleInRegion = getPdfInRegions(w, sample, region)
            sampleInRegionVal = 0.
            sampleInRegionError = 0.

            try: 
                sampleInRegionVal = sampleInRegion.getVal()
                sampleInRegionError = Util.GetPropagatedError(sampleInRegion, resultAfterFit, doAsym) 
                sampleInAllRegions.add(sampleInRegion)
            except:
                print " \n YieldsTable.py: WARNING: sample =", sampleName, " non-existent (empty) in region =", region, "\n"

            nSampleInRegionVal.append(sampleInRegionVal)
            nSampleInRegionError.append(sampleInRegionError)
      
        tablenumbers['Fitted_events_'+sampleName]   = nSampleInRegionVal
        tablenumbers['Fitted_err_'+sampleName]   = nSampleInRegionError


  
    # FROM HERE ON OUT WE CALCULATE THE EXPECTED NUMBER OF EVENTS __BEFORRE__ THE FIT
    
    #load beforeFit workspace snapshot (=set all parameters to values before fit)
    w.loadSnapshot('snapshot_paramsVals_RooExpandedFitResult_beforeFit')

    # check if any of the initial scaling factors is != 1
    _result = w.obj('RooExpandedFitResult_beforeFit')
    _muFacs = _result.floatParsFinal()

    for i in xrange(len(_muFacs)):

        if "mu_" in _muFacs[i].GetName() and _muFacs[i].getVal() != 1.0:
            print  " \n WARNING: scaling factor %s != 1.0 (%g) expected MC yield WILL BE WRONG!" % (_muFacs[i].GetName(), _muFacs[i].getVal())
  
    # get a list of pdf's and variables per region
    pdfinRegionList = [ Util.GetRegionPdf(w, region)  for region in region_list]
    varinRegionList =  [ Util.GetRegionVar(w, region) for region in region_list]


    # get a list of RooRealSumPdf per region (RooRealSumPdf is the top-pdf per region containing all samples)
    rrspdfinRegionList = []
    for index,pdf in enumerate(pdfinRegionList):
        if not pdf: 
            print "WARNING: pdf is NULL for index {0}".format(index)
            continue
        prodList = pdf.pdfList()
        foundRRS = 0
        for idx in xrange(prodList.getSize()):
            if prodList[idx].InheritsFrom("RooRealSumPdf"):
                rrspdfInt =  prodList[idx].createIntegral(ROOT.RooArgSet(varinRegionList[index]))
                rrspdfinRegionList.append(rrspdfInt)
                foundRRS += 1

        if foundRRS >1 or foundRRS==0:
            print " \n\n WARNING: ", pdf.GetName(), " has ", foundRRS, " instances of RooRealSumPdf"
            print pdf.GetName(), " component list:", prodList.Print("v")

    # calculate total pdf number of expected events and error
    nExpInRegionList =  [ pdf.getVal() for index, pdf in enumerate(rrspdfinRegionList)]
    pdfExpErrInRegionList = [ Util.GetPropagatedError(pdf, resultBeforeFit, doAsym)  for pdf in rrspdfinRegionList]
  
    tablenumbers['TOTAL_MC_EXP_BKG_events'] =  nExpInRegionList
    tablenumbers['TOTAL_MC_EXP_BKG_err']    =  pdfExpErrInRegionList
  
    # calculate the fitted number of events and propagated error for each requested sample, by splitting off each sample pdf
    for isam, sample in enumerate(sample_list):
      
        sampleName = getName(sample)

        nMCSampleInRegionVal = []
        nMCSampleInRegionError = []
        MCSampleInAllRegions = ROOT.RooArgSet()

        for ireg, region in enumerate(region_list):
            MCSampleInRegion = getPdfInRegions(w,sample,region)
            MCSampleInRegionVal = 0.
            MCSampleInRegionError = 0.

            try:
                MCSampleInRegionVal = MCSampleInRegion.getVal()
                MCSampleInRegionError = Util.GetPropagatedError(MCSampleInRegion, resultBeforeFit, doAsym) 
                MCSampleInAllRegions.add(MCSampleInRegion)
            except:
                print " \n WARNING: sample=", sampleName, " non-existent (empty) in region=",region
                
            nMCSampleInRegionVal.append(MCSampleInRegionVal)
            nMCSampleInRegionError.append(MCSampleInRegionError)

        tablenumbers['MC_exp_events_'+sampleName] = nMCSampleInRegionVal
        tablenumbers['MC_exp_err_'+sampleName]    = nMCSampleInRegionError

    # sort the tablenumbers set
    map_listofkeys = tablenumbers.keys()
    map_listofkeys.sort()

    f.Close()
  
    return tablenumbers


def get_fit_results(workspace, samples, channels):

    samples_list = cmdStringToListOfLists(samples)
    regions_list = [ '%s_cuts' % r for r in channels.split(",") ]

    m = latexfitresults(workspace, regions_list, samples_list)

    return m


def yieldstable(workspace, samples, channels, output_name, table_name='', show_before_fit=False, unblind=True, show_cr_info=False, cr_dict={}):

    if show_cr_info:
        show_before_fit = True
        normalization_factors = get_normalization_factors(workspace)

    samples_list = cmdStringToListOfLists(samples)

    regions_list = [ '%s_cuts' % r for r in channels.split(",") ]

    # call the function to calculate the numbers, or take numbers from pickle file  
    if workspace.endswith(".pickle"):
        print "Reading from pickle file"
        f = open(workspace, 'r')
        m = pickle.load(f)
        f.close()
    else:
        #m = YieldsTable.latexfitresults(workspace, regions_list, samples_list, 'obsData') 
        m = latexfitresults(workspace, regions_list, samples_list)

        with open(output_name.replace('.tex',  '.pickle'), 'w') as f:
            pickle.dump(m, f)


    regions_names = [ region.replace("_cuts", "").replace('_','\_') for region in m['names'] ]

    field_names = [table_name,] + regions_names
    align = ['l',] + [ 'r' for i in regions_names ]

    samples_list_decoded = []
    for isam, sample in enumerate(samples_list):
        sampleName = getName(sample)
        samples_list_decoded.append(sampleName)

    samples_list = samples_list_decoded

    tablel = LatexTable(field_names, align=align, env=True)

    #  number of observed events
    if unblind:
        row = ['Observed events',] + [ '%d' % n for n in m['nobs'] ]
    else:
        row = ['Observed events',] + [ '-' for n in m['nobs'] ]

    tablel.add_row(row)
    tablel.add_line()

    # Total fitted (after fit) number of events
    # if the N_fit - N_error extends below 0, make the error physical, meaning extend to 0
    rowl = ['Expected SM events', ]

    for index, n in enumerate(m['TOTAL_FITTED_bkg_events']):

        if (n - m['TOTAL_FITTED_bkg_events_err'][index]) > 0. :
            rowl.append('$%.2f \pm %.2f$' % (n, m['TOTAL_FITTED_bkg_events_err'][index]))
        else:
            rowl.append('$%.2f_{-%.2f}^{+%.2f}$' % (n, n, m['TOTAL_FITTED_bkg_events_err'][index]))

    tablel.add_row(rowl)
    tablel.add_line()

    map_listofkeys = m.keys()

    # After fit number of events per sample (if the N_fit-N_error extends below 0, make the error physical, meaning extend to 0)
    for sample in samples_list:
        for name in map_listofkeys:

            rowl = []

            if not "Fitted_events_" in name: 
                continue

            sample_name = name.replace("Fitted_events_", "")
            if sample_name != sample:
                continue
        
            rowl.append('%s' % labels_latex_dict.get(sample_name, sample_name).replace('_', '\_'))

            for index, n in enumerate(m[name]):

                if ((n - m['Fitted_err_'+sample][index]) > 0.) or not abs(n) > 0.00001:
                    rowl.append('$%.2f \\pm %.2f$' % (n, m['Fitted_err_'+sample][index]))
                else:
                    rowl.append('$%.2f_{-%.2f}^{+%.2f}$' % (n, n, m['Fitted_err_'+sample][index]))

            tablel.add_row(rowl)
  
    tablel.add_line()

    # Total expected (before fit) number of events
    if show_before_fit:

        # if the N_fit - N_error extends below 0, make the error physical, meaning extend to 0
        rowl = ['Before fit SM events',]

        total_before = {}
        purity_before = {}
            
        for index, n in enumerate(m['TOTAL_MC_EXP_BKG_events']):

            reg_name = regions_names[index]

            if cr_dict and reg_name in cr_dict:
                total_before[reg_name] = n

            rowl.append('$%.2f$' % n)

        tablel.add_row(rowl)
        tablel.add_line()

        map_listofkeys = m.keys()

        # Expected number of events per sample (if the N_fit - N_error extends below 0, make the error physical, meaning extend to 0)
        for sample in samples_list:

            for name in map_listofkeys:

                rowl = []

                if "MC_exp_events_" in name and sample in name:

                    sample_name = name.replace("MC_exp_events_","")

                    if sample_name != sample:
                        continue
              
                    rowl.append('Before fit %s' % labels_latex_dict.get(sample_name, sample_name).replace('_', '\_'))

                    for index, n in enumerate(m[name]):
                        reg_name = regions_names[index]
                        if cr_dict and reg_name in cr_dict and sample == cr_dict[reg_name]:
                            purity_before[reg_name] = n

                        rowl.append('$%.2f$' % n)

                    tablel.add_row(rowl)
  
        tablel.add_line()

    if show_cr_info and normalization_factors is not None:

        tablel.add_row(['' for i in range(len(regions_names)+1)])
        tablel.add_line()

        # purity
        rowl = ['Background purity',]

        for region in regions_names:

            try:
                purity = int(round(purity_before[region]/total_before[region] * 100.))
                rowl.append('$%i\%%$' % purity)
            except:
                rowl.append('-')

            
        tablel.add_row(rowl)
        tablel.add_line()

        # normalization
        rowl = ['Normalization factor ($\mu$)',]
        for region in regions_names:
            try:
                rowl.append('$%.2f \pm %.2f$' % normalization_factors[region])
            except:
                rowl.append('-')

        tablel.add_row(rowl)
        tablel.add_line()

    tablel.save_tex(output_name)



# def merge_tables(table_srl, table_srh, output_name):

#     if not os.path.isfile(table_srl) or not os.path.isfile(table_srh):
#         return None
    
#     file1 = open(table_srl).read().split('\n')
#     file2 = open(table_srh).read().split('\n')

#     ncols = 0
#     new_lines = []
#     for line1, line2 in zip(file1, file2):

#         sline1 = [ i.replace('\\\\','') for i in line1.split('&') ]
#         sline2 = [ i.replace('\\\\','') for i in line2.split('&') ]

#         if len(sline1) == 1:
#             new_line = sline1[0]

#             if 'hline' in new_line:
#                 new_lines.append(new_line)

#             continue

#         if not ncols:
#             ncols = len(sline1) - 1

#         new_list = sline1 + sline2[1:]

#         # if 'for' in new_list[0]:
#         #     new_list[0] = ''

#         new_line = ' & '.join(new_list)

#         if not 'hline' in new_line and not 'begin' in new_line and not 'end' in new_line:
#             new_line += '\\\\'

#         new_lines.append(new_line)


#     with open(output_name, 'w') as f:
        
#         s = r'\begin{{tabular}}{{l|{RCOLS}|{RCOLS}}}\hline & \multicolumn{{{NCOLS}}}{{c|}}{{\SRL}} & \multicolumn{{{NCOLS}}}{{c}}{{\SRH}}\\'.format(RCOLS='r'*ncols, NCOLS=str(ncols))

#         f.write(s)
#         f.write('\n'.join(new_lines))
#         f.write('\end{tabular}\n')


#     # merge HTML tables
#     table1 = from_html_one(open(table_srl.replace('.tex', '.html')).read())
#     table2 = from_html_one(open(table_srh.replace('.tex', '.html')).read())

#     field_names  = [ '%s (L)' % fn for fn in table1._field_names[1:] ]
#     field_names += [ '%s (H)' % fn for fn in table2._field_names[1:] ]

#     table3 = PrettyTable(['',] + field_names, align={'': 'left'})

#     for row1, row2  in zip(table1._rows, table2._rows):

#         if row1[0] == row2[0]:
#             table3.add_row(row1 + row2[1:])
#         else:
#             raise

#     with open(output_name.replace('.tex', '.html'), 'w+') as f:
#         f.write(table3.get_html_string())

    



