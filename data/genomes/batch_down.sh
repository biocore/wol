#!/bin/bash
# Batch download genome data from the NCBI FTP server.
# Usage: bash batch_down.sh download.list

while read url
do
    id='G'$(basename $url | cut -f1 -d'.' | cut -f2 -d'_')
    ext=$(echo $url | rev | cut -f1-2 -d'.' | rev)
    wget -c $url -O $id.$ext
done < $1
