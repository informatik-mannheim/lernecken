echo "Updating Schnuffelecken..."
echo

# get changes
git pull

# perform db migrations

python3 schnuffelecken/manage.py migrate
python3 schnuffelecken/manage.py collectstatic --no-input

# update apache config
cp conf/lernecken.conf /etc/apache2/vhosts.d/
cp conf/lernecken-ssl.conf /etc/apache2/vhosts.d/

# restart apache
systemctl restart apache2
