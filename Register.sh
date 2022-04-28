#!/bin/bash

cd /home/pi/Kokey

sudo systemctl stop KM4K && sudo ./KM4K.py 0
sudo systemctl start KM4K
