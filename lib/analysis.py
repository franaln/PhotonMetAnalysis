# Default options
use_purw = False

# Mini version
# versions = ['34']

# Luminosity
# lumi_data15 = 3209.05 # 20.1 
# lumi_data15 = 3245.43 # pb-1 20.7
# lumi_data15 = 3193.68 # pb-1 20.7 FINAL GRL v79-repro20-02 
# lumi_data16 = 2613.83 # pb-1 DS1
# lumi_data16 = 6302.24 # pb-1 DS1.2
# lumi_data16 = 8585.76 # pb-1 DS1.3

# NEW: OffLumi-13TeV-005
lumi_data15 = 3212.96  # All
lumi_data16 = 10064.30 # DS2
#lumi_data16 = 11571.50 # DS2.1

# Signal
from mass_dict import mass_dict
signal = [ 'GGM_M3_mu_%i_%i' % (m3, mu) for (m3, mu) in mass_dict.keys() ]

# Backgrounds
backgrounds_mc = [
    'photonjet',
    'wgamma',
    'zllgamma', 
    'znunugamma',
    'ttbarg',
    'diphoton',
    'vgammagamma',
    'vqqgamma',
    ]

backgrounds_dd = [
    'efake',
    'jfake',
    ]

backgrounds_extra_mc = [
    'ttbar', 
    'zjets', 
    'wjets',
    'multijet',
    ]

backgrounds_str = ','.join(backgrounds_mc+backgrounds_dd)

# Regions
region_types = ['L', 'H',]

sr_regions = [
    'SR',
    'SRincl',
    ]

cr_regions = [
    'CRQ',
    'CRW', 
    'CRT',
    ]

vr_regions = [
    'VRM1', 'VRM2', 'VRM3',
    'VRD1', 'VRD2', 'VRD3',
    'VRL1', 'VRL2', 'VRL3', 'VRL4'
    ]


