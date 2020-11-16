import tables
from myfilters import true_funcs, nominal_conditions
from parameters import vec_nom_m


def write_arrs_to_h5(file, arrs, names, titles=None, f_title="", attributes=None, mode='w'):
    """ Write an arbitrary number of arrays to a given HDF5 file using PyTables

    Parameters
    ----------
    file : str
        path to file

    arrs : list
        Arrays to store

    names : list
        Names of each array as they are stored in the .h5 file

    titles : list
        Descriptive titles of the arrays

    f_title : str
            Title of file

    attributes : list
        Metadata to associate with each array

    mode : str
        Mode in which the h5 file will be opened. Default is 'w', will overwrite file.
        Use 'a' for append.
    """
    num_arrays = len(arrs)
    attributes = [{}] * num_arrays if attributes is None else attributes
    titles = ['']*num_arrays if titles is None else titles

    with tables.open_file(file, mode, f_title) as f:
        for name, arr, title, attrib in zip(names, arrs, titles, attributes):
            a = f.create_array(f.root, name, arr, title)
            write_attrs(a, attrib)  # possible to gain performance here

            f.flush()
    return None


def write_attrs(arr, attr_dict):
    for key, value in attr_dict.items():
        arr.attrs[key] = value
    return None


class ErrDat:
    def __init__(self, name, filter_key, real, estimate, P_vals=None):
        self.name = name
        self.filter_key = filter_key
        self.real = real
        self.estimate = estimate
        self.error = estimate - real
        self.P_vals = P_vals


def extract_estimates(file, as_dict=False):
    """Expect the specific format of the filter estimates and extract all data into a dict,
    returns inputs, reals, implemented_filters, error_storage"""
    with tables.open_file(file) as f:
        r = f.root
        inputs = r.inputs.read().T
        reals = r.reals.read()
        implemented_filters = [key.decode("utf-8") for key in r.filters.read()]
        run_names = [name.decode("utf-8") for name in r.run_names.read()]
        error_storage = []
        for key, name in zip(implemented_filters, run_names):
            truth = true_funcs[key](reals, inputs)

            error_storage.append(ErrDat(name, key, truth, r[name].read() + nominal_conditions[key],
                                        r[name + "P"].read()))

    if as_dict:
        return inputs, reals, implemented_filters, {err_dat.name: err_dat for err_dat in error_storage}
    else:
        return inputs, reals, implemented_filters, error_storage


def extract_measurements(file):
    """Returns measurements, reals, inputs, times, linear_model"""
    with tables.open_file(file) as f:
        r = f.root
        reals = r.real.read()
        measurements = r.measurements.read()
        inputs = r.inputs.read()
        times = r.times.read()
        linear_model = r.linear.read() + vec_nom_m

        return measurements, reals, inputs, times, linear_model


