#
# exec(open("ithaca_temperature_annual_cycle.py").read())

import os
import numpy as np
import pandas as pd
import datetime
from datetime import date,timedelta
from matplotlib import pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.dates as mdates
import numpy.matlib
from scipy.ndimage.filters import uniform_filter1d

def f2c(temp_f):
    temp_c = (temp_f-32)*(5/9)
    return temp_c

plt.rcParams.update({
    'font.sans-serif': 'Arial',
    'font.family': 'sans-serif'
})

pathdate = datetime.datetime.today().strftime('%Y%m%d')

# -- define files and path
# pathin 		= '/Users/fl439/Dropbox/work/weather_data_ithaca/' # for testing
# pathin 		= '/home/fl439/work/weather_data_ithaca/' # for testing
pathin      = '/scratch/EASvis/gamefarm_climate/'
filein1		= 'StnData.csv'
filein2		= 'fcst.txt'
filename1   = pathin+filein1
filename2   = pathin+filein2
# pathout     = '/Users/fl439/Dropbox/work/weather_data_ithaca/' # for testing
# pathout     = '/home/fl439/work/weather_data_ithaca' # for testing
pathout     = '/scratch/EASvis/anims/'
fileout     = pathout + pathdate + '/ithaca_temperature_annual_cycle_fcst_subplots_'+pathdate+'.png'
linkout     = pathout + 'ithaca_temperature_annual_cycle_fcst_subplots_latest.png'

if os.path.exists(fileout):
   print('%s exists. Skipping update.' % fileout)
   exit()

# -- update data
startyear   = '1900'
refstart    = 1991 #1971 1991
refende     = 2020 #2000 2020
singleyear  = 2020
today       = date.today()
yesterday   = (today-timedelta(days=1)).strftime('%Y-%m-%d')
future      = (today+timedelta(days=30)).strftime('%Y-%m-%d')
pastyear    = (today-timedelta(days=365)).strftime('%Y-%m-%d')
# -- download newest Gamefarm Road data
os.system('curl \'http://data.rcc-acis.org/StnData?sid=304174&sdate='+startyear+'-01-01&edate='+yesterday+'&elems=1,2,43,4,10,11&output=csv\' > ' + filename1)

# -- download newest NWS Ithaca data
os.system('curl \'https://forecast.weather.gov/MapClick.php?lat=42.4465&lon=-76.4226&unit=0&lg=english&FcstType=dwml\' > ' + filename2)
file1 = open(filename2)
string1 = 'Daily Maximum'
string2 = 'Daily Minimum'
flag = 0
idx = 0
data = []
for line in file1:
    # print(line)
    data.append(line.strip())
    if string1 in line:
        idx1 = idx
    if string2 in line:
        idx2 = idx
    idx += 1

Tx_fcst = []
Tn_fcst = []
for i in range(1,7):
    s = data[idx1+i]
    s1 = s.find('e>')+2
    e1 = s.find('</')
    Tx_fcst.append(float(data[idx1+i][s1:e1]))
    s = data[idx2+i]
    s1 = s.find('e>')+2
    e1 = s.find('</')
    Tn_fcst.append(float(data[idx2+i][s1:e1]))

Tx_fcst = np.asarray(Tx_fcst)
Tn_fcst = np.asarray(Tn_fcst)
Tm_fcst = (Tx_fcst+Tn_fcst)/2


df = pd.read_csv(filename1,skiprows=1,header=None,names=['Date', 'Tx', 'Tn', 'Tm', 'P','Sf','Sd'],parse_dates=['Date'])
df = df[~((df.Date.dt.month == 2) & (df.Date.dt.day == 29))]
df = df.replace('T',999.)
df = df.replace('M',999.)
df = df.replace(999.,np.nan)

mask0 = (df['Date'] <= str(refende)+'-01-01')
mask1 = (df['Date'] >= str(refstart)+'-01-01') & (df['Date'] <= str(refende)+'-01-01')
mask2 = (df['Date'] >= '2021-01-01')
mask3 = (df['Date'] >= str(singleyear)+'-01-01') & (df['Date'] <= str(singleyear)+'-12-31')
mask4 = (df['Date'] >= pastyear) & (df['Date'] <= future)
ref0  = df.loc[mask0]
ref   = df.loc[mask1]
# ref2=ref.groupby(ref.Date.dt.dayofyear).apply(np.mean)

# -- what variables to plot
vars = ['Tm']#,'Tx','Tn']
vars_name = ['Mean']#,'Max','Min']

if len(vars)==3:
    fig = plt.figure(figsize = (8,15))
elif len(vars)==1:
    fig = plt.figure(figsize = (8,5))


