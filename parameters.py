import numpy


def heights(ms):
    """Calculate heights from mass
    Only handles as single pair of masses, assumes ms is in same order as rhos.
    NBNB Assumes most dense liquid in first position."""
    hs = ms / (rhos * A)  # calculate the thickness of the layer
    hs[1] += hs[0]
    return hs


def arr_heights(marr):
    hs = marr/(tall_rhos * A)
    hs[1] += hs[0]
    return hs


# region System parameters
hb, ht = 0, 1.5  # m
A = 1 # m^2
split = numpy.array([0.5, 0.5])
feed_nom = 2*3600  # kg/h
nom_F = feed_nom * split
# endregion

# region Physiochemical parameters
rho_w, rho_o = rhos = numpy.array([1000, 500])  # kg/m^3
tall_rhos = numpy.atleast_2d(rhos).T

# endregion

# region Nominal conditions
k_w, k_o = ks = [92.9516, 227.684]  # h, kg, m
nom_m = numpy.array([1000., 500.])  # kg
h_noms = nom_h_w, nom_h_o = heights(nom_m)
lin_m0 = numpy.array([0, 0])
vec_nom_m = numpy.atleast_2d(nom_m).T
# endregion


# plotting
halfsize = (3, 12/5)


