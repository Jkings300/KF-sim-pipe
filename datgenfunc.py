import numpy
import itertools as it
from scipy.integrate import solve_ivp


# Function using solve_ivp if have input function available
# This should allow for fast integration with partwise smooth inputs
def mult_meas_gen(diff_func, inp_func, tspans, dt, m0, noise_sd, max_step=numpy.inf, method='RK45'):
    """Inputs:
        diff_func: function f(t, x, inp_func) that returns the derivatives of a model at time t and state x

        tspans: iterable of tuples of start and end of simulation, like in scipy.integrate.solve_ivp
            meant to break the simulation when discontinuities in the derivatives occur.

        dt: step between measurements

        m0: initial states

        noise_sd: array with same length as number of states, standard deviation of the
            noise to be added to each state

        max_step: default None, same as in scipy.integrate.solve_ivp

        method: default 'RK45' same as in scipy.integrate.solve_ivp

       Outputs:
        meas: simulated values with noise added
        ys: the simulated values without noise
        tsmooth: times used to simulate results
        """

    def wrapper(t, x):
        return diff_func(t, x, inp_func)

    all_meas = []
    all_ys = []
    all_ts = []

    # This loop is a state handover
    # takes spans given, starts each span from the previous one's end so make sure input funcs are >=
    # In effect how this works I let solve_ivp integrate for only the section where the inputs are continuous
    # this means that I give a tspan for a completely continuous section.
    # I use the dense_output numerical approximation of the solution to predict
    # from the start of the first section up to the start of the next
    # This give the initial value of the next tspan without letting the input change influence the previous section's
    # numeric approximation.
    # Important to note here that the input value at the value of change should still be part of this
    # continuous input section
    # This implies the input only changes after the tspan[1]
    # This gave crisp results.
    # I then adjust the eval times after first section to not re-evaluate the initial value.
    for num, tspan in enumerate(tspans):
        # first should not drop the initial value
        if num == 0:
            tsmooth = numpy.arange(tspan[0], tspan[1] + dt, dt)  # from first value to start of next span
        else:
            tsmooth = numpy.arange(tspan[0] + dt, tspan[1] + dt, dt)
            # not eval the first value as we already know what it is

        all_ts.append(tsmooth)
        result = solve_ivp(wrapper, tspan, m0, method=method, dense_output=True, max_step=max_step)

        ys = result.sol(tsmooth)
        m0 = ys[:, -1]
        all_ys.append(ys)
        noise = numpy.random.randn(*ys.shape) * numpy.atleast_2d(noise_sd).T
        meas = ys + noise
        all_meas.append(meas)
    return numpy.hstack(all_meas), numpy.hstack(all_ys), numpy.hstack(all_ts)


def create_tspans(tends):
    a, b = it.tee(tends)
    next(b, None)
    return list(zip(a, b))
