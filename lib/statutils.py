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


## From HistFitter -> to plot significance in "pull" plots
"""
Modified from:

  Code for "Plotting the Differences Between Data and Expectation"
  by Georgios Choudalakis and Diego Casadei
  Eur. Phys. J. Plus 127 (2012) 25
  http://dx.doi.org/10.1140/epjp/i2012-12025-y
  (http://arxiv.org/abs/1111.2062)
  -----------------------------------------------------------------
  This code is covered by the GNU General Public License:
  http://www.gnu.org/licenses/gpl.html
  -----------------------------------------------------------------

Original code available as:
  Git: (recommended)
     https://github.com/dcasadei/psde

  SVN: (old)
     svn co https://svn.cern.ch/guest/psde
     svn co svn+ssh://svn.cern.ch/guest/psde

Modifications:
  * only selected functions are avaiable here
  * code ported to python
"""

def pvalue_poisson_error(nobs, exp, var):

    if exp <= 0 or var <= 0:
        print("ERROR: expectation and variance must be positive. returning 0.5")

    B = exp/var
    A = exp * B

    # need to use logarithms
    if A > 100:

        stop = nobs
        if nobs > exp:
            stop = stop - 1

        #/ NB: must work in log-scale otherwise troubles!
        log_prob = A * math.log(B/(1+B))

        sum_ = math.exp(log_prob) # P(n=0)
        for u in range(1, stop+1):
            log_prob += math.log((A+u-1)/(u*(1+B)))
            sum_ += math.exp(log_prob)

        if nobs >  exp:
            return (1-sum_)
        else:
            return sum_

    # Recursive formula: P(nA,B) = P(n-1A,B) (A+n-1)/(n*(1+B))
    else:

        p0 = pow(B/(1+B),A) # P(0A,B)
        nexp = A/B

        if nobs > nexp: # excess
            plast = p0
            sum_ = p0
            for k in range(1, nobs):
                p = plast * (A+k-1) / (k*(1+B))
                sum_ += p
                plast = p

            return (1-sum_)

        else: # deficit
            plast = p0
            sum_ = p0
            for k in range(1, nobs+1):
                p = plast * (A+k-1) / (k*(1+B))
                sum_ += p
                plast = p

            return sum_


def pja_normal_quantile(p):

    a = [
        -3.969683028665376e+01,
         2.209460984245205e+02,
         -2.759285104469687e+02,
         1.383577518672690e+02,
         -3.066479806614716e+01,
         2.506628277459239e+00
         ]

    b = [
        -5.447609879822406e+01, # b(1) -> b[0]
         1.615858368580409e+02, # b(2)
         -1.556989798598866e+02, # b(3)
         6.680131188771972e+01, # b(4)
         -1.328068155288572e+01, # b(5) -> b[4]
         ]

    c = [
        -7.784894002430293e-03, # c(1) -> c[0]
         -3.223964580411365e-01, # c(2)
         -2.400758277161838e+00, # c(3)
         -2.549732539343734e+00, # c(4)
         4.374664141464968e+00, # c(5)
         2.938163982698783e+00, # c(6) -> c[5]
         ]

    d = [
        7.784695709041462e-03, # d(1) -> d[0]
        3.224671290700398e-01, # d(2)
        2.445134137142996e+00, # d(3)
        3.754408661907416e+00, # d(4) -> d[3]
        ]

    # Define break-points.
    p_low  = 0.02425
    p_high = 1 - p_low

    # output value
    x = 0

    # Rational approximation for lower region.
    if 0 < p and p < p_low:
        q = math.sqrt(-2*math.log(p))
        x = (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)

    # Rational approximation for central region.
    elif p_low <= p and p <= p_high:
        q = p - 0.5
        r = q*q
        x = (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)

    # Rational approximation for upper region.
    elif p_high < p and p < 1:
        q = math.sqrt(-2*math.log(1-p))
        x = -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)

    return x


def pvalue_to_significance(p, excess): # excess: bool, False if deficit

    if p < 0 or p > 1:
        print("ERROR: p-value must belong to [0,1] but input value is ", p)
        return 0

    if excess:
        return pja_normal_quantile(1-p)
    else:
        return pja_normal_quantile(p)
