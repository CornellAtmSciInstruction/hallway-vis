#!/usr/bin/bash

PID=$(ps -C chromium-browse f | awk 'NR==2 { print $1 }')

if [ ! -z "$PID" ] 
then
   kill $PID
fi

PID=$(ps -C srv_pi f | awk 'NR==2 { print $1 }')

if [ ! -z "$PID" ] 
then
  kill $PID
fi

sleep 2

nohup /home/aph28/hallway-vis/webpages/srv_pi >& /dev/null &

#CHRMARGS="--new-window --noerrdialogs --disable-infobars --start-fullscreen"
CHRMARGS="--new-window --noerrdialogs --disable-infobars --kiosk"
#CHRMARGS="--new-window"
#FCLIST=$(cat fclist.txt)
#FCLIST="http://127.0.0.1:9000/gamefarm_climate.html http://127.0.0.1:9000/gauges/gauges.html"
FCLIST=/home/aph28/hallway-vis/webpages/fc.html
VSLIST=/home/aph28/hallway-vis/webpages/video.html

# Open video browser
#DISPLAY=:0.0 nohup chromium-browser /home/aph28/hallway-vis/webpages/video.html --new-window --start-fullscreen >& /dev/null &
DISPLAY=:0.0 nohup chromium-browser $FCLIST $CHRMARGS >& /dev/null &

sleep 2

DISPLAY=:0.0 nohup chromium-browser $VSLIST $CHRMARGS >& /dev/null &

# Open forecast browser
#DISPLAY=:0.0 nohup chromium-browser /home/aph28/hallway-vis/webpages/fc.html --new-window --start-fullscreen >& /dev/null &
#DISPLAY=:0.0 nohup chromium-browser http://127.0.0.1:9000/fc.html --new-window --noerrdialogs --disable-infobars --kiosk >& /dev/null &

sleep 6

# Get window ID for video browser
VISWNDID=$(DISPLAY=:0.0 xdotool search -name EASAtmosVis.*)
echo $VISWNDID
# move video browser to right screen
DISPLAY=:0.0 xdotool windowmove --sync $VISWNDID 0 0

# Get window ID for forecast browser
FCWNDID=$(DISPLAY=:0.0 xdotool search -name EASAtmosFC.*)
echo $FCWNDID
# move forecast browser to right screen
DISPLAY=:0.0 xdotool windowmove --sync $FCWNDID 1920 0

#echo $WINDOWID
#WINDOWPID=$(DISPLAY=:0.0 xdotool getwindowpid $WINDOWID)
