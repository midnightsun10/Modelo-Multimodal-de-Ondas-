#!/bin/bash

path=`pwd`

# export INPUT="/home/brayan/DATA/Modelo-Multimodal-de-Ondas/raw_data/$MODEL"
# export OUTPUT="/home/brayan/DATA/Modelo-Multimodal-de-Ondas/process/$MODEL/"
# export CURRENT_DATE="2022-08-03"

# cd ./process_data

chmod u+rwx ./process_data/fill_missing.py
pass=$(./process_data/fill_missing.py)
wait 

if [ "$pass"="true" ]
then
    chmod u+rwx ./process_data/anomalies.py
    ./process_data/anomalies.py
    echo "Aqui termina"
fi