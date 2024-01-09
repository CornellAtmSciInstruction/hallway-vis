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

fc_path, date, hour = tools.most_recent_GFS_init('prmsl')
animfn = tools.make_anim_filename(title, date, hour)

an_rts, fc_rts = tools.GFS_analysis_range(date, hour, 5)

dnow = datetime(int(date[:4]), int(date[4:6]), int(date[6:]), int(hour))

# Define the colormaps
def make_cmap():
   vc = [(960, '#61e0df'), \
         (980, '#37486b'), \
         (1010, '#FFFFFF'), \
         (1040, '#730f12'), \
         (1060, '#d45916')]

   mn = 960.
   mx = 1060.
   norm = Normalize(mn, mx, clip = False)

   vcn = [((v - mn)/(mx - mn), c) for v, c in vc]

   cmap = LinearSegmentedColormap.from_list('msl', vcn, N=4*512)
   cmap.set_over(color = vc[-1][1])
   cmap.set_under(color = vc[0][1])

   return norm, cmap

norm, cmap = make_cmap()

def make_frames(start, end):
   fr = []
   f = start
   while f < end:
      fr.append(f)
      dt = (1 / 24.) * (1 - 0.8 / (1 + (2*f)**2))
      #dt = 1 * (1 - 0.5 / (1 + f**2))
      f += dt
   return fr

def anim_z500():
    plt.ioff()
    f = plt.figure(1, figsize = (8, 4.5), dpi = 96)
    f.clf()

    # Open first netcdf to get coordinates
    ncfn = fc_path + 'gfs.t%sz.prmsl.0p25.f000.nc' % (hour,)
    ds = xr.open_dataset(ncfn)

    # Pre transform lat and lon grid
    srcproj = ccrs.PlateCarree(central_longitude=0.)
    dstproj = ccrs.PlateCarree()
    #dstproj = ccrs.LambertConformal()
    slon, slat = np.meshgrid(ds.longitude.data, ds.latitude.data)
    xform = dstproj.transform_points(srcproj, slon, slat)
    dlon, dlat = xform[..., 0], xform[..., 1]

    cgh = np.linspace(4500., 6000, 21)
    cms = 1010. + np.arange(-60, 61, 5.)

    # Create plot that can handle geographical data
    f.subplots_adjust(top=0.973, bottom=0.003, left=0.019, right=0.981)
    ax = f.add_subplot(111, projection = dstproj)  # Add axes to figure

    # Make initial contour plot using longitudes as dummy data to create colorbar
    c = ax.contourf(dlon[:, 721:], dlat[:, 721:], (ds.prmsl/100.)[:, 721:], norm=norm, cmap=cmap, levels=cms, extend='both')

    # Create Cartopy feature to include state and province borders
    states_provinces = cfeature.NaturalEarthFeature(
       category='cultural',
       name='admin_1_states_provinces_lines',
       scale='50m',
       facecolor='none')

    # Choose geographical extent of map
    extent = [-167,-3,3,74]
    ax.set_extent(extent, crs=srcproj)

    cb = f.colorbar(c, ax = ax, orientation = 'horizontal', ticks = range(920, 1101, 30), \
                    shrink = 0.65, aspect = 26, fraction=0.1, pad=0.07)
    f.axes[1].set_title(r'hPa')

    def make_frame(d):
        print(d)
        plt.ioff()
        ax.cla()

        # Find appropriate input files 
        ncfile1, ncfile2, step = tools.get_filename_template_from_frame(d, hour, fc_path, an_rts, fc_rts)
        #print(ncfile1, ncfile2, step, flush=True)

        # Interpolate between two steps of geopotential height data
        dgh1 = xr.open_dataset(ncfile1.format(var='gh500')) 
        dgh2 = xr.open_dataset(ncfile2.format(var='gh500')) 

        gh500 = (1 - step) * dgh1['gh500'].data + step * dgh2['gh500'].data

        # Interpolate between two steps of sea-level pressure data
        dms1 = xr.open_dataset(ncfile1.format(var='prmsl')) 
        dms2 = xr.open_dataset(ncfile2.format(var='prmsl')) 

        prmsl = (1 - step) * dms1['prmsl'].data + step * dms2['prmsl'].data
        prmsl = prmsl / 100. # Convert to hPa

        if d >= 0:
           label = 'GFS Forecast via NOAA'
           desc = 'Forecast Valid'
           f.set_facecolor('0.8')
        else:
           label = 'GFS Analysis via NOAA'
           desc = 'Analysis Valid'
           f.set_facecolor('w')

        fmt = '%d %b %Y %H:00 UTC'
        snow   = dnow.strftime(fmt)

        dvalid = np.datetime64(dms1.valid_time.data[()], 'h').astype(datetime)
        svalid = dvalid.strftime(fmt)

        ax.set_extent(extent, crs=srcproj)

        c = ax.contourf(dlon[:, 721:], dlat[:, 721:], prmsl[:, 721:], norm=norm, cmap=cmap, levels=cms)
        ax.contour(dlon[:, 721:], dlat[:, 721:], gh500[:, 721:], levels=cgh, colors=['black'])

        # Annotate plot

        # Add geographical features
        ax.coastlines(resolution='50m')
        ax.add_feature(cfeature.BORDERS, edgecolor='0.3')
        ax.add_feature(cfeature.LAKES, facecolor="None", edgecolor='k')
        ax.add_feature(states_provinces, edgecolor='0.6')
        ax.plot([-76.5], [42.43], 'k.', ms = 3, mew = 1., transform=ccrs.PlateCarree())

        # Set titles
        ax.set_title('Mean sea-level pressure (colors)\n500 hPa Geopotential Height (contours)',fontsize=11)
        ax.set_title('Last Updated: %s\n%s: %s' % (snow, desc, svalid),loc='right',fontsize=8)
        ax.set_title(label, loc='left', fontsize=8)

        # Add lat/lon grid
        gl = ax.gridlines(draw_labels = False, linewidth = 1, \
                          color = '0.4', alpha = 0.75, linestyle = '--')
        gl.xlocator = plt.MultipleLocator(30.)
        gl.ylocator = plt.MultipleLocator(10.)
        gl.top_labels = False
        gl.right_labels = False

        plt.ion()
        plt.draw()

    frames = make_frames(-5, 5.)

    #make_frame(-2.334306965081513)
    #make_frame(2.)
    #plt.ion()
    #plt.show()
    #plt.draw()
    #return

    anim = manim.FuncAnimation(f, make_frame, frames, repeat=False)

    print('Writing animation to %s.' % animfn)
   
    anim.save(animfn, fps=24, codec='h264', dpi=240.)
    plt.ion()

import os
animfn = 'test_z500.mp4'
anim_z500()

#if os.path.exists(animfn):
    #print('%s already exists; skipping.' % animfn)
#else:
    #anim_z500()

#lnk = tools.make_anim_symlink(title)
#if os.path.lexists(lnk): os.unlink(lnk)
#os.symlink(animfn, lnk)

