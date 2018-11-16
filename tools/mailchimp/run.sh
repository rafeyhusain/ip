#!/usr/bin/env bash

DATE=$(date +"%Y-%m-%d")
OUTPUT_DIR="/srv/ftp/mailchimp/${DATE}/"

if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
fi

cat mailing-list.cfg | \
    awk -F'=' -v output_dir="$OUTPUT_DIR" '{print $1" "$2" "output_dir}' | \
    xargs -I{} python backup.py {} 2>${OUTPUT_DIR}error.log

