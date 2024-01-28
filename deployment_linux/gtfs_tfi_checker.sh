#!/bin/bash

# This script checks if the GTFS data has been updated and if so, updates the database

URL="https://www.transportforireland.ie/transitData/Data/GTFS_Realtime.zip"

DOWNLOAD_DIR="/home/niall/SimplyTransport/gtfs_data/TFI/gtfs_checker"
EXISTING_DIR="/home/niall/SimplyTransport/gtfs_data/TFI"

FORCE_OPERATION=false

# Check if the argument -f is provided
if [ "$1" == "-f" ]; then
    FORCE_OPERATION=true
    echo "Bypassing file creation checks - force updating"
    echo
fi

wget -nv -N "$URL" -P "$DOWNLOAD_DIR"

unzip -j -o "$DOWNLOAD_DIR/GTFS_Realtime.zip" agency.txt -d "$DOWNLOAD_DIR"

CREATION_DATE=$(stat -c %y "$DOWNLOAD_DIR/agency.txt")
EXISTING_DIR_DATE=$(stat -c %y "$EXISTING_DIR/agency.txt")

echo
echo "CREATION_DATE: $CREATION_DATE"
echo "EXISTING_DIR_DATE: $EXISTING_DIR_DATE"
echo

if  [ "$FORCE_OPERATION" == true ] || [[ "$CREATION_DATE" > "$EXISTING_DIR_DATE" ]]; then
	unzip -o "$DOWNLOAD_DIR/GTFS_Realtime.zip" -d "$EXISTING_DIR"
    cd /home/niall/SimplyTransport && echo y | /home/niall/SimplyTransport/venv/bin/litestar importgtfs # This uses the CLI command

fi