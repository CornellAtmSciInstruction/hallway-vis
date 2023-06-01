import os, sys, glob
import shutil
import datetime

import xarray as xr

arch_root = '/scratch/EASvis/data/GFS/'

def get_gribpath(day, hour):
   return arch_root + '%s/%s/grib/' % (day, hour)

def get_ncpath(day, hour):
   return arch_root + '%s/%s/netcdf/' % (day, hour)

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

def process_gfs_to_nc(day, hour):
# {{{
   gribpath = get_gribpath(day, hour)
   ncpath = get_ncpath(day, hour)

   if not os.path.exists(ncpath):
      os.makedirs(ncpath)

   # Get list of available grib files
   filelist = glob.glob(gribpath + '*f???')
   filelist.sort()

   plev_vars = {'t': 850, 'gh': 500}

   for gribfn in filelist:
      #################################
      # Extract single-level isobaric data
      #############
      fcstep = gribfn[-3:]

      for v, pr in plev_vars.items():
         vname = v + '%d' % pr
         plfn = ncpath + 'gfs.t%sz.%s.0p25.f%s.nc' % (hour, vname, fcstep)

         if not os.path.exists(plfn):
            try:
               process_isobaric_level(gribfn, plfn, v, pr)
            except Exception as e:
               print("Failed to process single-level %s. Exception: '%s'" % (v, e))

      #################################
      # Extract precipitable water
      #############
      vname = 'pwat'
      vfn = ncpath + 'gfs.t%sz.%s.0p25.f%s.nc' % (hour, vname, fcstep)

      if not os.path.exists(vfn):
         try:
            process_pwat(gribfn, vfn)
         except Exception as e:
            print("Failed to process precipitable water. Exception: '%s'" % (e,))

      #################################
      # Extract mean sea-level pressure
      #############
      vname = 'prmsl'
      vfn = ncpath + 'gfs.t%sz.%s.0p25.f%s.nc' % (hour, vname, fcstep)

      if not os.path.exists(vfn):
         try:
            process_prmsl(gribfn, vfn)
         except Exception as e:
            print("Failed to process mean sea-level pressure. Exception: '%s'" % (e,))
# }}}

def clean_gribs(day, hour, days_old):
# {{{
   #Grib retention policy keep 00Z for 1 weeks, remove others after 3 days
   gribpath = get_gribpath(day, hour)

   # Confirm grib archive path exists
   if not os.path.exists(gribpath):
      #print("%s does not exist." % gribpath)
      return

   # Function to decide whether to delete files
   def should_delete():
      if days_old > 6:
         return True

      if days_old > 2 and not hour == '00':
         return True

      return False

   if should_delete():
      print("Removing %s." % gribpath)
      shutil.rmtree(gribpath)

      rt = os.path.split(gribpath[:-1])[0]
      if len(os.listdir(rt)) == 0:
         os.rmdir(rt)
# }}}

def clean_ncs(day, hour, days_old):
# {{{
   ncpath = get_ncpath(day, hour)
   #Nc retention policy keep 00Z for 2 weeks, remove others after 1 week

   # Confirm grib archive path exists
   if not os.path.exists(ncpath):
      #print("%s does not exist." % ncpath)
      return

   # Function to decide whether to delete files
   def should_delete():
      if days_old > 13:
         return True

      if days_old > 6 and not hour == '00':
         return True

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

   print('Scanning archive; %d date directories present.' % len(dates_avail))

   # Get today's date in UTC
   utc_today = datetime.datetime.now(datetime.timezone.utc).date()

   for path in dates_avail:
      datestr = os.path.basename(path)
      try:
         yr = int(datestr[:4])
         mn = int(datestr[4:6])
         dy = int(datestr[6:8])
         
      except:
         print("Path %s not recognized as a date; skipping." % path)
         continue

      # Work out how many days old this path is
      pathdate = datetime.date(yr, mn, dy)
      days_old = (utc_today - pathdate).days

      for hour in ['00', '06', '12', '18']:
         # Process any netcdf files that need processing
         process_gfs_to_nc(datestr, hour)

         # Clean old grib files
         clean_gribs(datestr, hour, days_old)

         # Clean old netcdf files
         clean_ncs(datestr, hour, days_old)
# }}}

scan_archive()
