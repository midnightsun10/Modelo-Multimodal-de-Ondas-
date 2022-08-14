#!/bin/bash

path=`pwd`
# date_current=$(date +'%Y-%m-%d')
# export OUTPUT="/home/brayan/DATA/Modelo-Multimodal-de-Ondas/raw_data/$MODEL/"
# export DATE="2022-08-03"  #$(date --date="yesterday" +%Y-%m-%d) 
# export END_DATE="2022-08-03"   #$(date --date="yesterday" +%Y-%m-%d) 

chmod u+rwx ./raw_data/generate_urls.py
./raw_data/generate_urls.py

cd "$OUTPUT"
sh *txt

wait

echo "continua"

cd "$path"
chmod u+rwx ./raw_data/modify_data.py
./raw_data/modify_data.py

[ -e $OUTPUT*/*/*_daily-ifremer-L3-MWF-GLO.nc ] && rm $OUTPUT*/*/*_daily-ifremer-L3-MWF-GLO.nc






# while ! [[ "$INIT_DATE" > "$END_DATE" ]]
# do
#     echo "$INIT_DATE"

#     ## Split and join
#     IFS="-" read -a params <<< "$INIT_DATE"
#     start_join=""
#     for j in "${params[@]}"; do
#         start_join+="$j"
#     done
#     echo "$start_join"

#     ################

#     INIT_DATE=$(date -d "$INIT_DATE +1 day" +%F)
#     echo "$INIT_DATE"
# done



