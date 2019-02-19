#!/usr/bin/env bash
sudo mkdir /gisdata/
sudo chmod 777 /gisdata/
aws s3 cp s3://sharedbikedata/Land_use/gisdata/ /gisdata/ --recursive