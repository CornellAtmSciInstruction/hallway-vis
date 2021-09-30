#!/bin/bash

# add ssh key
echo "# Start ssh-agent #"
eval `ssh-agent -s`
ssh-add /home/aph28/.ssh/id_picopy

rsync -Lvu /scratch/EASvis/anims/*latest* en-ea-aaph28-pi.coecis.cornell.edu:hallway-vis/anims/

kill $SSH_AGENT_PID

