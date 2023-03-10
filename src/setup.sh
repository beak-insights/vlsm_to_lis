#!/usr/bin/env bash
set -x
# trap read debug

pip install -r ./requirements.txt

sudo apt install supervisor
sudo rm /etc/supervisor/conf.d/hl7_results.conf
sudo cp ./hl7_results.conf /etc/supervisor/conf.d
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status