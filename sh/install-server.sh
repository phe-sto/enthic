#!/bin/sh

################################################################################
# 1) INSTALL DISTANT SYNAPTIC PACKAGES
apt-get -y install gunicorn3

cp ../server/enthic.service /etc/systemd/system/enthic.service

systemctl start enthic
systemctl enable enthic

touch /etc/cron.daily/enthic

script_dir=`dirname "$0"`

daily_cron_task="0 2 * * * /bin/sh ${script_dir}/database-update.sh"
echo ${daily_cron_task} > /etc/cron.daily/enthic
