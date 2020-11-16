import argparse
import tables
import pandas
from collections import defaultdict

from parameters import vec_nom_m
from datastorage import ErrDat, extract_estimates
from metrics import eval_err_dat, TCMetrics, relative_metrics, split_rmse, error_only, willmott_d, ln_q
# from filterpy.stats import NESS
parser = argparse.ArgumentParser()

parser.add_argument('--input', '-i', required=True)
parser.add_argument('--output', '-o', required=True)
parser.add_argument('--pattern', '-p', required=True)
parser.add_argument('--root', '-r', required=True)
args = parser.parse_args()

# read data from input h5
inputs, reals, filter_names, error_storage = extract_estimates(args.input)

meas_file = args.pattern.replace('%', args.root)

# read linear model and measurements form the meas file

with tables.open_file(meas_file) as f:
    r = f.root
    measurements = r.measurements.read()
    linear_model = r.linear.read() + vec_nom_m

extra_data = [ErrDat(name, name, reals, values)
              for name, values in zip(['measurements', 'linear'], [measurements, linear_model])]
error_storage += extra_data
# create the output file
ind_filter = []
ind_state = []

data_dict = defaultdict(list)
data_dict.update({"Filter": ind_filter, "State": ind_state})

for err_dat in error_storage:

    # for state,  (real, estimate, error) in enumerate(zip(err_dat.real, err_dat.estimate, err_dat.error)):
    #     ind_filter.append(name)
    #     ind_state.append(state)
    #     evaluated = []
    #
    #     for key in split_rmse:
    #         evaluated.append(split_rmse[key](real, estimate))
    #     for key in error_only:
    #         evaluated.append(error_only[key](error))
    #     for key in relative_metrics:
    #         evaluated.append(relative_metrics[key](error, real))
    #
    #     evaluated.append(willmott_d(real, estimate))
    #     evaluated.append(ln_q(real, estimate))
    #
    #     for met, val in zip(TCMetrics, evaluated):
    #         data_dict[met].append(val)

    eval_states, i_filts, i_states = eval_err_dat(err_dat)
    ind_state += i_states
    ind_filter += i_filts
    for evaluated in eval_states:
        for met, val in zip(TCMetrics, evaluated):
            data_dict[met].append(val)

df = pandas.DataFrame(data_dict)
df.set_index(['Filter', 'State'], inplace=True)
df.to_csv(args.output)  # testing make
