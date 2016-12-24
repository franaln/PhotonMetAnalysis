# Default options
use_purw = False

# Mini version
versions = ['48', '47', '41'] #'45', '41',] # keep v41 for signal

ptags = ['2889', '2840', '2824', '2769', '2689', '2688', '2666', '2667', ]

# Luminosity (OffLumi-13TeV-005)
lumi_data15 = 3212.96  # All
#lumi_data16 = 10064.30 # DS2 (Runs 297730-303560)
#lumi_data16 = 24799.90 # DS3 (Runs 297730-308084)
lumi_data16 = 33257.20 # All 2016

lumi_data = lumi_data15 + lumi_data16

# Signal
from signalgrid import grid_m3_mu
signal = [ 'GGM_M3_mu_%i_%i' % (m3, mu) for (m3, mu) in grid_m3_mu.keys() ]

# Backgrounds
backgrounds_mc = [
    'photonjet',
    'wgamma',
    'zllgamma', 
    'znunugamma',
    'ttbarg',
    'diphoton',
    'vgammagamma',
    # 'vqqgamma',
    ]

backgrounds_dd = [
    'efake',
    'jfake',
    ]

backgrounds_mc_alt = [
    'ttbar', 
    'zjets', 
    'wjets',
    'multijet',
    ]

backgrounds = backgrounds_mc + backgrounds_dd
backgrounds_str = ','.join(backgrounds_mc+backgrounds_dd)

# Regions
region_types = ['L', 'H',]

sr_regions = [
    'SR',
    'SRi',
    ]

cr_regions = [
    'CRQ',
    'CRW', 
    'CRT',
    ]

vr_regions = [
    'VRM1', 'VRM2', 'VRM3',
    'VRE1', 'VRE2', 'VRE3',
    'VRL1', 'VRL2', 'VRL3', 'VRL4',
    'VRZ',
    ]


