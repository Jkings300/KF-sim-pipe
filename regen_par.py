import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--set', '-s', required=True)
args = parser.parse_args()

with open('input-runs/all-runs.json', 'r') as db:
    runs_data = json.load(db)[args.set]

with open('input-runs/{}.json'.format(args.set), 'w') as outfile:
    parm = {'parm': runs_data}
    json.dump(parm, outfile)
