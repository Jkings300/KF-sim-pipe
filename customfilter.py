import numpy
import control
from filterpy.kalman import KalmanFilter

from scipy.linalg import expm


class OwnKF(KalmanFilter):

    def assign_discrete(self, F, Q, H, R, P, x0, G=None):
        self.F = F
        self.Q = Q
        self.H = H
        self.R = R
        self.P = P
        self.B = G  # Note the difference in terminology here. Should probably change it back to B
        self.x = x0

    def observable(self):
        O_mat = control.obsv(self.F, self.H)
        d = numpy.linalg.matrix_rank(O_mat)
        return d


def calc_F(Am, delt):
    return expm(Am*delt)


def calc_G(Am, B, delt):
    F = calc_F(Am, delt)
    return F @ (numpy.eye(Am.shape[0])-expm(-Am*delt))@numpy.linalg.inv(Am)@ B


def run_filter(kf, saver, measurements, us=None):
    if us is None:
        us = [None]*len(measurements)
    for ith_meas, u in zip(measurements, us):
        kf.predict(u)
        kf.update(ith_meas)  # no need to transpose, they do the checks
        saver.save()
    return None
