#!/bin/bash

# This script checks if the TFI stop features data has been updated and if so, updates the database

URL="https://www.transportforireland.ie/transitData/Data/ptims.zip"

DOWNLOAD_DIR="/home/niall/SimplyTransport/gtfs_data/TFI/gtfs_checker"
EXISTING_DIR="/home/niall/SimplyTransport/gtfs_data/TFI"

FORCE_OPERATION=false

# Check if the argument -f is provided
if [ "$1" == "-f" ]; then
    FORCE_OPERATION=true
    echo "Bypassing file creation checks - force updating"
fi

wget -nv -N "$URL" -P "$DOWNLOAD_DIR"

unzip -j -o "$DOWNLOAD_DIR/ptims.zip" stops.geojson -d "$DOWNLOAD_DIR"

CREATION_DATE=$(stat -c %y "$DOWNLOAD_DIR/stops.geojson")
EXISTING_DIR_DATE=$(stat -c %y "$EXISTING_DIR/stops.geojson")

if  [ "$FORCE_OPERATION" == true ] || [[ "$CREATION_DATE" > "$EXISTING_DIR_DATE" ]]; then
	unzip -o "$DOWNLOAD_DIR/ptims.zip" -d "$EXISTING_DIR"
    cd /home/niall/SimplyTransport && echo y | /home/niall/SimplyTransport/venv/bin/litestar importstopfeatures # This uses the CLI command
    
fi