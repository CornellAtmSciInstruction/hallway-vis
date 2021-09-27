#! /usr/bin/bash
SCRIPTROOT=/scratch/EASvis/scripts

# build logfile root name
LOGROOT=$(date +"/scratch/EASvis/logs/%Y%m%d_%H%m")

echo "Processing script run; output logged to $LOGROOT."

# start off sequence of scripts outputting to appropriate log files
echo "Fetching GFS data."
$SCRIPTROOT/wrangle_gfs.sh >& ${LOGROOT}_wrangle_gfs.txt 

echo "Processing grib data to netcdfs."
export PATH=$PATH:/opt/anaconda/bin; source activate adm; python $SCRIPTROOT/process_archive.py >& ${LOGROOT}_process_archive.txt

echo "Producing animations."
# parallelize animations?
