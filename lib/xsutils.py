# Signal cross sections

import os
from samples import samples_dict

data_dir = os.environ['SUSY_ANALYSIS'] + '/data/'

signal_xs_files = [
    'HerwigppEvtGen_UEEE5CTEQ6L1_GGM_M3_mu.txt',
    'HerwigppEvtGen_UEEE5CTEQ6L1_GGM_mu.txt',
    'MGPy8EG_A14N23LO_GGM_GG_bhmix.txt',
    'MGPy8EG_A14N23LO_GGM_CN_bhmix.txt',
]

bkg_xs_file = 'susy_crosssections_13TeV.txt'

_bkg_xs_db = dict()
_sig_xs_db = dict()

def _create_xs_db():

    # Background 
    with open(data_dir + bkg_xs_file) as f:
        for line in f:
            line = line.replace('\n', '')
            if not line or line.startswith('#'):
                continue
            
            try:
                did, sample, xs, kfac, eff, unc = line.split()
            except:
                continue

            # effective cross-section and relative uncertainty
            xseff = float(xs) * float(kfac) * float(eff)
            relunc = float(unc)

            _bkg_xs_db[int(did)] = (xseff, relunc)


    # Signal
    for xs_file in signal_xs_files:
        with open(data_dir+xs_file) as f:
            for line in f:
                line = line.replace('\n', '')
                if not line or line.startswith('#'):
                    continue
            
                try:
                    did, fs, xs, kfac, eff, unc = line.split()
                except:
                    continue

                # effective cross-section and relative uncertainty
                xseff = float(xs) * float(kfac) * float(eff)
                relunc = float(unc)

                _sig_xs_db[(int(did), int(fs))] = (xseff, relunc)



def get_did(name):
    sample = samples_dict[name]
    return sample.split('.')[1]

def get_xs_did(did, fs=None):

    if not _bkg_xs_db or not _sig_xs_db:
        _create_xs_db()

    if did in _bkg_xs_db:
        return _bkg_xs_db[did]
    elif (did, fs) in _sig_xs_db:
        return _sig_xs_db[(did, fs)]

    raise Exception('ERROR: XS not found for DID=%s (FS=%s)' % (did, fs))


def get_xs(par1, par2=None, fs=None):

    # GGM_mu
    if par2 is None:
        name = 'GGM_mu_%i' % par1
    # GGM_M3_mu
    else:
        name = 'GGM_M3_mu_%i_%i' % (par1, par2)

    did = get_did(name)

    return get_xs_did(did, fs)



# Electroweak signal 
relevant_fs = [111, 112, 113, 115, 117, 118, 123, 125, 126, 127, 133, 134, 135, 137, 138, 146, 148, 157, 158, 168]

def get_ewk_totalxs(did):

    total_xs = 0.
    total_unc = 0.
    for fs in relevant_fs:
        tmp = get_xs(did, fs=fs)
        total_xs += tmp[0]
        total_unc += tmp[1]

    total_unc /= len(relevant_fs) # avg between diff fs. FIX?

    return (total_xs, total_unc)

ewk_sumw = {

    150: {
        112: 3641.00,
        115: 4198.00,
        117: 2350.00,
        123: 85.00,
        125: 3860.00,
        127: 2154.00,
        135: 107.00,
        137: 54.00,
        157: 3551.00,
        },

    200: {
        111:  1.00,
        112:  3143.00,
        115:  4005.00,
        117:  2088.00,
        123:  347.00,
        125:  4044.00,
        127:  2099.00,
        135:  444.00,
        137:  195.00,
        157:  3634.00,
        },

    250: {
        112:  2892.00,
        115:  3611.00,
        117:  1786.00,
        123:  641.00,
        125:  4141.00,
        127:  2034.00,
        135:  877.00,
        137:  380.00,
        157:  3638.00,
        },

    450: {
        111:  2.00,
        112:  2218.00,
        115:  3083.00,
        117:  1178.00,
        123:  1176.00,
        125:  4524.00,
        127:  1774.00,
        135:  1686.00,
        137:  670.00,
        157:  3689.00,
        },

    650: {
        111:  4.00,
        112:  1958.00,
        113:  3.00,
        115:  2923.00,
        117:  962.00,
        123:  1376.00,
        125:  4925.00,
        127:  1579.00,
        135:  2057.00,
        137:  644.00,
        157:  3569.00,
        },

    850: {
        111:  3.00,
        112:  1819.00,
        113:  2.00,
        115:  2921.00,
        117:  876.00,
        123:  1416.00,
        125:  5063.00,
        127:  1515.00,
        133:  2.00,
        135:  2174.00,
        137:  684.00,
        157:  3525.00,
        },

    1050: {
        112:  1697.00,
        113:  6.00,
        115:  2890.00,
        117:  767.00,
        123:  1422.00,
        125:  5189.00,
        127:  1457.00,
        133:  2.00,
        135:  2414.00,
        137:  623.00,
        157:  3533.00,
        },
        
    1250: {
        111:  4.00,
        112:  1655.00,
        113:  5.00,
        115:  2914.00,
        117:  721.00,
        123:  1438.00,
        125:  5253.00,
        127:  1321.00,
        133:  1.00,
        135:  2514.00,
        137:  621.00,
        157:  3553.00,
        },

    1450: {
        111:  5.00,
        112:  1616.00,
        113:  5.00,
        115:  2938.00,
        117:  709.00,
        123:  1440.00,
        125:  5282.00,
        126:  1.00,
        127:  1352.00,
        133:  3.00,
        135:  2510.00,
        137:  608.00,
        148:  1.00,
        157:  3530.00,
        },

    1650: {
        111:  10.00,
        112:  1635.00,
        113:  11.00,
        115:  2817.00,
        117:  661.00,
        118:  1.00,
        123:  1504.00,
        125:  5215.00,
        127:  1286.00,
        133:  3.00,
        135:  2514.00,
        137:  581.00,
        138:  1.00,
        146:  2.00,
        157:  3757.00,
        158:  1.00,
        168:  1.00,
        },

    1850: {
        111:  8.00,
        112:  1571.00,
        113:  14.00,
        115:  2838.00,
        117:  620.00,
        123:  1466.00,
        125:  5260.00,
        126:  2.00,
        127:  1230.00,
        133:  3.00,
        134:  1.00,
        135:  2528.00,
        137:  611.00,
        146:  3.00,
        157:  3841.00,
        168:  4.00,
        }
}

def get_ewk_sumw(mu, fs=None):

    if fs is None:
        total_sumw = 0
        for fs in relevant_fs:
            total_sumw += get_ewk_sumw(mu, fs)
        return total_sumw

    sumw = 0
    try: 
        sumw = ewk_sumw[mu][fs]
    except:
        pass

    return sumw

