runnames =  hidden perflin  demo #will require update to include new runs
#define patterns for the substitution of
jpat = input-runs/%.json
mpat = measurements/measurements-%.h5
fpat = filter-output/filter-est-%.h5
epat = evaluated-pm/pm-%.csv
parpat = graphs/parities/parity-%-*.pdf

parplots = $(runnames:%=$(ppat))
jsons = $(runnames:%=$(jpat))
measurements = $(runnames:%=$(mpat))
filters = $(runnames:%=$(fpat))
evaluated = $(runnames:%=$(epat))

# If there was a change in one of the jsons, delete to have it update from the all-runs
all:  $(evaluated) $(filters) $(measurements) $(jsons)  # the ordering here could make a difference to performance


$(epat): $(fpat) metrics.py main-pm-analysis.py
	python3 main-pm-analysis.py -i $< -o $@ -p $(mpat) -r $*

$(fpat): $(mpat) main-run-filter.py
	python3 main-run-filter.py -p $* -j $(jpat) -m $< -o $@

$(mpat): $(jpat) main-generate-data.py
	python3 main-generate-data.py -p $< -o $@

$(jpat):
	python3 regen_par.py -s $*

clear_json:
	-rm $(jsons)
clear_measurements:
	-rm $(measurements)
clear_filters:
	-rm $(filters)
clear_pm:
	-rm $(evaluated)
clean: clear_measurements clear_filters clear_pm

se_plots: $(filters)
	python3 se-res-plots.py

pm_plots: $(evaluated)
	python3 pm-plots.py

pplots: $(filters)
	for i in $(filters); do \
  		python3 main-parity-plots.py -e $$i -r $(fpat) -g $(parpat) ; \
  		done
.PHONY: clean clear_json clear_measurements clear_filters clear_pm pplots se_plots pm_plots