#!/bin/bash
echo "Se imprime"

export PATH_MAIN=$1
export MODEL="ASCAT"
export DATE="2022-08-14"
export PATH_RAW_DATA="/home/brayan/DATA/Modelo-Multimodal-de-Ondas/raw_data/$MODEL/"
export PATH_PROCESSED_DATA="/home/brayan/DATA/Modelo-Multimodal-de-Ondas/process/$MODEL/"

bash "$PATH_MAIN"run_raw_data.sh
bash "$PATH_MAIN"run_process_data.sh

echo "termina"
