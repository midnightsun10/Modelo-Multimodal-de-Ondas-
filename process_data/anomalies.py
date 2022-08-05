#!/usr/bin/env python

import os
import gc
import sys
import glob
import xarray as xr
import pandas as pd
import xesmf as xe
import numpy as np
sys.path.append("/home/brayan/mnsun/")
from utils import check_dir
import datetime 
import warnings
warnings.filterwarnings('ignore')


def create_xarray(data_, dim1, dim2, dim3, dim1_name, dim2_name, dim3_name):
    """
    Se crea un xarray que tiene la siguiente estructura estandar:
    'time, latitud, longitud'
    
    Output: Informacion de data_Xarray en formato float_32 [Xarray] 
    """
    Array  =  xr.DataArray( np.float32(data_) ,
                            coords=[ dim1, dim2, dim3],
                            dims=[ dim1_name, dim2_name, dim3_name])     
    return Array

def main():
    DIR_             = str(os.environ["OUTPUT"])  #"/home/brayan/DATA/Modelo-Multimodal-de-Ondas/process/ASCAT/" 
    date_update      = str(os.environ["CURRENT_DATE"])

    file_tau         = glob.glob(DIR_+f"TAU/{date_update[:4]}/"+"".join(date_update.split("-"))+".nc")[0]
    DS_ASCAT         = xr.open_dataset(file_tau).interpolate_na(dim="lat", method="nearest", fill_value="extrapolate")
    DS_CLIM          = xr.open_dataset(DIR_+f"CLIMATOLOGY/TAU_CLIM.nc")
    if date_update[5:] == "02-29":
        number_day_of_year = 58
    else:
        number_day_of_year  = datetime.datetime.strptime(date_update, "%Y-%m-%d").date().timetuple().tm_yday-1
    TAUX_ANOM        = DS_ASCAT.taux-DS_CLIM.clim_taux.isel(dayofyear=number_day_of_year)
    TAUY_ANOM        = DS_ASCAT.tauy-DS_CLIM.clim_tauy.isel(dayofyear=number_day_of_year)
    ATAUX_CLEAN      = create_xarray(TAUX_ANOM.values.reshape(1, TAUX_ANOM.lat.shape[0], TAUX_ANOM.lon.shape[0]), pd.date_range(date_update, periods=1, freq="D"), TAUX_ANOM.lat, TAUX_ANOM.lon, "time", "lat", "lon")
    ATAUY_CLEAN      = create_xarray(TAUY_ANOM.values.reshape(1, TAUY_ANOM.lat.shape[0], TAUY_ANOM.lon.shape[0]), pd.date_range(date_update, periods=1, freq="D"), TAUY_ANOM.lat, TAUY_ANOM.lon, "time", "lat", "lon")
    DATASET_ANOM     = xr.Dataset({"ataux": ATAUX_CLEAN, "tauy": ATAUY_CLEAN})

    check_dir(DIR_+"ANOMALY/" +str(date_update)[:4]+"/")
    DATASET_ANOM.to_netcdf(DIR_+"ANOMALY/"+str(date_update)[:4]+"/"+"".join(str(date_update)[:10].split("-"))+".nc")   

if __name__ == "__main__":
    main()