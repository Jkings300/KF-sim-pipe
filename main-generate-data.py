import argparse
import numpy
# import scipy.interpolate
import json
# import matplotlib.pyplot as plt

from models import non_lin_des, lin_des
from datgenfunc import create_tspans, mult_meas_gen
from datastorage import write_arrs_to_h5
from parameters import nom_m, nom_F, lin_m0
from inputs import all_inputs

parser = argparse.ArgumentParser()
parser.add_argument('--parameters', '-p', required=True)
parser.add_argument('--output', '-o', required=True)

args = parser.parse_args()
with open(args.parameters, 'r') as input_file:
    run_dict = json.load(input_file)['parm']

R = numpy.array(run_dict['R'])
run_name = run_dict['name']
delt = run_dict['dt']
input_dict = run_dict['input']
inp_gen_name = input_dict['func']
inp_gen_args = input_dict['args']
inp_gen = all_inputs[inp_gen_name]

method = 'Radau'
if 'integration' in run_dict.keys():
    int_dict = run_dict['integration']
    try:
        method = int_dict['method']
    except KeyError:
        print("Warning: no method selected")

inp_func, end_times = inp_gen(*inp_gen_args, delt)


def lin_inp_func(t):
    return inp_func(t) - nom_F


tspan_list = create_tspans(numpy.append([0], end_times))

measurements, real_values, simulation_times = mult_meas_gen(diff_func=non_lin_des, inp_func=inp_func,
                                                            tspans=tspan_list, dt=delt,
                                                            m0=nom_m, noise_sd=R, method=method)

_, lin_vals, _ = mult_meas_gen(diff_func=lin_des, inp_func=lin_inp_func,
                               tspans=tspan_list, dt=delt,
                               m0=lin_m0, noise_sd=0, method=method)
# write data to file

meas_data_names = ['times',  # Times
                   'real',  # Real
                   'measurements',  # meas
                   'linear',
                   'inputs',  # inputs
                   'R_meas']  # R

inputs = numpy.array([inp_func(t) for t in simulation_times])


arrs = [simulation_times[1:],
        real_values[:, 1:],
        measurements[:, 1:],
        lin_vals[:, 1:],
        inputs[1:, :],
        R]

write_arrs_to_h5(args.output, arrs, meas_data_names)

# hs = numpy.array([heights(x) for x in measurements.T])
# plt.figure()
# plt.plot(simulation_times, hs)
# plt.savefig('graphs/meas-heights-{}.pdf'.format(run_name))
# plt.figure()
# plinputs = numpy.array([inp_func(t) for t in simulation_times])
# plt.plot(simulation_times, plinputs)
# plt.savefig('graphs/meas-heights-{}-inputs.pdf'.format(run_name))
# plt.show()
