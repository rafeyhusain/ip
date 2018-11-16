#!/usr/bin/env bash

DATE=$(date +"%Y%m%d%H%M")

OUTPUT=/srv/ftp/sorticorn

mkdir -p ${OUTPUT}/${DATE}

for CC in hk id my ph sg 
do
    # brand

    for BRAND in louis-vuitton prada samsung nike daiso puma adidas swarovski
    do
        python products.py --size 100000 --country ${CC} --brand ${BRAND} > ${OUTPUT}/${DATE}/${CC}-products-${BRAND}.csv 2>> ${OUTPUT}/${DATE}/error.log
    done

    # category

    if [ ${CC} = id ]; then
        CATEGORIES=(komputer ponsel-tablet video-game kamera-foto tv-video-dvd)
    else
        CATEGORIES=(clothing bags bags/handbags shoes shoes/sports-shoes shoes/sneakers phones-tablets watches clothing/saris clothing/dresses)
    fi

    for CATEGORY in ${CATEGORIES[@]}
    do
        category_file=$( echo "$CATEGORY" | tr '/' ' ')
        python products.py --size 100000 --country ${CC} --category ${CATEGORY} > ${OUTPUT}/${DATE}/${CC}-products-"${category_file}".csv 2>> ${OUTPUT}/${DATE}/error.log
    done

    # brand & category

    declare -A BRAND_CATEGORY=(['prada']='bags' ['nike']='shoes' ['michael-kors']='bags' ['louis-vuitton']='bags' ['gucci']='shoes' ['puma']='shoes' ['fila']='shoes' ['toms']='shoes' ['lacoste']='shoes' ['gucci']='clothing'  ['chanel']='bags' ['longchamp']='bags' ['coach']='bags' ['gucci']='bags' ['yves-saint-laurent']='bags' ['casio']='watches' ['omega']='watches')
    for BRAND in "${!BRAND_CATEGORY[@]}";
    do
        category=${BRAND_CATEGORY[${BRAND}]}
        category_file=$( echo "$category" | tr '/' ' ')
        python products.py --size 100000 --country ${CC} --brand ${BRAND} --category ${category} > ${OUTPUT}/${DATE}/${CC}-products-${BRAND}-"${category_file}".csv 2>> ${OUTPUT}/${DATE}/error.log
    done
done
