import ROOT
import math

def get_significance_unc(s, b, sb_over_b=0.5):

    """ Get significance taking into account
    the background systematic uncertainty
    (from Cowan formula) """

    try:
        s = s.mean
        b = b.mean
    except:
        pass

    s, b = float(s), float(b)

    if s < 0 or b < 0:
        return 0.00
    if b == 0.:
        return 0.00

    sb = sb_over_b * b # as default we use 50% of uncertainty for the background

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


def get_significance(s, b):

    try:
        s = s.mean
        b = b.mean
    except:
        pass

    s, b = float(s), float(b)

    try:
        za2 = 2 * ((s+b) * math.log(1+s/b) - s)
    except ZeroDivisionError:
        return 0.

    if za2 <= 0:
        return 0.

    za = math.sqrt(za2)

    return round(za, 2)


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


# def calc_z_bi(s, b):

#     n_on = 

#     tau = mu_b_hat / (sigma_b**2)
#     n_off = tau * mu_b_hat
    
#     p_bi = ROOT.TMath.BetaIncomplete(1./(1.+tau), n_on, n_off+1)
#     z_bi = math.sqrt(2) * ROOT.TMath.ErfInverse(1 - 2*p_bi)

    
