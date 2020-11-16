from customfilter import OwnKF, calc_F, calc_G
from parameters import *
from filterpy.common import Saver


def null_func(i):
    return None


# Model values
k_wp = 0.5 * k_w * (nom_h_w * (rho_w - rho_o) + nom_h_o * rho_o - rho_w * hb) ** (-0.5)
k_op = k_o * 0.5 * rho_o ** 0.5 * (nom_h_o - ht) ** (-0.5)

a = - k_wp/(rho_w * A)
b = - k_wp/(rho_o * A)
c = - k_op/(rho_w * A)
d = - k_op/(rho_o * A)


# 3NU

Am3 = numpy.array([[a * rho_w, b * rho_o, split[0]],
                   [c, d, split[1]],
                   [0, 0, 0]])

P3 = (numpy.array([[1e3, 0, 0],
                 [0, 5e2, 0],
                 [0, 0, 7200]])*0.001)**2
H3 = numpy.array([[1, 0, 0],
                 [0, 1, 0]])


def nu3_builder(Qvar, Rvar, dt):
    F3 = calc_F(Am3, dt)
    f_var = numpy.array([[Qvar**2]])  # (kg/h)**2 Will be larger for
    Q3 = numpy.atleast_2d(F3[:, 2]).T @ f_var @ numpy.atleast_2d(F3[:, 2])
    R3 = numpy.eye(2) * Rvar ** 2
    three_state = OwnKF(3, 2)
    three_state.assign_discrete(F3, Q3, H3, R3, P3, numpy.append(lin_m0, 0))
    sav = Saver(three_state)
    return three_state, sav, null_func
# 2 State filter without inputs


def nu3_real(reals, inputs):
    return numpy.vstack([*reals, numpy.sum(inputs, axis=0)])


# wu2
Am1 = numpy.array([[a * rho_w, b * rho_o],
                   [c, d]])

P1 = (numpy.array([[1e3, 0],
                   [0, 5e2]])*0.001)**2
H1 = numpy.eye(2)
# 2 State filter with inputs
B2 = numpy.array([[1, 0],
                 [0, 1]])


def wu2_builder(Qvar, Rvar, dt):
    F1 = calc_F(Am1, dt)
    F3 = calc_F(Am3, dt)
    f_var = numpy.array([[Qvar ** 2]])
    Q1 = numpy.atleast_2d(F3[:2, 2]).T @ f_var @ numpy.atleast_2d(F3[:2, 2])
    R1 = numpy.eye(2) * Rvar ** 2
    G2 = calc_G(Am1, B2, dt)

    two_with_u = OwnKF(2, 2, 2)
    two_with_u.assign_discrete(F1, Q1, H1, R1, P1, lin_m0, G2)
    sav = Saver(two_with_u)

    def ufunc(in_flows):
        return ((numpy.sum(in_flows, axis=1)-nom_F)*numpy.atleast_2d(split).T).T

    return two_with_u, sav, ufunc


def wu2_real(reals, inputs):
    return reals


# nu2
def nu2_builder(Qvar, Rvar, dt):
    F1 = calc_F(Am1, dt)
    F3 = calc_F(Am3, dt)
    f_var = numpy.array([[Qvar ** 2]])
    Q1 = numpy.atleast_2d(F3[:2, 2]).T @ f_var @ numpy.atleast_2d(F3[:2, 2])
    R1 = numpy.eye(2) * Rvar ** 2
    two_no_u = OwnKF(2, 2)
    two_no_u.assign_discrete(F1, Q1, H1, R1, P1, lin_m0)
    sav = Saver(two_no_u)
    return two_no_u, sav, null_func


nu2_real = wu2_real


# perfect
def perfect_builder(Qvar, Rvar, dt):
    F1 = calc_F(Am1, dt)
    F3 = calc_F(Am3, dt)
    f_var = numpy.diag(Qvar) ** 2
    # f_var = numpy.array([[Qvar ** 2]])
    # Q1 = numpy.atleast_2d(F3[:2, 2]).T @ f_var @ numpy.atleast_2d(F3[:2, 2])

    R1 = numpy.eye(2) * Rvar ** 2
    G2 = calc_G(Am1, B2, dt)
    Q1 = G2 @ f_var @ G2.T

    perfect = OwnKF(2, 2, 2)
    perfect.assign_discrete(F1, Q1, H1, R1, P1, lin_m0, G2)
    sav = Saver(perfect)

    def ufunc(in_flows):
        """The ufunc in the filter should return the deviation variable form of the inputs of the given run's
        input func. Recieves inputs in tall array (time varies by row and inputs vary by column) must return in
        wide format."""
        return in_flows - nom_F # works with time by row arrays in and out

    return perfect, sav, ufunc


perfect_real = wu2_real
# NU4
Am4 = numpy.array([[a * rho_w, b * rho_o, 1, 0],
                   [c, d, 0, 1],
                   [0, 0, 0, 0],
                   [0, 0, 0, 0]])
P4 = (numpy.array([[1e3, 0, 0, 0],
                  [0, 5e2, 0, 0],
                  [0, 0, 3600, 0],
                  [0, 0, 0, 3600]])*0.001)**2
H4 = numpy.array([[1, 0, 0, 0],
                 [0, 1, 0, 0]])


def nu4_builder(Qvar, Rvar, dt):
    F4 = calc_F(Am4, dt)
    f_var = numpy.diag(Qvar)**2  # (kg/h)**2 Will be larger for
    Q4 = numpy.atleast_2d(F4[:, 2:]) @ f_var @ numpy.atleast_2d(F4[:, 2:]).T
    R4 = numpy.eye(2) * Rvar ** 2
    four_states = OwnKF(4, 2)
    four_states.assign_discrete(F4, Q4, H4, R4, P4, numpy.append(lin_m0, [0, 0]))
    sav = Saver(four_states)
    return four_states, sav, null_func
# 2 State filter without inputs


def nu4_real(reals, inputs):
    return numpy.vstack([*reals, inputs])

# define funcitions to build the "true state matrix for the specific filter from the real and inputs


filter_builders = {'WU2': wu2_builder, 'NU2': nu2_builder, 'NU3': nu3_builder, 'perfect': perfect_builder,
                   'NU4': nu4_builder}
# filters = {key: builder(200, 500, delt)[0] for key, builder in filter_builders.items()}
# savers = {key: Saver(val) for key, val in filters.items()}

true_funcs = {'NU2': nu2_real, 'WU2': wu2_real, 'NU3': nu3_real, 'perfect': perfect_real, 'NU4': nu4_real}
all_f_states = {'NU2': ['water', 'oil'], 'WU2': ['water', 'oil'], 'NU3': ['water', 'oil', 'ilmenite'],
                'perfect': ['water', 'oil'], 'NU4': ['water', 'oil', 'm_in', 's_in']}
nominal_conditions = {'NU2': vec_nom_m, 'WU2': vec_nom_m, 'perfect': vec_nom_m,
                      "NU4": numpy.vstack((vec_nom_m, [[3600], [3600]])),
                      'NU3': numpy.atleast_2d(numpy.append(nom_m, numpy.sum(nom_F))).T}


# kf, _, _ = nu4_builder([10, 20], 500, 1)