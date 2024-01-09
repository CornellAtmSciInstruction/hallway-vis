import os, sys, glob
import datetime

import numpy as np

anim_root = '/scratch/EASvis/anims/'
gfs_root = '/scratch/EASvis/data/GFS/'
gfs_analysis_root = '/scratch/EASvis/data/GFS_analysis/'

def most_recent_GFS_init(var):
   ''' Returns path (to netcdf files), date, and hour of most recent available GFS initialization (that has been processed). '''

   dates_avail = glob.glob(gfs_root + '????????/??/netcdf/')
   dates_avail.sort()

   i = len(dates_avail) - 1
   while i >= 0:
      mr = dates_avail[i]
      ncfiles = glob.glob(mr + '*%s*.nc' % var)
      if len(ncfiles) > 0: break
      i -= 1

   if i < 0: 
      raise ValueError("No GFS initilizations are available with %s processed." % var)

   mrl = mr.split('/')
   ncfiles.sort()

   return mr, mrl[5], mrl[6]

def GFS_analysis_range(date, hour, days):
   ''' Returns paths to netcdf files for a certain number of days prior to date for the GFS analysis. 
       For each path another path corresponding to the forecast from that date/time is also returned.'''

   # Create datetime objects for ending and start dates
   dt = datetime.datetime.strptime(date+hour, '%Y%m%d%H')
   dt0 = dt - datetime.timedelta(days = days)

   anroots = []
   fcroots = []

   while dt0 < dt:
      m = dt0.strftime('%Y%m')
      d = dt0.strftime('%Y%m%d')
      h = dt0.strftime('%H')
      anroots.append(gfs_analysis_root + '%s/netcdf/gfs.%s.t%sz' % (m, d, h))
      fcroots.append(gfs_root + '%s/%s/netcdf/' % (d, h))

      dt0 += datetime.timedelta(hours = 6)

   return anroots, fcroots

def get_filename_template_from_frame(fr, hour, fc_path, an_rts, fc_rts):
   ''' Returns templates for netcdf filenames for a given day relative to paths returned by above helper functions.'''

   if fr >= 0: 
      # Use current forecast
      valid_hour = int(fr*24)
      step = fr*24 - valid_hour
      file1 = fc_path + 'gfs.t%sz.{var}.0p25.f%03d.nc' % (hour, valid_hour) 
      file2 = fc_path + 'gfs.t%sz.{var}.0p25.f%03d.nc' % (hour, valid_hour + 1) 
   else: 
      # Use analysis (or corresponding forecast)

      # Most recent analysis
      an_i = int(np.floor(fr*4))
      # Fraction of day; since fr is measured in days since most recent analysis, need to offset by hour of current analysis
      fr = fr + int(hour) / 24.
      hr = fr - np.floor(fr)
      an_hr = int(hr*4) * 6
      fc_hr1 = int(hr*24) - an_hr
      fc_hr2 = fc_hr1 + 1
      step = hr*24 - int(hr*24)

      print(an_hr, hr, fc_hr1, fc_hr2)
      # For most recent timestep, either return most recent analysis or subsequent forecast
      if fc_hr1 == 0: 
         file1 = an_rts[an_i] + '.{var}.0p25.nc'
      else:
         file1 = fc_rts[an_i] + 'gfs.t%02dz.{var}.0p25.f%03d.nc' % (an_hr, fc_hr1)

      # For next timestep, either subsequent forecast or analysis
      if fc_hr2 == 6:
         if an_i == -1:
            file2 = fc_path + 'gfs.t%sz.{var}.0p25.f%03d.nc' % (hour, 0) 
         else:
            file2 = an_rts[an_i + 1] + '.{var}.0p25.nc'
      else:
         file2 = fc_rts[an_i] + 'gfs.t%02dz.{var}.0p25.f%03d.nc' % (an_hr, fc_hr2)
  
   return file1, file2, step

def make_anim_filename(title, date, hour):
   ''' Returns filename to use for animation and makes path if necessary. '''
   path = anim_root + date

   if not os.path.exists(path):
      os.makedirs(path)

   return path + '/%s_anim_%s_%sz.mp4' % (title, date, hour)

def make_anim_symlink(title):
   return anim_root + '%s_anim_latest.mp4' % title
