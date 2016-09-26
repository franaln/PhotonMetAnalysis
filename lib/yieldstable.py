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
import YieldsTable
from cmdLineUtils import getPdfInRegions, getName, getPdfInRegionsWithRangeName
from fitutils import get_normalization_factors

labels_latex_dict = {
    'wgamma': '$W + \gamma$',
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
    'group_zllgamma_znunugamma': '$Z + \gamma$',
    'group_diphoton_vgammagamma': '$\gamma\gamma / W\gamma\gamma / Z\gamma\gamma$',

    'efake15': '$e\\rightarrow\\gamma$ fakes',
    'jfake15': '$j\\rightarrow\\gamma$ fakes',

    'efake16': '$e\\rightarrow\\gamma$ fakes',
    'jfake16': '$j\\rightarrow\\gamma$ fakes',

    'efake': '$e\\rightarrow\\gamma$ fakes',
    'jfake': '$j\\rightarrow\\gamma$ fakes',
    }

labels_html_dict = {
    'wgamma': 'W gamma',
    'ttbarg': 'tt gamma',
    'topgamma': 't gamma',
    'diboson': 'Dibosons',
    'wjets': 'W + jets',
    'ttbar': 'tt',
    'zjets': 'Z + jets',
    'zllgamma': 'Z(ll) + gamma',
    'znunugamma': 'Z(nunu) + gamma',
    'photonjet': 'gamma + jet',
    'vqqgamma': 'V(qq) gamma',
    'group_zllgamma_znunugamma': 'Z gamma',
    'group_diphoton_vgammagamma': 'diphoton',
    'efake': 'e fakes',
    'jfake': 'j fakes',
    }

