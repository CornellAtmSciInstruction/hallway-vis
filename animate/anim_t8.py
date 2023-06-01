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
title = 't850'

ncpath, date, hour = tools.most_recent_GFS_init('t850')
animfn = tools.make_anim_filename(title, date, hour)

dnow = datetime(int(date[:4]), int(date[4:6]), int(date[6:]), int(hour))

# Define the colormaps
norm_ref, cmap_ref = ctables.registry.get_with_steps('rainbow', -80., .5)
newcmap = ListedColormap(cmap_ref(range(0, 175)))
newnorm = Normalize(-44,48)

def anim_t8():
    plt.ioff()
    f = plt.figure(1, figsize = (8, 4.5), dpi = 96)
    f.subplots_adjust(top=0.967, bottom=0.033, left=0.069, right=0.981, hspace=0.2, wspace=0.2)
    f.clf()

    # Open first netcdf to get coordinates
    ncfile = ncpath + 'gfs.t%sz.t850.0p25.f000.nc' % (hour,)
    ds = xr.open_dataset(ncfile)

    # Pre transform lat and lon grid
    srcproj = ccrs.PlateCarree(central_longitude=0.)
    dstproj = ccrs.PlateCarree()
    #dstproj = ccrs.LambertConformal()
    slon = ds.longitude.data
    slat = ds.latitude.data
    slon, slat = np.meshgrid(ds.longitude.data, ds.latitude.data)
    xform = dstproj.transform_points(srcproj, slon, slat)
    dlon, dlat = xform[..., 0], xform[..., 1]

    # Create plot that can handle geographical data
    ax = f.add_subplot(111, projection = dstproj)  # Add axes to figure

    def make_frame(i):
        print(i)
        plt.ioff()
        ax.cla()
        ax.coastlines(resolution='50m')

        ncfile = ncpath + 'gfs.t%sz.t850.0p25.f%03d.nc' % (hour, i)
        ds = xr.open_dataset(ncfile)

        fmt = '%d %b %Y %H:00 UTC'
        dvalid = np.datetime64(ds.valid_time.data[()], 'h').astype(datetime)
        svalid = dvalid.strftime(fmt)
        snow   = dnow.strftime(fmt)

        t8 = ds['t850'].data - 273.15
        #t8 = add_cyclic_point(t8,coord=t8.longitude)
        ax.set_extent((-157,-3,10,70), crs=srcproj)

        #ax.contourf(dlon, dlat, t8, norm=newnorm, cmap=newcmap, levels=range(-40,40,1))
        c = ax.contourf(dlon[:, 721:], dlat[:, 721:], t8[:, 721:], norm=newnorm, cmap=newcmap, levels=range(-40,40,1))
        ax.contour(dlon[:, 721:], dlat[:, 721:], t8[:, 721:], levels=[0],colors=['blue'])

        ax.set_title(r'850hPa Temperature; 0$^\circ$ C isotherm',fontsize=11)
        ax.set_title('Last updated: %s\nValid:  %s' % (snow, svalid),loc='right',fontsize=8)
        ax.set_title('GFS Forecast via NOAA \nPlot by Jack Sillin',loc='left',fontsize=8)

        #cb = plt.colorbar(c, shrink=0.7)
        #f.axes[1].set_title(r'$^\circ$ C')

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
if os.path.exists(animfn):
    print('%s already exists; skipping.' % animfn)
    anim_t8()
else:
    anim_t8()

lnk = tools.make_anim_symlink(title)
if os.path.lexists(lnk): os.unlink(lnk)
os.symlink(animfn, lnk)

