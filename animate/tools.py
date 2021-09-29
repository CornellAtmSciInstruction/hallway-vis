import os, sys, glob
import datetime

anim_root = '/scratch/EASvis/anims/'
gfs_root = '/scratch/EASvis/data/GFS/'

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

def make_anim_filename(title, date, hour):
   ''' Returns filename to use for animation and makes path if necessary. '''
   path = anim_root + date

   if not os.path.exists(path):
      os.makedirs(path)

   return path + '/%s_anim_%s_%sz.mp4' % (title, date, hour)


def make_anim_symlink(title):
   return anim_root + '%s_anim_latest.mp4' % title