def latexfitresults(filename, region_list, sample_list):

    f = ROOT.TFile.Open(filename)
    w = f.Get('w')

    if w is None:
        print "ERROR : Cannot open workspace : w"
        sys.exit(1)

    resultAfterFit = w.obj('RooExpandedFitResult_afterFit')
    if resultAfterFit is None:
        print "ERROR : Cannot open fit result after fit RooExpandedFitResult_afterFit"
        sys.exit(1)

    resultBeforeFit = w.obj('RooExpandedFitResult_beforeFit')
    if resultBeforeFit is None:
        print "ERROR : Cannot open fit result before fit RooExpandedFitResult_beforeFit"
        sys.exit(1)

    # pick up dataset from workspace
    data_set = w.data('obsData')
      
    # pick up channel category (RooCategory) from workspace
    regionCat = w.obj("channelCat")
    # if not blinded:
    #   data_set.table(regionCat).Print("v")

    # find full (long) name list of regions (i.e. short=SR3J, long=SR3J_meffInc30_JVF25pt50)
    regionFullNameList = [ Util.GetFullRegionName(regionCat, region) for region in region_list ]

    # load afterFit workspace snapshot (=set all parameters to values after fit)
    snapshot =  'snapshot_paramsVals_RooExpandedFitResult_afterFit'
    w.loadSnapshot(snapshot)

    if not w.loadSnapshot(snapshot):
        print "ERROR : Cannot load snapshot : ", snapshot
        sys.exit(1)

    # define set, for all names/yields to be saved in
    tablenumbers = {}

    tablenumbers['names'] = region_list

    # make a list of channelCat calls for every region
    regionCatList = [ 'channelCat==channelCat::' + region.Data() for region in regionFullNameList]
  
    # retrieve number of observed (=data) events per region
    regionDatasetList = [data_set.reduce(regioncat) for regioncat in regionCatList]
    for index, data in enumerate(regionDatasetList):
        data.SetName("data_" + region_list[index])
        data.SetTitle("data_" + region_list[index])
    
    nobs_regionList = [ data.sumEntries() for data in regionDatasetList]

    tablenumbers['nobs'] = nobs_regionList


    # FROM HERE ON OUT WE CALCULATE THE FITTED NUMBER OF EVENTS __AFTER__ THE FIT
    
    #get a list of pdf's and variables per region
    pdfinRegionList = [ Util.GetRegionPdf(w, region)  for region in region_list]
    varinRegionList =  [ Util.GetRegionVar(w, region) for region in region_list]
  
    # if splitBins=True get the list of Nbins, binMax and binMin; make a list of new region names for each bin
    varNbinsInRegionList =  [] 
    varBinLowInRegionList = []  
    varBinHighInRegionList =  [] 
    rangeNameBinsInRegionList = [] 
  
    # if blinded=True, set all numbers of observed events to -1
    # if blinded: 
    #     for index, nobs in enumerate(nobs_regionListWithBins):
    #         nobs_regionListWithBins[index] = -1
    # tablenumbers['nobs'] = nobs_regionListWithBins


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
        if foundRRS >1 or foundRRS==0:
            print " \n\n WARNING: ", pdf.GetName(), " has ", foundRRS, " instances of RooRealSumPdf"
            print pdf.GetName(), " component list:", prodList.Print("v")
    
    # calculate total pdf number of fitted events and error
    nFittedInRegionList =  [ pdf.getVal() for index, pdf in enumerate(rrspdfinRegionList)]
    pdfFittedErrInRegionList = [ Util.GetPropagatedError(pdf, resultAfterFit, True) for pdf in rrspdfinRegionList]

    tablenumbers['TOTAL_FITTED_bkg_events']        =  nFittedInRegionList
    tablenumbers['TOTAL_FITTED_bkg_events_err']    =  pdfFittedErrInRegionList
 
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

            try: ##if sampleInRegion is not None:
                sampleInRegionVal = sampleInRegion.getVal()
                sampleInRegionError = Util.GetPropagatedError(sampleInRegion, resultAfterFit, True) 
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
        for idx in range(prodList.getSize()):
            if prodList[idx].InheritsFrom("RooRealSumPdf"):
                rrspdfInt =  prodList[idx].createIntegral(ROOT.RooArgSet(varinRegionList[index]))
                rrspdfinRegionList.append(rrspdfInt)
                foundRRS += 1

        if foundRRS >1 or foundRRS==0:
            print " \n\n WARNING: ", pdf.GetName(), " has ", foundRRS, " instances of RooRealSumPdf"
            print pdf.GetName(), " component list:", prodList.Print("v")

    # calculate total pdf number of expected events and error
    nExpInRegionList =  [ pdf.getVal() for index, pdf in enumerate(rrspdfinRegionList)]
    pdfExpErrInRegionList = [ Util.GetPropagatedError(pdf, resultBeforeFit, True)  for pdf in rrspdfinRegionList]
  
    tablenumbers['TOTAL_MC_EXP_BKG_events']    =  nExpInRegionList
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
                MCSampleInRegionError = Util.GetPropagatedError(MCSampleInRegion, resultBeforeFit, True) 
                MCSampleInAllRegions.add(MCSampleInRegion)
            except:
                print " \n WARNING: sample=", sampleName, " non-existent (empty) in region=",region
                
            nMCSampleInRegionVal.append(MCSampleInRegionVal)
            nMCSampleInRegionError.append(MCSampleInRegionError)

        tablenumbers['MC_exp_events_'+sampleName] = nMCSampleInRegionVal
        tablenumbers['MC_exp_err_'+sampleName] = nMCSampleInRegionError

    # sort the tablenumbers set
    map_listofkeys = tablenumbers.keys()
    map_listofkeys.sort()
  
    return tablenumbers


