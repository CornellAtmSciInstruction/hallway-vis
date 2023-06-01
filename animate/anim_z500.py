import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point
from datetime import datetime, timedelta
import numpy as np
import xarray as xr
from metpy.plots import ctables
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize

import matplotlib.animation as manim

# import helper module
import tools

animroot = '/scratch/EASvis/anims/'
title = 'z500'

ncpath, date, hour = tools.most_recent_GFS_init('prmsl')
animfn = tools.make_anim_filename(title, date, hour)

dnow = datetime(int(date[:4]), int(date[4:6]), int(date[6:]), int(hour))

# Define the colormaps
norm_ref, cmap_ref = ctables.registry.get_with_steps('rainbow', -80., .5)
newcmap = ListedColormap(cmap_ref(range(0, 175)))
newnorm = Normalize(-44,48)

def anim_z500():
    plt.ioff()
    f = plt.figure(1, figsize = (8, 4.5), dpi = 96)
    f.subplots_adjust(top=0.967, bottom=0.033, left=0.069, right=0.981, hspace=0.2, wspace=0.2)
    f.clf()

    # Open first netcdf to get coordinates
    ncfn = ncpath + 'gfs.t%sz.prmsl.0p25.f000.nc' % (hour,)
    ds = xr.open_dataset(ncfn)

    # Pre transform lat and lon grid
    srcproj = ccrs.PlateCarree(central_longitude=0.)
    dstproj = ccrs.PlateCarree()
    #dstproj = ccrs.LambertConformal()
    slon = ds.longitude.data
    slat = ds.latitude.data
    slon, slat = np.meshgrid(ds.longitude.data, ds.latitude.data)
    xform = dstproj.transform_points(srcproj, slon, slat)
    dlon, dlat = xform[..., 0], xform[..., 1]

    cgh = np.linspace(4500., 6000, 21)
    cms = 1010. + np.arange(-45, 45, 5.)

    # Create plot that can handle geographical data
    ax = f.add_subplot(111, projection = dstproj)  # Add axes to figure
    c = ax.contourf(dlon[:, 721:], dlat[:, 721:], (ds.prmsl/100.)[:, 721:], cmap=plt.cm.RdBu_r, levels=cms)
    cb = plt.colorbar(c, shrink=0.7)
    cax = cb.ax

    def make_frame(i):
        print(i)
        plt.ioff()
        ax.cla()
        cax.cla()

        ax.coastlines(resolution='50m')

        ncfn1 = ncpath + 'gfs.t%sz.gh500.0p25.f%03d.nc' % (hour, i)
        dgh = xr.open_dataset(ncfn1)

        ncfn2 = ncpath + 'gfs.t%sz.prmsl.0p25.f%03d.nc' % (hour, i)
        dms = xr.open_dataset(ncfn2)

        fmt = '%d %b %Y %H:00 UTC'
        dvalid = np.datetime64(dgh.valid_time.data[()], 'h').astype(datetime)
        svalid = dvalid.strftime(fmt)
        snow   = dnow.strftime(fmt)

        gh500 = dgh['gh500'].data
        prmsl = dms['prmsl'].data / 100.
        ax.set_extent((-157,-3,10,70), crs=srcproj)

        c = ax.contourf(dlon[:, 721:], dlat[:, 721:], prmsl[:, 721:], cmap=plt.cm.RdBu_r, levels=cms)
        ax.contour(dlon[:, 721:], dlat[:, 721:], gh500[:, 721:], levels=cgh,colors=['black'])

        ax.set_title('Mean sea-level pressure (colors)\n500 hPa Geopotential Height (contours)\n\n',fontsize=11)
        ax.set_title('Last updated: %s\nValid:  %s' % (snow, svalid),loc='right',fontsize=8)
        ax.set_title('GFS Forecast via NOAA',loc='left',fontsize=8)

        cb = plt.colorbar(c, cax = cax)
        cax.set_title(r'hPa')

        gl = ax.gridlines(draw_labels = True, linewidth = 1, \
                          color = '0.4', alpha = 0.75, linestyle = '--')
        gl.top_labels = False
        gl.right_labels = False

        plt.ion()
        plt.draw()

    frames = range(0,100,1)

    #make_frame(4)
    #plt.ion()
    #plt.show()
    #plt.draw()
    #return

    anim = manim.FuncAnimation(f, make_frame, frames, repeat=False)

    print('Writing animation to %s.' % animfn)
   
    anim.save(animfn, fps=12, codec='h264', dpi=240.)
    plt.ion()

import os
#animfn = 'test.mp4'
anim_z500()

if os.path.exists(animfn):
    print('%s already exists; skipping.' % animfn)
else:
    anim_z500()

lnk = tools.make_anim_symlink(title)
if os.path.lexists(lnk): os.unlink(lnk)
os.symlink(animfn, lnk)

