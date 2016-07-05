import ROOT

chain = ROOT.TChain('baseline')

#chain.Add('/disk/falonso/base/data15_13TeV.00283780.physics_Main.base.v1_output.root')
#chain.Add('/disk/falonso/base/data15_13TeV.00283780.physics_Main.base.v4_output.root')

chain.Add('~/work/Susy/Run2/PhotonMetNtuple/output_test/data-output/data.root')
# chain.Add('~/work/Susy/Run2/PhotonMetNtuple_20.1/output_test/data-output/data.root')

ROOT.gDirectory.Delete('list*')
chain.SetEntryList(0)

total_events = chain.GetEntries()
chain.Draw('>>list', 'event == 1774431567', 'entrylist')
entry_list = ROOT.gDirectory.Get('list')

chain.SetEntryList(entry_list)
selected_events = entry_list.GetN()

if selected_events <= 0:
    print 'No events passing this selection... '


def print_obj(pt, eta, phi, baseline, passor, signal, isol=None):
    if isol is None:
        print '(pt, eta, phi) = (%7.2f, %7.2f, %7.2f), baseline=%s, passOR=%s, signal=%s' % (pt, eta, phi, baseline, passor, signal)
    else:
        print '(pt, eta, phi) = (%7.2f, %7.2f, %7.2f), baseline=%s, passOR=%s, isol=%s, signal=%s' % (pt, eta, phi, baseline, passor, isol, signal)

for event in xrange(selected_events):
    
    n = entry_list.Next()
    chain.GetEntry(n)


    ph_baseline_n = 0
    ph_passOR_n = 0
    ph_isol_n = 0
    ph_signal_n = 0
    for i in xrange(chain.ph_n):
        if chain.ph_baseline[i] == 1:
            ph_baseline_n += 1
        if chain.ph_passOR[i] == 1:
            ph_passOR_n += 1
        if chain.ph_isol[i] == 1:
            ph_isol_n += 1
        if chain.ph_signal[i] == 1:
            ph_signal_n += 1

    el_baseline_n = 0
    el_passOR_n = 0
    el_isol_n = 0
    el_signal_n = 0
    for i in xrange(chain.el_n):
        if chain.el_baseline[i] == 1:
            el_baseline_n += 1
        if chain.el_passOR[i] == 1:
            el_passOR_n += 1
        if chain.el_isol[i] == 1:
            el_isol_n += 1
        if chain.el_signal[i] == 1:
            el_signal_n += 1

    mu_baseline_n = 0
    mu_passOR_n = 0
    mu_isol_n = 0
    mu_signal_n = 0
    for i in xrange(chain.mu_n):
        if chain.mu_baseline[i] == 1:
            mu_baseline_n += 1
        if chain.mu_passOR[i] == 1:
            mu_passOR_n += 1
        if chain.mu_isol[i] == 1:
            mu_isol_n += 1
        if chain.mu_signal[i] == 1:
            mu_signal_n += 1

    jet_baseline_n = 0
    jet_passOR_n = 0
    jet_signal_n = 0
    for i in xrange(chain.jet_n):
        if chain.jet_baseline[i] == 1:
            jet_baseline_n += 1
        if chain.jet_passOR[i] == 1:
            jet_passOR_n += 1
        if chain.jet_signal[i] == 1:
            jet_signal_n += 1


    # photons
    print '# photons (all: %i, baseline: %i, passOR: %i, isol: %i, signal: %i)' % (chain.ph_n, ph_baseline_n, ph_passOR_n, ph_isol_n, ph_signal_n)
    
    for i in xrange(chain.ph_n):
        print_obj(chain.ph_pt[i], chain.ph_etas2[i], chain.ph_phi[i], chain.ph_baseline[i], chain.ph_passOR[i], chain.ph_signal[i], chain.ph_isol[i])


    # electrons
    print '# electrons (all: %i, baseline: %i, passOR: %i, isol: %i, signal: %i)' % (chain.el_n, el_baseline_n, el_passOR_n, el_isol_n, el_signal_n)
    
    for i in xrange(chain.el_n):
        print_obj(chain.el_pt[i], chain.el_etas2[i], chain.el_phi[i], chain.el_baseline[i], chain.el_passOR[i], chain.el_signal[i], chain.el_isol[i])


    # muons
    print '# muons (all: %i, baseline: %i, passOR: %i, isol: %i, signal: %i)' % (chain.mu_n, mu_baseline_n, mu_passOR_n, mu_isol_n, mu_signal_n)
    
    for i in xrange(chain.mu_n):
        print_obj(chain.mu_pt[i], chain.mu_eta[i], chain.mu_phi[i], chain.mu_baseline[i], chain.mu_passOR[i], chain.mu_signal[i], chain.mu_isol[i])


    # jets
    print '# jets (all: %i, baseline: %i, passOR: %i, signal: %i)' % (chain.jet_n, jet_baseline_n, jet_passOR_n, jet_signal_n)
    
    for i in xrange(chain.jet_n):
        print_obj(chain.jet_pt[i], chain.jet_eta[i], chain.jet_phi[i], chain.jet_baseline[i], chain.jet_passOR[i], chain.jet_signal[i])


    break
