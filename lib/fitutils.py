import os
import ROOT

def get_normalization_factors(workspace):

    mu_dict = dict()

    # get mus from workspace
    if not os.path.isfile(workspace):
        print 'Workspace does not exist'
        return mu_dict

    rf = ROOT.TFile(workspace)

    w = rf.Get('w')

    for name in ('q', 'w', 't'):
        mu = w.var('mu_'+name)
        mu_dict['CR%s' % name.upper()] = (mu.getValV(), mu.getError())

    rf.Close()

    return mu_dict
