#!/bin/bash
# Author: Darren
#
# Utility script to create an "AoC" folder for the specified year, based on the template folder
# To use the script from the project root:
# scripts/create_year.sh <year>
#
# E.g.
# scripts/create_year.sh 2023

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <year>"
    echo "Enter a year to use as a path suffix"
    exit 1
fi

YEAR=$1
# Assuming the script is run from the project root.
DEST_FOLDER="src/AoC_$YEAR"
TEMPLATE_FOLDER="src/template_folder"
TEMPLATE_FILE="${TEMPLATE_FOLDER}/template.py"
TEMPLATE_INPUT_FOLDER="${TEMPLATE_FOLDER}/input"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Template file '$TEMPLATE_FILE' not found."
    exit 1
fi

if [ ! -d "$TEMPLATE_INPUT_FOLDER" ]; then
    echo "Error: Template input folder '$TEMPLATE_INPUT_FOLDER' not found."
    exit 1
fi

for i in $(seq 1 25); do
    DAY_PREFIX=$(printf "d%02d" "$i")
    DAY_FOLDER="${DEST_FOLDER}/${DAY_PREFIX}"
    
    mkdir -p "${DAY_FOLDER}"

    NEW_PYTHON_FILE="${DAY_FOLDER}/${DAY_PREFIX}.py"
    # Replace the hardcoded year in the template file with the provided year.
    # This updates the 'YEAR' variable and the year in the Advent of Code URL.
    sed -e "s/YEAR = 2017/YEAR = $YEAR/" \
        -e "s/adventofcode.com\/2023\/day\//adventofcode.com\/$YEAR\/day\//" \
        "${TEMPLATE_FILE}" > "${NEW_PYTHON_FILE}"

    # Also copy the input folder
    cp -r "${TEMPLATE_INPUT_FOLDER}" "${DAY_FOLDER}/"
done

echo "Successfully created files for AoC $YEAR."
