#! /usr/bin/bash
VISROOT=/scratch/EASvis
SCRIPTROOT=$VISROOT/wrangle
ANIMROOT=$VISROOT/animate

START=$SECONDS

shopt -s expand_aliases
alias Python='export PATH=$PATH:/opt/anaconda/bin; source activate adm; python'

# Create new directory for logs
LOGPATH=$(date +"/scratch/EASvis/logs/%Y%m%d_%H%M/")
mkdir -p $LOGPATH

echo "------------------------------------------------"
echo "Processing script run; logged to $LOGPATH"

# start off sequence of scripts outputting to appropriate log files

# ------------------------------------------------------
# -- Fetch data
echo "Fetching GFS data."
$SCRIPTROOT/wrangle_gfs.sh >& ${LOGPATH}wrangle_gfs.txt &

wait

# ------------------------------------------------------
# -- Process raw data to netcdfs
echo "Processing grib data to netcdfs."

# GFS forecasts
Python $SCRIPTROOT/process_archive.py >& ${LOGPATH}process_gfs_forecast.txt &

# GFS analysis
Python $SCRIPTROOT/process_gfs_analysis.py >& ${LOGPATH}process_gfs_analysis.txt &

wait

# ------------------------------------------------------
# -- Produce animations/graphics
echo "Producing animations."

# T 850 animation
Python $ANIMROOT/anim_t8.py >& ${LOGPATH}anim_t8.txt &

# Z 500 animation
Python $ANIMROOT/anim_z500.py >& ${LOGPATH}anim_z5.txt &

# gamefarm road animation
Python $VISROOT/gamefarm_climate/ithaca_temperature_annual_cycle_fcst_subplots_for_hallway_vis.py >& ${LOGPATH}gamefarm_clim.txt &

wait

# ------------------------------------------------------
# -- Transfer to hallway pi
echo "Copying graphics to pi."
$SCRIPTROOT/copyanims.sh >& ${LOGPATH}copyanims.txt

# ------------------------------------------------------
# -- Print summary

END=$(date +"%Y%m%d_%H%M")
ELAPSED=$(date -u -d "0 $SECONDS seconds - $START seconds" +"%H:%M:%S" )

echo "Processing completed at ${END}. ${ELAPSED} elapsed." 