for v in range(len(vars)):
    temp = vars[v]

    # -- insert latest observed value as first value in forecast
    tmp     = np.array(float(df[temp].iloc[-1]))
    if temp == 'Tx':
        T_fcst = Tx_fcst
    if temp == 'Tn':
        T_fcst = Tn_fcst
    if temp == 'Tm':
        T_fcst = Tm_fcst

    T_fcst = np.insert(T_fcst,0,tmp)

    clim_m  = np.zeros([365,])
    clim_x  = np.zeros([365,])
    clim_n  = np.zeros([365,])
    for d in range(365):
        clim_m[d] = ref[temp].iloc[d::365].astype(float).mean()
        clim_x[d] = ref0[temp].iloc[d::365].astype(float).max()
        clim_n[d] = ref0[temp].iloc[d::365].astype(float).min()

    clim_m_rep = np.matlib.repmat(clim_m,3,1).flatten()
    clim_x_rep = np.matlib.repmat(clim_x,3,1).flatten()
    clim_n_rep = np.matlib.repmat(clim_n,3,1).flatten()
    for i in range(200):
        clim_m_rep = uniform_filter1d(clim_m_rep,size=3)

    # clim_m_smooth = tmp[366:366+365]
    dayofyear = date.today().timetuple().tm_yday
    clim_m_smooth   = clim_m_rep[dayofyear-1:395+dayofyear-1]
    clim_x          = clim_x_rep[dayofyear-1:395+dayofyear-1]
    clim_n          = clim_n_rep[dayofyear-1:395+dayofyear-1]

    # new = df.Tm.loc[mask2].astype(float)
    # new = df.Tm.loc[mask3].astype(float)
    new = df[temp].loc[mask4].astype(float)

    new_above = np.where(new >= clim_m_smooth[0:len(new)], new, clim_m_smooth[0:len(new)])
    new_below = np.where(new < clim_m_smooth[0:len(new)], new, clim_m_smooth[0:len(new)])

    # start       = datetime.datetime(2021, 1, 1)
    start       = (today-timedelta(days=365))
    time_clim   = np.array([start + datetime.timedelta(days=i) for i in range(395)])
    time_new    = np.array([start + datetime.timedelta(days=i) for i in range(len(new))])
    time_fcst   = np.array([today-timedelta(days=1) + datetime.timedelta(days=i) for i in range(len(T_fcst))]) # if latest observed value is included in forecast data

    if np.isnan(new.iloc[-1]):
        yesterday = (today-timedelta(days=2)).strftime('%Y-%m-%d')

    ax1 = fig.add_subplot(len(vars),1,v+1)
    plt.title('Daily '+vars_name[v]+' temperature Cornell (latest: '+yesterday+')')
    # h1, = plt.plot(time_clim,clim_x,color=[.7,.7,.7],linewidth=.5,label='Max./Min. '+str(startyear)+'-'+str(refende))
    # h2, = plt.plot(time_clim,clim_n,color=[.7,.7,.7],linewidth=.5,label='Min.')
    h1, = plt.step(time_clim,clim_x,color=[.7,.7,.7],linewidth=.5,label='Max./Min. '+str(startyear)+'-'+str(refende))
    h2, = plt.step(time_clim,clim_n,color=[.7,.7,.7],linewidth=.5,label='Min.')
    hf, = plt.step(time_fcst,T_fcst,'-',color='k',label='NWS forecast',where='pre')
    # plt.plot(time_new,new,'r')
    # ax1.fill_between(time_new, new, clim_m_smooth[0:len(new)], where=new>=clim_m_smooth[0:len(new)], interpolate=True, color='red')
    # ax1.fill_between(time_new, new, clim_m_smooth[0:len(new)], where=new<=clim_m_smooth[0:len(new)], interpolate=True, color='blue')
    ax1.fill_between(time_new, new_above, clim_m_smooth[0:len(new)], interpolate=True, color='red',step='pre',alpha=.8)
    ax1.fill_between(time_new, new_below, clim_m_smooth[0:len(new)], interpolate=True, color='blue',step='pre',alpha=.8)
    h0, = plt.plot(time_clim,clim_m_smooth,color=[.4,.4,.4],label='Climatology '+str(refstart)+'-'+str(refende))
    ax1.plot(time_clim,clim_m_smooth*0+32,color='k')
    ymin = -20 #-30
    ymax = 100 #110
    ax1.set_ylim(ymin,ymax) # apply function and set transformed values to right axis limits
    ax1.set_ylabel('Temperature ($^\circ$F)')
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax1.xaxis.set_minor_locator(mdates.MonthLocator(interval=1))
    ax1.xaxis.grid(which='both',color=[.8,.8,.8], linestyle=':', linewidth=1)
    plt.legend(handles=[h0,h1,hf],loc='best')

    ax2 = ax1.twinx() # 2nd y-axis in celsius
    ymin, ymax = ax1.get_ylim() # get left axis limits
    ax2.set_ylim((f2c(ymin),f2c(ymax))) # apply function and set transformed values to right axis limits
    ax2.plot([],[]) # set an invisible artist to twin axes to prevent falling back to initial values on rescale events
    ax2.set_ylabel('Temperature ($^\circ$C)')
    plt.xlabel('Time')

#os.system('rm -rf '+pathin+fileout)
plt.savefig(fileout,dpi=300)
if os.path.exists(linkout): os.unlink(linkout)
os.symlink(fileout,linkout)

# plt.show()
exit()
