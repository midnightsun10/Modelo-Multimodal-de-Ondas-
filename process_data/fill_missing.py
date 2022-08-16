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

def main():

    INPUT_DIR        = str(os.environ["PATH_RAW_DATA"]) #"/home/brayan/DATA/Modelo-Multimodal-de-Ondas/raw_data/"
    OUTPUT_DIR       = str(os.environ["PATH_PROCESSED_DATA"]) #"/home/brayan/DATA/Modelo-Multimodal-de-Ondas/process/ASCAT/"
    date_update      = str(os.environ["DATE"]) #"2020-06-01"
    
    if OUTPUT_DIR.split("/")[-2] == "ASCAT":    
        lag              = 30

        date_update_back = str(pd.date_range( date_update, periods=1, freq="D").shift(-lag, freq="D").values[0])[:10]
        dates_update     = dates_download( date_update_back, date_update)

        file_ascat = []
        for date_ in dates_update:
            file_ascat += glob.glob(INPUT_DIR+f"TAU/"+date_.split("-")[0]+"/"+"".join(date_.split("-"))+".nc")
            
        files_exists = [asc_[-11:-7] +"-"+ asc_[-7:-5] +"-"+ asc_[-5:-3] for asc_ in file_ascat]
        files_fill   = list(set(dates_update) - set(files_exists))

        if file_ascat[-1][-11:] !=  "".join(dates_update[-1].split("-")) + ".nc":
            print("El ultimo dia no se considera como actualizacion")
            os.environ["pass"] = "false"
        else:
            print("pass")
            os.environ["pass"] = "true"
            DS_ASCAT   = xr.open_mfdataset(file_ascat, parallel=True)
            dates_fill = pd.date_range(date_update_back, date_update, freq="D")
            TAUX_MISS  = create_xarray(DS_ASCAT.taux.values, DS_ASCAT.time, DS_ASCAT.lat, DS_ASCAT.lon, "time", "lat", "lon")
            TAUX_FILL  = TAUX_MISS.interp(time=dates_fill, method="linear").interpolate_na(dim="time")
            ds_MOM     = xr.Dataset(
                                    {"lon": np.arange( 90, 299, 1), "lat":np.arange( -30, 30.5, 0.5)}
                                )    
            regridder  = xe.Regridder( TAUX_FILL, ds_MOM, "bilinear")
            regridder.clean_weight_file()
            TAUX_FILL_MOM    = regridder(TAUX_FILL)
            TAUX_FILL_32_MOM = create_xarray(TAUX_FILL_MOM.values, TAUX_FILL_MOM.time, np.float32(ds_MOM.lat), np.float32(ds_MOM.lon), "time", "lat", "lon")
            
            TAUY_MISS        = create_xarray(DS_ASCAT.tauy.values, DS_ASCAT.time, DS_ASCAT.lat, DS_ASCAT.lon, "time", "lat", "lon")
            TAUY_FILL        = TAUY_MISS.interp(time=dates_fill, method="linear").interpolate_na(dim="time")
            TAUY_FILL_MOM    = regridder(TAUY_FILL)
            TAUY_FILL_32_MOM = create_xarray(TAUY_FILL_MOM.values, TAUY_FILL_MOM.time, np.float32(ds_MOM.lat), np.float32(ds_MOM.lon), "time", "lat", "lon")
            
            DATASET = xr.Dataset({"taux": TAUX_FILL_32_MOM, "tauy": TAUY_FILL_32_MOM})
            check_dir(OUTPUT_DIR+ "TAU/"+str(date_)[:4]+"/")
            DATASET.isel(time=-1).to_netcdf(OUTPUT_DIR+"TAU/"+str(date_)[:4]+"/"+"".join(str(date_)[:10].split("-"))+".nc")
            
            if len(files_fill) != 0:
                for date_fill in files_fill:
                    DATASET.sel(time=date_fill).to_netcdf(OUTPUT_DIR+"TAU/"+str(date_fill)[:4]+"/"+"".join(str(date_fill)[:10].split("-"))+".nc")      

    elif OUTPUT_DIR.split("/")[-2] == "NCEP":
        dates_for_update = dates_download(date_update.split("-")[0]+"-01-01",date_update ) 
        file_ncep = []
        for date_ in dates_for_update:
            file_ncep += glob.glob(INPUT_DIR+f"TAU/"+date_update.split("-")[0]+"/"+"".join(date_.split("-"))+".nc")
            
        if file_ncep[-1][-11:] !=  "".join(dates_for_update[-1].split("-")) + ".nc":
            print("Nada para actualizar")
            print("false")
        else:
            print("true")
            # os.putenv("pass", "true")
            # os.system("export pass=true")
            # myenv = os.environ.copy()
            # myenv['pass'] = 'true'
            # os.environ["pass"] = "true"
            DS_NCEP    = xr.open_mfdataset(file_ncep,  concat_dim = 'time', parallel=True)
            dates_fill = pd.date_range(date_update.split("-")[0]+"-01-01", date_update, freq="D")
            TAUX_MISS  = create_xarray(DS_NCEP.taux.values, DS_NCEP.time, DS_NCEP.lat, DS_NCEP.lon, "time", "lat", "lon")
            TAUX_FILL  = TAUX_MISS.interp(time=dates_fill, method="linear").interpolate_na(dim="time")
            ds_MOM     = xr.Dataset(
                                    {"lon": np.arange( 90, 299, 1), "lat":np.arange( -30, 30.5, 0.5)}
                                    )        
            regridder  = xe.Regridder( TAUX_FILL, ds_MOM, "bilinear")
            regridder.clean_weight_file()
            TAUX_FILL_MOM    = regridder(TAUX_FILL)
            TAUX_FILL_32_MOM = create_xarray(TAUX_FILL_MOM.values, TAUX_FILL_MOM.time, np.float32(ds_MOM.lat), np.float32(ds_MOM.lon), "time", "lat", "lon")    

            TAUY_MISS  = create_xarray(DS_NCEP.tauy.values, DS_NCEP.time, DS_NCEP.lat, DS_NCEP.lon, "time", "lat", "lon")
            TAUY_FILL  = TAUY_MISS.interp(time=dates_fill, method="linear").interpolate_na(dim="time")  
            TAUY_FILL_MOM    = regridder(TAUY_FILL)
            TAUY_FILL_32_MOM = create_xarray(TAUY_FILL_MOM.values, TAUY_FILL_MOM.time, np.float32(ds_MOM.lat), np.float32(ds_MOM.lon), "time", "lat", "lon")        
            DATASET          = xr.Dataset({"taux": TAUX_FILL_32_MOM, "tauy": TAUY_FILL_32_MOM})
            check_dir(OUTPUT_DIR+ "TAU/"+str(date_update)[:4]+"/")
            
            for t, date_2 in enumerate(DATASET.time.values):
                date_compact = "".join(str(date_2)[:10].split("-"))
                DATASET.isel(time=t).to_netcdf(OUTPUT_DIR + "TAU/" + date_compact[:4] + "/" + date_compact + ".nc")    
if __name__ == "__main__":
    main()      