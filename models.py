from parameters import *


def non_lin_des(t, x, inp_func):
    us = numpy.array(inp_func(t))
    # Equations to calculate other outputs from current states
    # Heights
    h_w, h_o = heights(x)

    f_w = k_w * (rho_w * (h_w - hb) + rho_o * (h_o - h_w)) ** 0.5
    f_o = k_o * (rho_o * (h_o - ht)) ** 0.5

    outs = numpy.array([f_w, f_o])
    dms = us - outs
    return dms


def lin_des(t, x, inp_func):
    us = inp_func(t)

    # Equations to calculate other outputs from current states
    # Heights
    h_w, h_o = heights(x)

    # Flows: these equations are simplifications
    F_w = 0.5 * k_w * (nom_h_w * (rho_w - rho_o) + nom_h_o * rho_o - rho_w * hb) ** (-0.5) * (
            (rho_w - rho_o) * h_w + rho_o * h_o)
    F_o = k_o * 0.5 * rho_o ** 0.5 * (nom_h_o - ht) ** (-0.5) * h_o

    outs = numpy.array([F_w, F_o])

    dms = us - outs
    return dms