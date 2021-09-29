#! /usr/bin/bash
VISROOT=/scratch/EASvis
SCRIPTROOT=$VISROOT/wrangle
ANIMROOT=$VISROOT/animate

# Create new directory for logs
LOGPATH=$(date +"/scratch/EASvis/logs/%Y%m%d_%H%M/")
mkdir -p $LOGPATH

echo "Processing script run; output logged to $LOGROOT."

# start off sequence of scripts outputting to appropriate log files
echo "Fetching GFS data."
$SCRIPTROOT/wrangle_gfs.sh >& ${LOGROOT}_wrangle_gfs.txt 

echo "Processing grib data to netcdfs."
# GFS forecasts
export PATH=$PATH:/opt/anaconda/bin; source activate adm; python $SCRIPTROOT/process_archive.py >& ${LOGPATH}process_gfs_forecast.txt

# GFS analysis
export PATH=$PATH:/opt/anaconda/bin; source activate adm; python $SCRIPTROOT/process_gfs_analysis.py >& ${LOGPATH}process_gfs_analysis.txt

# TODO: parallelize animations?
echo "Producing animations."

# T 850 animation
export PATH=$PATH:/opt/anaconda/bin; source activate adm; python $ANIMROOT/anim_t8.py >& ${LOGPATH}anim_t8.txt

# gamefarm road animation
export PATH=$PATH:/opt/anaconda/bin; source activate adm; python $VISROOT/gamefarm_climate/ithaca_temperature_annual_cycle_fcst_subplots_for_hallway_vis.py >& ${LOGPATH}gamefarm_clim.txt

# TODO: copy animations to pi
$SCRIPTROOT/copyanims.sh >& ${LOGROOT}_copyanims.txt

