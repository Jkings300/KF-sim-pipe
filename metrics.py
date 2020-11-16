import numpy

"""Different functions for calculating performance metrics:
===========================================================
Here I code the functions for the performance metrics I've selected in INV1111
Some of the following functions are merely wrappers for normal numpy functions that could easily be used on
their own in the code, but for automation purposes they are all given the same inputs and arguments
(some just don't use all of it)"""


def p_hats(real, estimate):
    p = numpy.polyfit(real, estimate, 1)
    return numpy.polyval(p, real)


def rmses(real, estimate):
    p_hat = p_hats(real, estimate)
    error = p_hat-real
    return rmse(error)


def rmseu(real, estimate):
    phat = p_hats(real, estimate)
    error = estimate-phat
    return rmse(error)


split_rmse = {'RMSEs': rmses, 'RMSEu': rmseu}


def rmse(error):
    return numpy.sqrt(numpy.mean(error**2))


def me(error):
    return numpy.mean(error)


def mae(error):
    return numpy.mean(numpy.abs(error))


def err_var(error):
    return numpy.var(error)


error_only = {'RMSE': rmse, 'ME': me, 'MAE': mae, 'Variance': err_var}


def mre(error, real):
    return me(error/real)


def rmsre(error, real):
    return rmse(error/real)


def mare(error, real):
    return mae(error/real)


relative_metrics = {'RMSRE': rmsre, 'MRE': mre, 'MARE': mare}


def willmott_d(real, estimate, mean_func=numpy.mean, c=2):
    """Calculate the Willmott agreement index

    Parameters
    ----------
    real :
        Array of the real or observed values

    estimate :
        Array of SE estimates for the states (Predicted values)

    mean_func :
        Function that takes the real array as input and returns a single O_bar value
        or a vector of same length as real containing some other standard reference mean

    c :
        Parameter of the Willmott index. Recommended value 2 (Willmott, 2012)"""

    o_bar = mean_func(real)
    delta = numpy.sum(numpy.abs(estimate - real))
    mu = c*numpy.sum(numpy.abs(real - o_bar))

    if delta <= mu:
        return 1 - delta/mu
    else:
        return mu/delta - 1


def ln_q(real, estimate):  # strictly positive values only
    q = estimate/real
    return numpy.sum(numpy.log(q)**2)


Metrics = ['RMSEs', 'RMSEu', 'RMSE', 'ME', 'MAE', 'Variance', 'RMSRE', 'MRE', 'MARE', '$d_r$', '$\\ln Q$']
TCMetrics = ['RMSEs', 'RMSEu', 'RMSE', 'ME', 'MAE', 'Variance', 'RMSRE', 'MRE', 'MARE', 'd_r', 'ln_Q']


def eval_err_dat(err_dat):
    ind_filter = []
    ind_state = []
    all_eval = []
    for state, (real, estimate, error) in enumerate(zip(err_dat.real, err_dat.estimate, err_dat.error)):
        ind_filter.append(err_dat.name)  # uses the run_name value
        ind_state.append(state)
        evaluated = []

        for key in split_rmse:
            evaluated.append(split_rmse[key](real, estimate))
        for key in error_only:
            evaluated.append(error_only[key](error))
        for key in relative_metrics:
            evaluated.append(relative_metrics[key](error, real))

        evaluated.append(willmott_d(real, estimate))
        evaluated.append(ln_q(real, estimate))
        all_eval.append(evaluated)
    return all_eval, ind_filter, ind_state
