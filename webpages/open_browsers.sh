#!/usr/bin/bash

# Open video browser
DISPLAY=:0.0 nohup chromium-browser /home/aph28/hallwayvis/webpages/video_test.html --new-window --start-fullscreen >& /dev/null &
# Open forecast browser
DISPLAY=:0.0 nohup chromium-browser /home/aph28/hallwayvis/webpages/fc_test.html --new-window --start-fullscreen >& /dev/null &

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
