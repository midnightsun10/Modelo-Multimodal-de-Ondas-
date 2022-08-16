#!/usr/bin/env python

import os
import sys
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

def build_sentences_ascat(list_dates_, output_):
    """
    Fincion que permite crear las sentencias de descarga y descompresion en un archivo txt a partir del url fuente
    """
    base_ = "wget -cO - ftp://ftp.ifremer.fr/ifremer/cersat/products/gridded/MWF/L3/ASCAT/Daily/Netcdf/{year}/{month}/{day}/{year}{month}{day}00* > {output}/TAU/{year}/{year}{month}{day}00_daily-ifremer-L3-MWF-GLO.nc.bz2 && bzip2 -d ./TAU/{year}/{year}{month}{day}00*.bz2"
    with open(output_ + "download.txt", "w") as f:        
        for date_ in list_dates_:
            check_dir(output_ + "TAU/" + date_.split("-")[0]+"/")
            f.write(base_.format(year=date_.split("-")[0], month=date_.split("-")[1], day=date_.split("-")[-1], output = output_)+ "\n")

def build_sentences_ncep(date_, output_):
    """
    Fincion que permite crear las sentencias de descarga y descompresion en un archivo txt a partir del url fuente para ncep
    """
    base_u = "wget -cO - https://downloads.psl.noaa.gov//Datasets/ncep.reanalysis/Dailies/surface_gauss/uwnd.10m.gauss.{year}.nc > {output}/WIND/{year}/{year}_uwnd_daily-ncep.nc" 
    base_v = "wget -cO - https://downloads.psl.noaa.gov//Datasets/ncep.reanalysis/Dailies/surface_gauss/vwnd.10m.gauss.{year}.nc > {output}/WIND/{year}/{year}_vwnd_daily-ncep.nc" 
    check_dir(output_ + "WIND/" + date_.split("-")[0]+"/")
    with open(output_ + "download.txt", "w") as f:
        f.write(base_u.format(year=date_.split("-")[0], output = output_)+ "\n")
        f.write(base_v.format(year=date_.split("-")[0], output = output_)+ "\n")
            
def main():
    OUTPUT_DIR       = str(os.environ["PATH_RAW_DATA"])
    date_update      = str(os.environ["DATE"])
    # end_date_update  = str(os.environ["END_DATE"])
    if OUTPUT_DIR.split("/")[-2] == "ASCAT":
        build_sentences_ascat(dates_download(date_update, date_update) ,OUTPUT_DIR)
    elif OUTPUT_DIR.split("/")[-2] == "NCEP":
        build_sentences_ncep( date_update, OUTPUT_DIR)

if __name__ == "__main__":
    main()