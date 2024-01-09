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

fc_path, date, hour = tools.most_recent_GFS_init('t850')
animfn = tools.make_anim_filename(title, date, hour)

an_rts, fc_rts = tools.GFS_analysis_range(date, hour, 5)

dnow = datetime(int(date[:4]), int(date[4:6]), int(date[6:]), int(hour))

# Define the colormaps
def make_cmap():
   vc = [(-50, '#502D76'), \
         (-40, '#E0AEE0'), \
         (-20, '#38738F'), \
         (  0, '#FFFFFF'), \
         ( 10, '#246416'), \
         ( 20, '#FFFD80'), \
         ( 30, '#631212'), \
         ( 40, '#FFD7D6'), \
         ( 50, '#894900')]

   mn = -50.
   mx = 50.
   norm = Normalize(mn, mx, clip = False)

   vcn = [((v - mn)/(mx - mn), c) for v, c in vc]

   cmap = LinearSegmentedColormap.from_list('temp', vcn, N=4*512)
   cmap.set_over(color = vc[-1][1])
   cmap.set_under(color = vc[0][1])

   return norm, cmap

#norm_ref, cmap_ref = ctables.registry.get_with_steps('rainbow', -80., .5)
#cmap = ListedColormap(cmap_ref(range(0, 175)))
#norm = Normalize(-44,48)

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

def anim_t8():
    plt.ioff()
    f = plt.figure(1, figsize = (8, 4.5), dpi = 96)
    f.clf()

    # Open first netcdf to get coordinates
    ncfile = fc_path + 'gfs.t%sz.t850.0p25.f000.nc' % (hour,)
    ds = xr.open_dataset(ncfile)

    # Pre transform lat and lon grid
    srcproj = ccrs.PlateCarree(central_longitude=0.)
    dstproj = ccrs.PlateCarree()
    #dstproj = ccrs.LambertConformal()
    slon, slat = np.meshgrid(ds.longitude.data, ds.latitude.data)
    xform = dstproj.transform_points(srcproj, slon, slat)
    dlon, dlat = xform[..., 0], xform[..., 1]

    # Create plot that can handle geographical data
    f.subplots_adjust(top=0.973, bottom=0.003, left=0.019, right=0.981)
    ax = f.add_subplot(111, projection = dstproj)  # Add axes to figure

    # Make initial contour plot using longitudes as dummy data to create colorbar
    c = ax.contourf(dlon[:, 721:], dlat[:, 721:], slon[:, 721:] - 270., norm=norm, cmap=cmap, levels=range(-60,61,1), extend='both')

    # Create Cartopy feature to include state and province borders
    states_provinces = cfeature.NaturalEarthFeature(
       category='cultural',
       name='admin_1_states_provinces_lines',
       scale='50m',
       facecolor='none')

    # Choose geographical extent of map
    extent = [-167,-3,3,74]
    ax.set_extent(extent, crs=srcproj)

    cb = f.colorbar(c, ax = ax, orientation = 'horizontal', ticks = range(-60, 61, 10), \
                    shrink = 0.65, aspect = 26, fraction=0.1, pad=0.07)
    f.axes[1].set_title(r'$^\circ$C')

    def make_frame(d):
        print(d)
        plt.ioff()
        ax.cla()
        ax.coastlines(resolution='50m')

        fmt = '%d %b %Y %H:00 UTC'
        snow   = dnow.strftime(fmt)

        # Find appropriate input files 
        ncfile1, ncfile2, step = tools.get_filename_template_from_frame(d, hour, fc_path, an_rts, fc_rts)
        #print(ncfile1, ncfile2, step, flush=True)

        if d >= 0:
           label = 'GFS Forecast via NOAA\nPlot by Jack Sillin'
           desc = 'Forecast Valid'
           f.set_facecolor('0.8')
        else:
           label = 'GFS Analysis via NOAA\nPlot by Jack Sillin'
           desc = 'Analysis Valid'
           f.set_facecolor('w')

        ds1 = xr.open_dataset(ncfile1.format(var='t850'))
        ds2 = xr.open_dataset(ncfile2.format(var='t850'))

        dvalid = np.datetime64(ds1.valid_time.data[()], 'h').astype(datetime)
        svalid = dvalid.strftime(fmt)

        t8_1 = ds1['t850'].data - 273.15
        t8_2 = ds2['t850'].data - 273.15

        t8 = (1 - step) * t8_1 + step * t8_2

        #t8 = add_cyclic_point(t8,coord=t8.longitude)
        ax.set_extent(extent, crs=srcproj)

        #ax.contourf(dlon, dlat, t8, norm=newnorm, cmap=newcmap, levels=range(-40,40,1))
        c = ax.contourf(dlon[:, 721:], dlat[:, 721:], t8[:, 721:], norm=norm, cmap=cmap, levels=range(-60,61,1))
        #c = ax.pcolor(dlon[:, 721:], dlat[:, 721:], t8[:, 721:], norm=norm, cmap=cmap, shading='nearest')#, levels=range(-60,61,1))
        #ax.contour(dlon[:, 721:], dlat[:, 721:], t8[:, 721:], levels=[0],colors=['blue'])

        # Annotate plot
        # Add geographical features
        ax.add_feature(cfeature.BORDERS, edgecolor='0.3')
        ax.add_feature(cfeature.LAKES, facecolor="None", edgecolor='k')
        ax.add_feature(states_provinces, edgecolor='0.6')
        ax.plot([-76.5], [42.43], 'k.', ms = 3, mew = 1., transform=ccrs.PlateCarree())

        ax.set_title(r'850hPa Temperature',fontsize=11) #; 0$^\circ$ C isotherm'
        ax.set_title('Last Updated: %s\n%s: %s' % (snow, desc, svalid),loc='right',fontsize=8)
        ax.set_title(label, loc='left', fontsize=8)

        #cb = plt.colorbar(c, shrink=0.7)
        #f.axes[1].set_title(r'$^\circ$ C')

        gl = ax.gridlines(draw_labels = False, linewidth = 1, \
                          color = '0.4', alpha = 0.75, linestyle = '--')
        gl.xlocator = plt.MultipleLocator(30.)
        gl.ylocator = plt.MultipleLocator(10.)
        gl.top_labels = False
        gl.right_labels = False

        plt.ion()
        plt.draw()

    frames = make_frames(-5, 5.)

    make_frame(-2.334306965081513)
    #make_frame(2.)
    plt.ion()
    plt.show()
    plt.draw()
    return

    anim = manim.FuncAnimation(f, make_frame, frames, repeat=False)

    print('Writing animation to %s.' % animfn)
   
    anim.save(animfn, fps=24, codec='h264', dpi=240.)
    plt.ion()

import os
if os.path.exists(animfn):
    print('%s already exists; skipping.' % animfn)
    #anim_t8()
else:
    anim_t8()

lnk = tools.make_anim_symlink(title)
if os.path.lexists(lnk): os.unlink(lnk)
os.symlink(animfn, lnk)

# Add lakes, country boundaries, state boundaries, cities? (Ithaca at least)
