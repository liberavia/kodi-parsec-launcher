#!/bin/bash
sudo openvt -c 7 -s -f clear
sudo su osmc -c "openvt -c 7 -f -s /home/osmc/Scripts/parsec-start/x_init.sh `echo $@` &" &
sleep 1
sudo su -c "xbmc-send -a "Quit" | sudo systemctl stop mediacenter" &
exit


