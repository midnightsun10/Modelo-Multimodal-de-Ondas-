#!/usr/bin/env python

import os
import glob
import sys
import numpy as np
import xarray as xr
import pandas as pd
sys.path.append("/home/brayan/mnsun/")
from utils import check_dir

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

def wind_to_tau(u_, v_):
    """
    Se crea la variable esfuerzo de vientos a partir de los vientos
    
    Output: Data Xarray en formato float_32
    """
    rho   = 1.22
    C_d   = 0.0013
    taux_ = rho * C_d * np.sqrt(u_**2 + v_**2)*u_
    tauy_ = rho * C_d * np.sqrt(u_**2 + v_**2)*v_
    
    return taux_, tauy_

def main():
    OUTPUT_DIR       = str(os.environ["PATH_RAW_DATA"])
    date_update      = str(os.environ["DATE"])
        # end_date_update  = str(os.environ["END_DATE"])
            
    if OUTPUT_DIR.split("/")[-2] == "ASCAT":

        list_ncs   = [glob.glob(OUTPUT_DIR+"TAU/"+date_.split("-")[0]+"/"+"".join(date_.split("-"))+"*_daily-ifremer-L3-MWF-GLO.*")[0] for date_ in dates_download(date_update, date_update)]
        list_dates = dates_download(date_update, date_update)
        
        for file_nc, list_date in zip(list_ncs, list_dates):
            if file_nc[-3:] in ["bz2"]:
                # print("Corrupted data")
                # os.environ["corrupted"] = "true"
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
    
    elif OUTPUT_DIR.split("/")[-2] == "NCEP":
        file_update_u      = getattr(xr.open_dataset(OUTPUT_DIR + "WIND/" + date_update.split("-")[0] + "/"+date_update.split("-")[0]+ "_uwnd_daily-ncep.nc"), "uwnd")
        file_update_v      = getattr(xr.open_dataset(OUTPUT_DIR + "WIND/" + date_update.split("-")[0] + "/"+date_update.split("-")[0]+ "_vwnd_daily-ncep.nc"), "vwnd")
        
        U_32               = create_xarray( file_update_u.values[:,::-1,:],
                                            file_update_u.time, file_update_u.lat.values[::-1], file_update_u.lon, 
                                            "time", "lat", "lon").sel(lat=slice(-31.5, 31.5), lon=slice(89.5, 300.5))

        V_32               = create_xarray( file_update_v.values[:,::-1,:],
                                            file_update_v.time, file_update_v.lat.values[::-1], file_update_v.lon, 
                                            "time", "lat", "lon").sel(lat=slice(-31.5, 31.5), lon=slice(89.5, 300.5))     
        
        check_dir(OUTPUT_DIR + "TAU/" + date_update.split("-")[0]+"/")

        for t, date_ in enumerate(U_32.time.values):
            TAUX, TAUY   = wind_to_tau( U_32.isel(time=t), V_32.isel(time=t))
            date_compact = "".join(str(date_)[:10].split("-"))
            DATASET      = xr.Dataset({"taux": TAUX, "tauy": TAUY})
            DATASET.to_netcdf(OUTPUT_DIR + "TAU/" + date_compact[:4] + "/" + date_compact + ".nc")
           
if __name__ == "__main__":
    main()    