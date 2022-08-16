#!/bin/bash

export MODEL="NCEP"
export DATE="2022-08-02"
export PATH_RAW_DATA="/home/brayan/DATA/Modelo-Multimodal-de-Ondas/raw_data/$MODEL/"
export PATH_PROCESSED_DATA="/home/brayan/DATA/Modelo-Multimodal-de-Ondas/process/$MODEL/"
bash ./run_raw_data.sh
bash ./run_process_data.sh
