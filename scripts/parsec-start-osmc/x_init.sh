#!/bin/bash
sleep 2
sudo fbi -T 7 -d /dev/fb0 --noverbose /home/osmc/.kodi/addons/plugin.program.parsec-launcher/fanart.jpg &
sleep 3
sudo openvt -c 7 -s -f clear
sudo su osmc -c "startx /home/osmc/Scripts/parsec-start/start_scc_parsec `echo $@`"
sudo openvt -c 7 -s -f clear
sudo systemctl start mediacenter
exit


