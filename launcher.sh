#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home
# credit to this page for the help with the launcher: https://www.instructables.com/Raspberry-Pi-Launch-Python-script-on-startup/

cd /
cd home/gabe/Multi-Stage-Control
sudo python main.py
cd /