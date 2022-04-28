#!/bin/bash

cd /home/pi/Kokey

sudo systemctl stop KM4K && sudo ./KM4K.py 1
sudo systemctl start KM4K
