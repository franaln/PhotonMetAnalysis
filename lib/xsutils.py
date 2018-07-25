# Signal cross sections

import os
from samples import samples_dict

data_dir = os.environ['SUSY_ANALYSIS'] + '/data/'

xs_file = os.path.join(data_dir, 'CrossSectionData.txt')

_xs_db = dict()

def _create_xs_db():

    with open(xs_file) as f:
        for line in f:
            line = line.replace('\n', '')
            if not line or line.startswith('#'):
                continue
            
            try:
                dsid, name, gen_xs, filter_eff, kfact, unc, gen_name = line.split()
            except:
                continue

            # effective cross-section and relative uncertainty
            xseff = float(gen_xs) * float(kfact) * float(filter_eff)

            _xs_db[int(dsid)] = xseff


def get_xs_from_did(did):

    if not _xs_db:
        _create_xs_db()

    if did in _xs_db:
        return _xs_db[did]

    raise Exception('ERROR: XS not found for DID=%s' % (did))

