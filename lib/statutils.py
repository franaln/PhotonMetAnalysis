import ROOT
import math
from array import array

def get_significance(s, b, sb, minb=None, mins=None):
    
    sig = ROOT.RooStats.NumberCountingUtils.BinomialExpZ(s, b, sb)

    if minb is not None and b < minb:
        sig = 0.
    if mins is not None and s < mins:
        sig = 0.
    if sig < 0.:
        sig = 0.

    if sig == float('Inf'):
        sig = 0.
    
    return sig



def get_significance_unc(s, b, sb=0.5, minb=None, mins=None): 

    """ Get significance taking into account
    the background systematic uncertainty
    (from Cowan formula) """

    try:
        s = s.mean
        b = b.mean
    except:
        pass

    s, b = float(s), float(b)

    if s < 0.00001 or b < 0.00001:
        return 0.00

    if mins is not None and s < mins:
        return 0.00
    if minb is not None and b < minb:
        return 0.00

    sb = sb * b # as default we use 50% of uncertainty for the background

    za2_p = (s + b) * math.log( ((s + b) * (b + sb**2)) / (b**2 + (s + b) * sb**2) )
    za2_m = (b**2/sb**2) * math.log( 1 + (s * sb**2)/(b * (b + sb**2)) )

    za2 = 2 * (za2_p - za2_m)

    if za2 <= 0.:
        return 0

    za = math.sqrt(za2)

    if za > 0.0:
        za = round(za, 2)
    else:
        za = 0.00

    return za


# def get_significance(s, b):

#     try:
#         s = s.mean
#         b = b.mean
#     except:
#         pass

#     s, b = float(s), float(b)

#     try:
#         za2 = 2 * ((s+b) * math.log(1+s/b) - s)
#     except:
#         return 0.

#     if za2 <= 0:
#         return 0.

#     za = math.sqrt(za2)

#     return round(za, 2)


def get_sb(s, b):
    if b > 0:
        return s/math.sqrt(b)
    else:
        return 0


def pvalue(obs, exp):
    if obs > exp:
        return 1 - ROOT.Math.inc_gamma_c(obs, exp)
    else:
        return ROOT.Math.inc_gamma_c(obs+1, exp)


def zvalue(pvalue):
    return ROOT.TMath.Sqrt(2) * ROOT.TMath.ErfInverse(1. - 0.2*pvalue)


def poisson_significance(obs, exp):

    p = pvalue(obs, exp)

    if p < 0.5:
        if obs > exp:
            return zvalue(p)
        else:
            return -zvalue(p)

    return 0.0


def calc_poisson_cl_lower(q, obs):
    """
    Calculate lower confidence limit
    e.g. to calculate the 68% lower limit for 2 observed events:
    calcPoissonCLLower(0.68, 2.)
    """
    ll = 0.
    if obs >= 0.:
        a = (1. - q) / 2. # = 0.025 for 95% confidence interval
        ll = ROOT.TMath.ChisquareQuantile(a, 2.*obs) / 2.

    return ll

def calc_poisson_cl_upper(q, obs):
    """
    Calculate upper confidence limit
    e.g. to calculate the 68% upper limit for 2 observed events:
    calcPoissonCLUpper(0.68, 2.)
    """
    ul = 0.
    if obs >= 0. :
        a = 1. - (1. - q) / 2. # = 0.025 for 95% confidence interval
        ul = ROOT.TMath.ChisquareQuantile(a, 2.* (obs + 1.)) / 2.

    return ul

def get_poisson_interval(q, obs):
    return calc_poisson_cl_lower(0.68, obs), calc_poisson_cl_upper(0.68, obs)

def make_poisson_cl_errors(hist):

    x_val    = array('f')
    y_val    = array('f')
    x_err_up = array('f')
    x_err_dn = array('f')
    y_err_up = array('f')
    y_err_dn = array('f')

    for b in range(1, hist.GetNbinsX()+1):
        bin_c = hist.GetBinContent(b)

        if bin_c < 0.0000001:
            continue

        if bin_c - int(bin_c) < 0.0001:
            y_dn, y_up = get_poisson_interval(0.68, bin_c)
        else:
            n1 = int(bin_c)
            n2 = n1+1

            y1_dn, y1_up = get_poisson_interval(0.68, n1)
            y2_dn, y2_up = get_poisson_interval(0.68, n2)

            y_dn = y1_dn + (bin_c - n1)*(y2_dn - y1_dn)
            y_up = y1_up + (bin_c - n1)*(y2_up - y1_up)

        x_val.append(hist.GetXaxis().GetBinCenter(b))
        y_val.append(bin_c)

        y_err_up.append(y_up - bin_c)
        y_err_dn.append(bin_c - y_dn)

        x_err_up.append(0.) #hist.GetXaxis().GetBinWidth(b)/2.)
        x_err_dn.append(0.) #hist.GetXaxis().GetBinWidth(b)/2.)


    if len(x_val) > 0:
        data_graph = ROOT.TGraphAsymmErrors(len(x_val), x_val, y_val, x_err_dn, x_err_up, y_err_dn, y_err_up)
        return data_graph
    else:
        return ROOT.TGraph()
