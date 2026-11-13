#!/bin/bash
# Author: Darren
#
# Utility script to create an "AoC" folder for the specified year, based on the template folder.
# Usage from the project root:
#   scripts/create_year.sh <year> [days]
#
# Examples:
#   scripts/create_year.sh 2026       # Creates 12 day folders (AoC 2025+ format)
#   scripts/create_year.sh 2020 25    # Creates 25 day folders (legacy format)

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <year> [days]"
    echo "Creates src/AoC_<year>/d01..d<days> from src/template_folder/template.py (default: 12 days)."
    exit 1
fi

YEAR="$1"
DAYS="${2:-12}"

if [[ ! "$YEAR" =~ ^[0-9]{4}$ ]]; then
    echo "Error: Year '$YEAR' must be a 4-digit integer."
    exit 1
fi

if [[ ! "$DAYS" =~ ^[0-9]+$ ]] || [ "$DAYS" -lt 1 ] || [ "$DAYS" -gt 25 ]; then
    echo "Error: Days '$DAYS' must be an integer between 1 and 25."
    exit 1
fi

DEST_FOLDER="src/AoC_${YEAR}"
TEMPLATE_FOLDER="src/template_folder"
TEMPLATE_FILE="${TEMPLATE_FOLDER}/template.py"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Template file '$TEMPLATE_FILE' not found. Run this script from the repository root."
    exit 1
fi

for i in $(seq 1 "$DAYS"); do
    DAY_PREFIX=$(printf "d%02d" "$i")
    DAY_FOLDER="${DEST_FOLDER}/${DAY_PREFIX}"

    mkdir -p "${DAY_FOLDER}/input"
    touch "${DAY_FOLDER}/input/sample_input_part_1.txt"

    NEW_PYTHON_FILE="${DAY_FOLDER}/${DAY_PREFIX}.py"
    sed -e "s/^YEAR: int = 2026$/YEAR: int = ${YEAR}/" \
        -e "s/^DAY: int = 1$/DAY: int = ${i}/" \
        -e "s|adventofcode.com/2026/day/1|adventofcode.com/${YEAR}/day/${i}|" \
        "${TEMPLATE_FILE}" > "${NEW_PYTHON_FILE}"
done

echo "Successfully created ${DAYS} day folder(s) in ${DEST_FOLDER}."
