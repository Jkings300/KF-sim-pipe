import numpy
import json
import argparse
import tables
import matplotlib.pyplot as plt

from parameters import nom_m
from customfilter import run_filter
from myfilters import filter_builders, all_f_states
from datastorage import write_arrs_to_h5, extract_measurements

parser = argparse.ArgumentParser()
parser.add_argument('--parm', '-p', required=True)  # input json file root name of experiment
parser.add_argument('--jsonpattern', '-j', required=True)
parser.add_argument('--measurements', '-m', required=True)  # measurement file to run the experiment on
parser.add_argument('--output', '-o', required=True)  # h5 file to store the filtered data

args = parser.parse_args()

par_file = args.jsonpattern.replace('%', args.parm)

# unpack json
with open(par_file, 'r') as infile:
    input_json_dat = json.load(infile)['parm']

dt = input_json_dat['dt']
filter_data = input_json_dat['filters']
applied_filters = filter_data['names']
# allow for multiple runs of the same filter

if 'multiple' in input_json_dat.keys():
    run_names = input_json_dat['multiple']['run_names']
else:
    run_names = applied_filters


# read measurement data (same for all filters)
measurements, actual, in_flows, times, _ = extract_measurements(args.measurements)

filter_estimates = []
P_lists = []
for filter_key, qvars, rvars in zip(applied_filters, filter_data['Qvars'], filter_data['Rvars']):
    # build filter
    kf, sav, us_func = filter_builders[filter_key](qvars, rvars, dt)  # will rebuild each time to ensure reset
    us = us_func(in_flows)  # must convert to the relevant deviation variables

    run_filter(kf, sav, measurements.T - nom_m, us)  # here the measurements and inputs are given in deviation variables
    filter_estimates.append(numpy.array(sav.x).T)
    P_lists.append(sav.P)

P_names = [name + "P" for name in run_names]

arrs = [actual, in_flows, applied_filters, run_names] + filter_estimates + P_lists
names = ['reals', 'inputs', 'filters', 'run_names'] + run_names + P_names
write_arrs_to_h5(args.output, arrs, names)


# temporary plots to get a quick view of the data
# for filt, dat in zip(applied_filters, filter_estimates):
#     f_states = all_f_states[filt]
#     for state, state_name in zip(dat, f_states):
#         plt.plot(state, label=filt+' '+state_name)
#
# plt.plot(actual.T-nom_m, label='real')
# plt.legend()
# plt.savefig('graphs/check-filter-{}.pdf'.format(args.parm))
#
# plt.figure('inputs')
# plt.plot(in_flows)
# plt.legend(['metal-in', 'slag-in'])
# plt.savefig('graphs/check-filter-{}-inputs.pdf'.format(args.parm))
# plt.show()