def yieldstable(workspace, samples, channels, output_name, table_name, is_cr=False, show_before_fit=False, unblind=True):

    if is_cr:
        show_before_fit=True
        normalization_factors = get_normalization_factors(workspace)

    #sample_str = samples.replace(",","_")
    from cmdLineUtils import cmdStringToListOfLists
    samples_list = cmdStringToListOfLists(samples)

    regions_list = [ '%s_cuts' % r for r in channels.split(",") ]
    #samples_list = samples.split(",")

    # call the function to calculate the numbers, or take numbers from pickle file  
    if workspace.endswith(".pickle"):
        print "READING PICKLE FILE"
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
    tablep = PrettyTable(field_names, align=align)

    #  number of observed events
    if unblind:
        row = ['Observed events',] + [ '%d' % n for n in m['nobs'] ]
    else:
        row = ['Observed events',] + [ '-' for n in m['nobs'] ]

    tablel.add_row(row)
    tablep.add_row(row)
    tablel.add_line()
    tablep.add_line()

    #print the total fitted (after fit) number of events
    # if the N_fit - N_error extends below 0, make the error physical , meaning extend to 0
    rowl = ['Expected SM events', ]
    rowp = ['Expected SM events', ]

    for index, n in enumerate(m['TOTAL_FITTED_bkg_events']):

        if (n - m['TOTAL_FITTED_bkg_events_err'][index]) > 0. :
            rowl.append('$%.2f \pm %.2f$' % (n, m['TOTAL_FITTED_bkg_events_err'][index]))
            rowp.append('%.2f &plusmn %.2f' % (n, m['TOTAL_FITTED_bkg_events_err'][index]))

        else:
            print "WARNING:   negative symmetric error after fit extends below 0. for total bkg pdf:  will print asymmetric error w/ truncated negative error reaching to 0."
            rowl.append('$%.2f_{-%.2f}^{+%.2f}$' % (n, n, m['TOTAL_FITTED_bkg_events_err'][index]))
            rowp.append('%.2f -%.2f +%.2f' % (n, n, m['TOTAL_FITTED_bkg_events_err'][index]))

    tablel.add_row(rowl)
    tablel.add_line()
    tablep.add_row(rowp)
    tablep.add_line()

    map_listofkeys = m.keys()

    # print fitted number of events per sample
    # if the N_fit - N_error extends below 0, make the error physical , meaning extend to 0
    for sample in samples_list:
        for name in map_listofkeys:

            rowl = []
            rowp = []

            if not "Fitted_events_" in name: 
                continue

            sample_name = name.replace("Fitted_events_", "")
            if sample_name != sample:
                continue
        
            rowl.append('%s' % labels_latex_dict.get(sample_name, sample_name).replace('_', '\_'))
            rowp.append('%s' % labels_html_dict.get(sample_name, sample_name))

            for index, n in enumerate(m[name]):

                if ((n - m['Fitted_err_'+sample][index]) > 0.) or not abs(n) > 0.00001:
                    rowl.append('$%.2f \\pm %.2f$' % (n, m['Fitted_err_'+sample][index]))
                    rowp.append('%.2f &plusmn %.2f' % (n, m['Fitted_err_'+sample][index]))

                else:
                    print "WARNING:   negative symmetric error after fit extends below 0. for sample", sample, "    will print asymmetric error w/ truncated negative error reaching to 0."
                    rowl.append('$%.2f_{-%.2f}^{+%.2f}$' % (n, n, m['Fitted_err_'+sample][index]))
                    rowp.append('%.2f -%.2f +%.2f' % (n, n, m['Fitted_err_'+sample][index]))

            tablel.add_row(rowl)
            tablep.add_row(rowp)
  
    tablel.add_line()
    tablep.add_line()

    # print the total expected (before fit) number of events
    if show_before_fit:

        # if the N_fit - N_error extends below 0, make the error physical , meaning extend to 0
        rowl = ['Before SM events',]
        rowp = ['(before fit) SM events',]

        total_before = []
        purity_before = []
            
        for index, n in enumerate(m['TOTAL_MC_EXP_BKG_events']):

            if regions_names[index].startswith('CR'):
                total_before.append(n)

            rowl.append('$%.2f$' % n)
            rowp.append('%.2f' % n)

        tablel.add_row(rowl)
        tablel.add_line()

        tablep.add_row(rowp)
        tablep.add_line()

        map_listofkeys = m.keys()

        # print expected number of events per sample
        # if the N_fit - N_error extends below 0, make the error physical , meaning extend to 0
        for sample in samples_list:

            for name in map_listofkeys:

                rowl = []
                rowp = []

                if "MC_exp_events_" in name and sample in name:

                    sample_name = name.replace("MC_exp_events_","")

                    if sample_name != sample:
                        continue
              
                    rowl.append('(before fit) %s' % labels_latex_dict.get(sample_name, sample_name).replace('_', '\_'))
                    rowp.append('(before fit) %s' % labels_html_dict.get(sample_name, sample_name))

                    for index, n in enumerate(m[name]):
                    
                        if regions_names[index] == 'CRQ' and sample == 'photonjet':
                            purity_before.append(n)
                        if regions_names[index] == 'CRW' and sample == 'wgamma':
                            purity_before.append(n)
                        if regions_names[index] == 'CRT' and sample == 'ttbarg':
                            purity_before.append(n)

                        rowl.append('$%.2f$' % n)
                        rowp.append('%.2f' % n)

                    tablel.add_row(rowl)
                    tablep.add_row(rowp)
  
        tablel.add_line()
        tablep.add_line()

    if show_before_fit and all([r.startswith('CR') for r in regions_names]) and normalization_factors is not None:

        tablel.add_row(['', '', '', ''])
        tablel.add_line()

        tablep.add_row(['', '', '', ''])
        tablep.add_line()

        # purity
        rowl = ['Purity',]
        rowp = ['Purity',]

        for index, region in enumerate(regions_names):

            purity = int(purity_before[index]/total_before[index] * 100.)

            rowl.append('$%i\%%$' % purity)
            rowp.append('%i%%' % purity)
            
        tablel.add_row(rowl)
        tablel.add_line()

        tablep.add_row(rowp)
        tablep.add_line()

        # normalization
        rowl = ['Normalization factor ($\mu$)',]
        rowp = ['Normalization factor (mu)',]
        for region in regions_names:
            rowl.append('$%.2f \pm %.2f$' % normalization_factors[region])
            rowp.append('%.2f &plusmn %.2f' % normalization_factors[region])

        tablel.add_row(rowl)
        tablel.add_line()
        tablep.add_row(rowp)
        tablep.add_line()


    tablel.save_tex(output_name)

    with open(output_name.replace('.tex', '.html'), 'w+') as f:
        f.write(tablep.get_html_string())



