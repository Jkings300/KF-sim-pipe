import numpy
from scipy.interpolate import interp1d

from parameters import split
# NBNB order of variables in output is water then oil


def random_steps(total_length, min_length, max_length):
    """Generate an array of integers that add up to total_length,
    with values between min_length and max_length (inclusive)"""
    # Start building on integers because we are limited to discrete time values

    cummulative = 0
    steps = []

    while cummulative < total_length:
        steps_i = numpy.random.randint(min_length, max_length+1)
        if cummulative + steps_i > total_length:
            steps_i = total_length-cummulative
        cummulative += steps_i
        steps.append(steps_i)

    return numpy.array(steps)


def random_times(t_final, min_time, max_time, dt):
    """Generate array of time values, ending at t_final.
    Consecutive times differ by a value between min_time and max_time and they are all possible times for step-size dt.
    For now this works for reasonable dt values."""
    step_args = numpy.array([t_final, min_time, max_time]) / dt
    steps = random_steps(*step_args)
    time_lengths = steps*dt
    t_ends = numpy.cumsum(time_lengths)
    return t_ends  # zero not included


def input_factory(tends: numpy.ndarray, magnitudes: numpy.ndarray):
    """Build a function that returns the magnitude of a step in the relevant time-span, given a t.

    :param tends: array of ending time values corresponding to the magnitudes
        NB must include all times you want to call for

    :param magnitudes: array of step magnitudes, each corresponding to a specific end time of the step.
        This means that for a value <= tend it will return the corresponding magnitude


    :returns input_func: function in form f(t) that takes the given time value and returns the corresponding step
        In order to make this work with multi_meas_gen it needs to return the magnitude in the
        interval (closest_previous_time, next_time]"""

    tends, magnitudes = map(numpy.asarray, [tends, magnitudes])

    def input_func(t: float):
        mask = (t <= tends)
        try:  # handle exception when solve_ivp calls past allowed range.
            return magnitudes[mask][0]
        except IndexError:
            return magnitudes[-1]
    return input_func


def step_wrapper(end_times, step_mags):
    return interp1d(end_times, step_mags, kind='next', fill_value='extrapolate')


# random step of ilmenite with constant composition
def random_step_constant(time_args, size_args, dt):
    """Build input function assuming the ilmenite composition stays constant."""
    end_times = random_times(*time_args, dt)
    step_mags = numpy.random.uniform(*size_args, len(end_times))

    rand_ilm = step_wrapper(end_times, step_mags)

    def inp_func(t):
        return rand_ilm(t) * split
    return inp_func, end_times


def random_step_different(time_args, water_args, oil_args, dt):
    """First stick to switching at same time"""
    end_times = random_times(*time_args, dt)
    water_mags = numpy.random.uniform(*water_args, len(end_times))
    oil_mags = numpy.random.uniform(*oil_args, len(end_times))

    return separate_steps(end_times, water_mags, oil_mags, dt)


def separate_steps(end_times, water_mags, oil_mags, dt):
    water = step_wrapper(end_times, water_mags)
    oil = step_wrapper(end_times, oil_mags)

    def inp_func(t):
        return water(t), oil(t)

    return inp_func, end_times


all_inputs = {'separate_steps': separate_steps, 'random_step_constant': random_step_constant,
              'random_step_different': random_step_different}


