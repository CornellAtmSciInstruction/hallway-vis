#!/usr/bin/bash

PID=$(ps -C chromium-browse f | awk 'NR==2 { print $1 }')

if [ ! -z "$PID" ] 
then
   kill $PID
fi

# Open video browser
DISPLAY=:0.0 nohup chromium-browser /home/aph28/hallway-vis/webpages/video.html --new-window --start-fullscreen >& /dev/null &
# Open forecast browser
DISPLAY=:0.0 nohup chromium-browser /home/aph28/hallway-vis/webpages/fc.html --new-window --start-fullscreen >& /dev/null &

sleep 5

# Get window ID for video browser
VISWNDID=$(DISPLAY=:0.0 xdotool search -name EASAtmosVis.*)
# move video browser to right screen
DISPLAY=:0.0 xdotool windowmove --sync $VISWNDID 1920 0

# Get window ID for forecast browser
FCWNDID=$(DISPLAY=:0.0 xdotool search -name EASAtmosFC.*)
# move forecast browser to right screen
DISPLAY=:0.0 xdotool windowmove --sync $FCWNDID 0 0

echo $WINDOWID
WINDOWPID=$(DISPLAY=:0.0 xdotool getwindowpid $WINDOWID)
