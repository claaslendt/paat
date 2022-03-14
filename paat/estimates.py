import pandas as pd

from . import preprocessing


def calculate_pa_levels(time, acceleration, mvpa_cutpoint=.069, sb_cutpoint=.015, interval="1s"):
    """
    Calculate moderate to vigourous physical activity (MVPA) and sedentary behavior
    based on cutpoints (mvpa_cutpoint and sb_cutpoint). On default, this procedure
    uses the algorithm and  values from Sanders et al. (2019). This means

        1. The Euclidian norm minus one (ENMO) is calculated from the triaxial signal
        2. The ENMO is averaged over 1s epochs
        3. These epochs are compared against the cutpoints MVPA = 69mg and SB = 15mg

    References
    ----------

    George J. Sanders, Lynne M. Boddy, S. Andy Sparks, Whitney B. Curry, Brenda Roe,
    Axel Kaehne & Stuart J. Fairclough (2019) Evaluation of wrist and hip sedentary
    behaviour and moderate-to-vigorous physical activity raw acceleration cutpoints
    in older adults, Journal of Sports Sciences, 37:11, 1270-1279,
    DOI: 10.1080/02640414.2018.1555904

    Parameters
    ----------
    time : np.array (n_samples x 1)
        a numpy array with time stamps for the observations in values
    acceleration : np.array (n_samples x 3)
        a numpy array with the tri-axial acceleration values in
        the default order of ActiGraph which is ['Y','X','Z']
    mvpa_cutpoint : float (optional)
        a float indicating the cutpoint between light physical activity and
        moderate-to-vigourous activity
    sb_cutpoint : float (optional)
        a float indicating the cutpoint between light physical activity and
        sedentary behavior
    interval : str (optional)
        a str indicating at what frequency the cutpoints are calculated

    Returns
    ---------
    pa_levels : np.array (n_samples, 2)
        a numpy array indicating whether the values of the acceleration data are
        moderate-to-vigourous physical activity (first column) or sedentary
        behavior (second column)

    """
    data = pd.DataFrame(acceleration, columns=["Y", "X", "Z"])
    data.loc[:, "Time"] = time
    data.loc[:, "EMNO"] = preprocessing.calculate_vector_magnitude(acceleration,
                                                                   minus_one=True,
                                                                   round_negative_to_zero=True)

    if interval:
        tmp = data.set_index("Time").resample(interval).mean().reset_index()
    else:
        tmp = data

    tmp.loc[:, "MVPA"] = (tmp["EMNO"].values >= mvpa_cutpoint)
    tmp.loc[:, "SB"] = (tmp["EMNO"].values <= sb_cutpoint)

    data = pd.merge_asof(data, tmp[["Time", "MVPA", "SB"]], on="Time")

    return data[["MVPA", "SB"]].values