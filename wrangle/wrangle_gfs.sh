#! /usr/bin/bash

# Add path to Google cloud utility script
PATH=/scratch/EASvis/gsutil:$PATH

fetch_date() {
   DATE=$1
   for HOUR in 00 06 12 18;
   do
      echo "------------------------------------"
      echo "Syncing forecasts for ${HOUR}Z $DATE"

      # GFS Analysis
      # Create local path if needed
      MONTH=${DATE:0:6}
      LOCALPATH=/scratch/EASvis/data/GFS_analysis/$MONTH/grib/
      mkdir -p $LOCALPATH

      # Check if analysis is available
      if gsutil -q stat gs://global-forecast-system/gfs.$DATE/$HOUR/atmos/gfs.t${HOUR}z.pgrb2.0p25.anl ; then
         # Copy analysis file if not currently present
         gsutil cp -n gs://global-forecast-system/gfs.$DATE/$HOUR/atmos/gfs.t${HOUR}z.pgrb2.0p25.anl $LOCALPATH/gfs.${DATE}.t${HOUR}z.pgrb2.0p25.anl
      fi

      # GFS Forecasts
      # Create local path if needed
      LOCALPATH=/scratch/EASvis/data/GFS/$DATE/$HOUR/grib/
      mkdir -p $LOCALPATH

      # Check if forecasts are available
      if gsutil -q stat gs://global-forecast-system/gfs.$DATE/$HOUR/atmos/gfs.t${HOUR}z.pgrb2.0p25.f120 ; then
         # Copy any forecast files not currently present
         gsutil cp -n gs://global-forecast-system/gfs.$DATE/$HOUR/atmos/gfs.t${HOUR}z.pgrb2.0p25.f0?? $LOCALPATH
         gsutil cp -n gs://global-forecast-system/gfs.$DATE/$HOUR/atmos/gfs.t${HOUR}z.pgrb2.0p25.f1[0-2]? $LOCALPATH
      fi
   done
}

# Loop over today and previous two days
for d in {0..2}
do
   # Get UTC date in YYYYMMDD format
   DAY=$(TZ='UTC' date -d "-$d day" +"%Y%m%d")

   fetch_date $DAY
done

# Process forecast data
#export PATH=$PATH:/opt/anaconda/bin; source activate adm; python /scratch/EASvis/scripts/process_archive.py
