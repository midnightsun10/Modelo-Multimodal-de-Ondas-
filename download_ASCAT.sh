#!/bin/bash

export OUTPUT="/home/brayan/DATA/Modelo-Multimodal-de-Ondas/raw_data/"
export INIT_DATE="2007-03-21"
export END_DATE="2007-03-24"

chmod u+rwx ./raw_data/generate_urls.py
./raw_data/generate_urls.py

cd "$OUTPUT"
sh *txt


