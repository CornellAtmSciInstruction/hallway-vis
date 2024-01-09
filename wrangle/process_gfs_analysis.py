import os, sys, glob
import shutil
import re
import datetime

import xarray as xr

arch_root = '/scratch/EASvis/data/GFS_analysis/'

def get_gribpath(month):
   return arch_root + '%s/grib/' % (month, )

def get_ncpath(month):
   return arch_root + '%s/netcdf/' % (month, )

def process_isobaric_level(gribfn, ncfn, var, plev):
# {{{
   vname = var + '%d' % plev

   gribkwa = dict(filter_by_keys = dict(typeOfLevel = 'isobaricInhPa', \
                                        shortName=var))

   ds = xr.open_dataset(gribfn, engine='cfgrib', backend_kwargs=gribkwa)

   v = ds.data_vars[var].sel(isobaricInhPa = plev).rename(vname)

   enc = {vname : dict(dtype="float32", zlib=True, complevel=9)}

   print("Writing to %s" % ncfn)
   v.to_netcdf(ncfn, encoding=enc)
# }}}

def process_pwat(gribfn, ncfn):
# {{{
   vname = 'pwat'

   gribkwa = dict(filter_by_keys = dict(cfVarName = 'pwat'))

   ds = xr.open_dataset(gribfn, engine='cfgrib', backend_kwargs=gribkwa)

   var = ds.pwat.rename(vname)

   enc = {vname : dict(dtype="float32", zlib=True, complevel=9)}

   print("Writing to %s" % ncfn)
   var.to_netcdf(ncfn, encoding=enc)
# }}}

def process_prmsl(gribfn, ncfn):
# {{{
   vname = 'prmsl'

   gribkwa = dict(filter_by_keys = dict(cfVarName = 'prmsl'))

   ds = xr.open_dataset(gribfn, engine='cfgrib', backend_kwargs=gribkwa)

   var = ds.prmsl.rename(vname)

   enc = {vname : dict(dtype="float32", zlib=True, complevel=9)}

   print("Writing to %s" % ncfn)
   var.to_netcdf(ncfn, encoding=enc)
# }}}

def process_gfs_to_nc(month):
# {{{
   gribpath = get_gribpath(month)
   ncpath = get_ncpath(month)

   if not os.path.exists(ncpath):
      os.makedirs(ncpath)

   # Get list of available grib files
   filelist = glob.glob(gribpath + '*anl')
   filelist.sort()

   #plev_vars = {'t': 850}
   plev_vars = {'t': 850, 'gh': 500}

   pattern = re.compile('gfs.(?P<date>[0-9]{8}).t(?P<hour>[0-9]{2})z')

   for gribfn in filelist:
      # Extract date and hour from filename
      mt = pattern.match(os.path.basename(gribfn))
      if mt is None:
         print('Filename %s is unrecognized. Skipping.' % gribfn)
         continue

      date = mt.group('date')
      hour = mt.group('hour')

      #################################
      # Extract isobaric data
      #############
      for v, pr in plev_vars.items():
         vname = v + '%d' % pr
         plfn = ncpath + 'gfs.%s.t%sz.%s.0p25.nc' % (date, hour, vname)

         if not os.path.exists(plfn):
            try:
               process_isobaric_level(gribfn, plfn, v, pr)
            except Exception as e:
               print("Failed to process single-level %s. Exception: '%s'" % (v, e))

      #################################
      # Extract precipitable water
      #############
      vname = 'pwat'
      vfn = ncpath + 'gfs.%s.t%sz.%s.0p25.nc' % (date, hour, vname)

      if not os.path.exists(vfn):
         try:
            process_pwat(gribfn, vfn)
         except Exception as e:
            print("Failed to process precipitable water. Exception: '%s'" % (e,))

      #################################
      # Extract mean sea-level pressure
      #############
      vname = 'prmsl'
      vfn = ncpath + 'gfs.%s.t%sz.%s.0p25.nc' % (date, hour, vname)

      if not os.path.exists(vfn):
         try:
            process_prmsl(gribfn, vfn)
         except Exception as e:
            print("Failed to process mean sea-level pressure. Exception: '%s'" % (e,))
# }}}

def clean_gribs(month, days_old):
# {{{
   #Grib retention policy keep all
   gribpath = get_gribpath(month)

   # Confirm grib archive path exists
   if not os.path.exists(gribpath):
      #print("%s does not exist." % gribpath)
      return

   # Function to decide whether to delete files
   def should_delete():
      return False

   if should_delete():
      print("Removing %s." % gribpath)
      shutil.rmtree(gribpath)

      rt = os.path.split(gribpath[:-1])[0]
      if len(os.listdir(rt)) == 0:
         os.rmdir(rt)
# }}}

def clean_ncs(month, days_old):
# {{{
   ncpath = get_ncpath(month)
   #Nc retention policy keep all

   # Confirm grib archive path exists
   if not os.path.exists(ncpath):
      #print("%s does not exist." % ncpath)
      return

   # Function to decide whether to delete files
   def should_delete():
      return False

   if should_delete():
      print("Removing %s." % ncpath)
      shutil.rmtree(ncpath)

      rt = os.path.split(ncpath[:-1])[0]
      if len(os.listdir(rt)) == 0:
         os.rmdir(rt)
# }}}

def scan_archive():
# {{{
   dates_avail = glob.glob(arch_root + '*')

   print('Scanning GFS analysis archive; %d month directories present.' % len(dates_avail))

   # Get today's date in UTC
   utc_today = datetime.datetime.now(datetime.timezone.utc).date()

   for path in dates_avail:
      datestr = os.path.basename(path)
      try:
         yr = int(datestr[:4])
         mn = int(datestr[4:6])
         
      except:
         print("Path %s not recognized as a date; skipping." % path)
         raise

      # Work out how many days old this path is
      pathdate = datetime.date(yr, mn, 1)
      days_old = (utc_today - pathdate).days

      # Process any netcdf files that need processing
      process_gfs_to_nc(datestr)

      # Clean old grib files
      #clean_gribs(datestr, days_old)

      # Clean old netcdf files
      #clean_ncs(datestr, days_old)
# }}}

scan_archive()