def merge_tables(table_srl, table_srh, output_name):

    if not os.path.isfile(table_srl) or not os.path.isfile(table_srh):
        return None

    
    file1 = open(table_srl).read().split('\n')
    file2 = open(table_srh).read().split('\n')

    ncols = 0
    new_lines = []
    for line1, line2 in zip(file1, file2):

        sline1 = [ i.replace('\\\\','') for i in line1.split('&') ]
        sline2 = [ i.replace('\\\\','') for i in line2.split('&') ]

        if len(sline1) == 1:
            new_line = sline1[0]

            if 'hline' in new_line:
                new_lines.append(new_line)

            continue

        if not ncols:
            ncols = len(sline1) - 1

        new_list = sline1 + sline2[1:]

        if 'for' in new_list[0]:
            new_list[0] = ''

        new_line = ' & '.join(new_list)

        if not 'hline' in new_line and not 'begin' in new_line and not 'end' in new_line:
            new_line += '\\\\'

        new_lines.append(new_line)


    with open(output_name, 'w') as f:
        
        s = r'\begin{{tabular}}{{l|{RCOLS}|{RCOLS}}}\hline & \multicolumn{{{NCOLS}}}{{c|}}{{\SRL}} & \multicolumn{{{NCOLS}}}{{c}}{{\SRH}}\\'.format(RCOLS='r'*ncols, NCOLS=str(ncols))

        f.write(s)
        f.write('\n'.join(new_lines))
        f.write('\end{tabular}\n')


    # merge HTML tables
    table1 = from_html_one(open(table_srl.replace('.tex', '.html')).read())
    table2 = from_html_one(open(table_srh.replace('.tex', '.html')).read())

    field_names  = [ '%s (L)' % fn for fn in table1._field_names[1:] ]
    field_names += [ '%s (H)' % fn for fn in table2._field_names[1:] ]

    table3 = PrettyTable(['',] + field_names, align={'': 'left'})

    for row1, row2  in zip(table1._rows, table2._rows):

        if row1[0] == row2[0]:
            table3.add_row(row1 + row2[1:])
        else:
            raise

    with open(output_name.replace('.tex', '.html'), 'w+') as f:
        f.write(table3.get_html_string())

    



