#!/bin/bash

export MODEL="ASCAT"
export DATE="2022-08-07"
export OUTPUT="/home/brayan/DATA/Modelo-Multimodal-de-Ondas/raw_data/$MODEL/"
bash ./run_raw_data.sh
# bash ./run_process_data.sh