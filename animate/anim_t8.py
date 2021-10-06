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

# Define the colormaps
norm_ref, cmap_ref = ctables.registry.get_with_steps('rainbow', -80., .5)
newcmap = ListedColormap(cmap_ref(range(0, 175)))
newnorm = Normalize(-44,48)

def anim_t8():
    plt.ioff()
    f = plt.figure(1, figsize = (8, 4.5), dpi = 96, tight_layout=True)
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

        t8 = ds['t850'].data - 273.15
        #t8 = add_cyclic_point(t8,coord=t8.longitude)
        ax.set_extent((-157,-3,10,70), crs=srcproj)

        #ax.contourf(dlon, dlat, t8, norm=newnorm, cmap=newcmap, levels=range(-40,40,1))
        ax.contourf(dlon[:, 721:], dlat[:, 721:], t8[:, 721:], norm=newnorm, cmap=newcmap, levels=range(-40,40,1))
        ax.contour(dlon[:, 721:], dlat[:, 721:], t8[:, 721:], levels=[0],colors=['blue'])

        ax.set_title('850hPa Temperature (C)',fontsize=11)
        #ax.set_title('Valid: '+dtfs,loc='right',fontsize=8)
        ax.set_title('GFS Forecast via NOAA \nPlot by Jack Sillin',loc='left',fontsize=8)

        plt.ion()
        plt.draw()

    frames = range(0,100,1)

    #make_frame(0)

    anim = manim.FuncAnimation(f, make_frame, frames, repeat=False)

    print('Writing animation to %s.' % animfn)
   
    anim.save(animfn, fps=12, codec='h264', dpi=240.)
    plt.ion()

import os
if os.path.exists(animfn):
    print('%s already exists; skipping.' % animfn)
else:
    anim_t8()

lnk = tools.make_anim_symlink(title)
if os.path.exists(lnk): os.unlink(lnk)
os.symlink(animfn, lnk)

