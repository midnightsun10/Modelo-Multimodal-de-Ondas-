#!/usr/bin/env python

import os
import xarray as xr
import glob
import numpy as np
import pandas as pd

def dates_download(init_, end_):
    
    """
    Esta funcion permite listar las fechas que seran utilizadas para la descarga.
    
    Input: 
            init_: fecha de inicio [string]
            end_ : fecha final [string]
    Output: 
            : fechas listadas [list]    
    """
    
    if init_ != end_:
        dates_ = pd.date_range(init_, end_, freq="D")
    else:
        dates_ = pd.date_range(init_, periods=1, freq="D")
        
    return [str(i)[:10] for i in dates_.values]  

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
    OUTPUT_DIR       = str(os.environ["OUTPUT"])
    init_date_update = str(os.environ["INIT_DATE"])
    end_date_update  = str(os.environ["END_DATE"])

    list_ncs   = [glob.glob(OUTPUT_DIR+"TAU/"+date_.split("-")[0]+"/"+"".join(date_.split("-"))+"*")[0] for date_ in dates_download(init_date_update, end_date_update)]
    list_dates = dates_download(init_date_update, end_date_update)
    
    for file_nc, list_date in zip(list_ncs, list_dates):
        if file_nc[-3:] in ["bz2"]:
            continue        
        NC   = xr.open_dataset(file_nc)
        TAUX = getattr(NC,"surface_downward_eastward_stress")
        TAUY = getattr(NC,"surface_downward_northward_stress")
        date    = pd.date_range( list_date, periods=1, freq="D")
        lon_old = np.roll(TAUX.longitude.values, int(TAUX.shape[-1]/2))
        
        TAUX_32 = create_xarray( np.roll(TAUX.values.reshape(1,TAUX.latitude.shape[0], lon_old.shape[0]), int(TAUX.shape[-1]/2), axis=-1) ,
                                date, TAUX.latitude.values, np.where( lon_old < 0, lon_old + 360, lon_old), 
                                "time", "lat", "lon").sel(lat=slice(-30.5, 30.5), lon=slice(89.5, 300.5))
        TAUY_32 = create_xarray( np.roll(TAUY.values.reshape(1,TAUX.latitude.shape[0], lon_old.shape[0]), int(TAUX.shape[-1]/2), axis=-1) ,
                                date, TAUX.latitude.values, np.where( lon_old < 0, lon_old + 360, lon_old), 
                                "time", "lat", "lon").sel(lat=slice(-30.5, 30.5), lon=slice(89.5, 300.5))
        DATASET = xr.Dataset({"taux": TAUX_32, "tauy": TAUY_32})
        DATASET.to_netcdf(file_nc.split("00_")[0]+".nc")    
        
if __name__ == "__main__":
    main()    