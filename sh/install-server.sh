#!/bin/sh

################################################################################
# 1) INSTALL DISTANT SYNAPTIC PACKAGES
apt-get -y install gunicorn3 nginx certbot

# 2) INSTALL ENTHIC SERVICE AND ENABLE IT
cp ../server/enthic.service /etc/systemd/system/enthic.service
mkdir -p /var/www/enthic/
systemctl start enthic
systemctl enable enthic

# 3) CONFIGURE NGINX SERVER
cp ../server/enthic-nginx.conf /etc/nginx/sites-available/enthic.conf
ln -s /etc/nginx/sites-available/enthic.conf /etc/nginx/sites-enabled/

systemctl enable nginx
systemctl start nginx

# 4) CONFIGURE HTTPS
certbot --nginx

# 3) INSTALL DAILY UPDATE CRON (TODO fix it)
touch /etc/cron.daily/enthic

script_dir=$(dirname "$0")

daily_cron_task="0 2 * * * /bin/sh ${script_dir}/database-update.sh"
echo "${daily_cron_task}" > /etc/cron.daily/enthic
