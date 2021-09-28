#! /usr/bin/bash
SCRIPTROOT=/scratch/EASvis/wrangle
ANIMROOT=/scratch/EASvis/animate

# build logfile root name
LOGROOT=$(date +"/scratch/EASvis/logs/%Y%m%d_%H%m")

echo "Processing script run; output logged to $LOGROOT."

# start off sequence of scripts outputting to appropriate log files
echo "Fetching GFS data."
$SCRIPTROOT/wrangle_gfs.sh >& ${LOGROOT}_wrangle_gfs.txt 

echo "Processing grib data to netcdfs."
# GFS forecasts
export PATH=$PATH:/opt/anaconda/bin; source activate adm; python $SCRIPTROOT/process_archive.py >& ${LOGROOT}_process_gfs_forecast.txt

# GFS analysis
export PATH=$PATH:/opt/anaconda/bin; source activate adm; python $SCRIPTROOT/process_gfs_analysis.py >& ${LOGROOT}_process_gfs_analysis.txt

# TODO: parallelize animations?
echo "Producing animations."

# T 850 animation
export PATH=$PATH:/opt/anaconda/bin; source activate adm; python $ANIMROOT/anim_t8.py >& ${LOGROOT}_anim_t8.txt

