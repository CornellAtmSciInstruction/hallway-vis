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

day, hour = tools.most_recent_GFS_init('t850')
ncpath = '/scratch/EASvis/data/GFS/%s/%s/netcdf/' % (day, hour)
animfn = animroot + 't850_anim_%d%02dz.mp4' % (day, hour)

# Define the colormaps
norm_ref, cmap_ref = ctables.registry.get_with_steps('rainbow', -80., .5)
newcmap = ListedColormap(cmap_ref(range(0, 175)))
newnorm = Normalize(-44,48)

def anim_t8():
    plt.ioff()
    f = plt.figure(1, figsize = (8, 4), dpi = 96, tight_layout=True)
    f.clf()

    # Create plot that can handle geographical data
    ax = f.add_subplot(111, projection = ccrs.PlateCarree())  # Add axes to figure

    def make_frame(i):
        plt.ioff()
        ax.cla()
        ax.coastlines(resolution='50m')

        ncfile = ncpath + 'gfs.t%sz.t850.0p25.f%03d.nc' % (hour, i)
        ds = xr.open_dataset(ncfile)

        t8 = ds['t850'] - 273.15
        #t8 = add_cyclic_point(t8,coord=t8.longitude)
        ax.set_extent((-157,0,0,90))

        ax.contourf(t8.longitude,t8.latitude,t8,norm=newnorm,cmap=newcmap,antialiased=True,levels=range(-40,40,1),alpha=0.7,transform=ccrs.PlateCarree())
        ax.contour(t8.longitude,t8.latitude,t8,levels=[0],colors=['blue'],transform=ccrs.PlateCarree())

        ax.set_title('850hPa Temperature (C)',fontsize=11)
        #ax.set_title('Valid: '+dtfs,loc='right',fontsize=8)
        ax.set_title('GFS Forecast via NOAA \nPlot by Jack Sillin',loc='left',fontsize=8)

        plt.ion()
        plt.draw()

    frames = range(0,100,1)

    #make_frame(0)
    anim = manim.FuncAnimation(f, make_frame, frames, repeat=False)

    anim.save(animfn, fps=12, codec='h264')
    plt.ion()

import os
if not os.path.exists(animfn):
   anim_t8()

