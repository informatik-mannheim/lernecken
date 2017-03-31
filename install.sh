#!/bin/bash

echo "Installiere Schnuffelecken..."
echo

# root check
if [[ $(id -u) -ne 0 ]]
then 
	echo "Please run as root";
	exit 1; 
fi

# add required repos
zypper --no-gpg-checks addrepo http://download.opensuse.org/repositories/devel:languages:python3/SLE_12_SP2/devel:languages:python3.repo
zypper --no-gpg-checks addrepo http://download.opensuse.org/repositories/Apache:Modules/SLE_12_SP2/Apache:Modules.repo
zypper --no-gpg-checks refresh

# install python3, apache2 and all necessary modules and libraries
zypper -n install python3 apache2 python3-setuptools cyrus-sasl-devel apache2-mod_wsgi-python3 wget

# get pip3 (is there a better way in suse le?)
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
rm get-pip.py

# make sure pip is newest version
pip3 install -U pip

#install django and the LDAP backend
pip3 install django django_auth_ldap

# copy configuration files to target locations
cp conf/lernecken.conf /etc/apache2/vhosts.d/
cp conf/lernecken-ssl.conf /etc/apache2/vhosts.d/
test -d /etc/openldap/ || mkdir -p /etc/openldap && cp conf/ldap.conf /etc/openldap/

# Create settings_secret.py file from skeleton generating a new secret key
cp conf/settings_secret_skel.py schnuffelecken/schnuffelecken/settings_secret.py
sed 's/SECRET_KEY\s=\s"DEFAULT"/SECRET_KEY = "'$(python3 schnuffelecken/manage.py gen_secret_key)'"/' conf/settings_secret_skel.py > schnuffelecken/schnuffelecken/settings_secret.py 

# create daily cron job to remove old booking
cp remove_old_bookings.sh /etc/cron.daily

# install dfn root certificate for LDAP authentication
wget http://cdp.pca.dfn.de/global-root-ca/pub/cacert/cacert.pem -O /etc/ssl/certs/cacert.pem

# create database migrations and migrate them
python3 schnuffelecken/manage.py migrate
python3 schnuffelecken/manage.py collectstatic --no-input

# grant write permissions on the database
chown wwwrun: schnuffelecken
chown wwwrun: schnuffelecken/db.sqlite3

# restart apache2
systemctl restart apache2
