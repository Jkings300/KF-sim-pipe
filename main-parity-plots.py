import matplotlib.pyplot as plt
import argparse
import numpy as np

from datastorage import extract_estimates

parser = argparse.ArgumentParser()
parser.add_argument('--estimate_file', '-e', required=True)
parser.add_argument('--root_pattern', '-r', required=True)
parser.add_argument('--graph_pattern', '-g', required=True)
args = parser.parse_args()

m_inputs, m_reals, filter_names, error_storage = extract_estimates(args.estimate_file)

# get the things to remove from the estimate file to get the root
# this workround necessary as I couldn't figure out how to use the autovars in the make file


def parity_line(r, e):
    unite = np.append(r, e)
    mi = np.min(unite)
    ma = np.max(unite)
    return [mi, ma], [mi, ma]


to_remove = args.root_pattern.split('%')
run_name = args.estimate_file
for i in to_remove:
    run_name = run_name.replace(i, '')  # remove both sides of the pattern
graph_base = args.graph_pattern.replace('%', run_name)

for f_data in error_storage:
    f_name = f_data.name
    estimates = f_data.estimate
    reals = f_data.real
    for i, (real, est) in enumerate(zip(reals, estimates), 1):
        graph_file = graph_base.replace('*', f_name + str(i))
        plt.figure(graph_file)
        plt.plot(*parity_line(real, est), 'k', label='ideal')
        plt.plot(real, est, '.', color='red', markersize=1, label=f_name + str(i))

        plt.gca().set_aspect('equal')
        plt.xlabel('Real values', fontsize=12)
        plt.ylabel('Estimated values', fontsize=12)
        plt.tight_layout()
        plt.savefig(graph_file)
plt.show()