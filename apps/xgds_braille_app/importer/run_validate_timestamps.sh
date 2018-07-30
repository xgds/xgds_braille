#!/bin/bash

# To use this, call it with 2 arguments.
# The first is the parent directory containing directories to analyze
# The second (optional) is the output file for the times.
# Note this will APPEND to the output file.

dir=$1
echo "Validating times for $dir"

dirname=$(basename $dir)
timefile=/tmp/$dirname.txt
if [ $# -eq 2 ]
  then
    timefile=$2
fi
touch $timefile
echo "writing to: $timefile"

for d in $dir*/; do
  echo "./validate_timestamps.py -q -c timestamp_validator_config.yaml $d >> $timefile"
  ./validate_timestamps.py -q -c timestamp_validator_config.yaml $d >> $timefile
done