import os, sys, glob
import datetime

anim_root = '/scratch/EASvis/anims/'
gfs_root = '/scratch/EASvis/data/GFS/'

def most_recent_GFS_init(var):
   ''' Returns date and hour of most recent available GFS initialization (that has been processed). '''

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

   mr = mr.split('/')
   ncfiles.sort()

   return int(mr[5]), int(mr[6])


