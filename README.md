# Lernecken

Buchungssystem für die Lernecken (studentische Arbeitsecken) des CIT.

## Voraussetzungen
- OS: [SUSE Linux Enterprise Server 12 SP2](https://www.suse.com/releasenotes/x86_64/SUSE-SLES/12-SP2/)
- Plattform: Python3 mit Django und LDAP-Backend
- Webserver: Apache2 mit Python3-WSGI-Module
- Datenbank: Sqlite3

*(Plattform, Webserver und Datenbank werden durch das Installationsskript automatisch installiert. Lediglich das OS muss manuell aufgesetzt werden.)*

## Installation
1. SSH auf den Zielserver
```bash
$ ssh root@lernecken.hs-mannheim.de
```
2. Git installieren:
```bash
$ zypper refresh && zypper install -y git
```
3. Das Projekt auschecken (muss in `/srv/www/` liegen): 
```bash
$ cd /srv/www/
$ git clone https://github.com/informatik-mannheim/lernecken.git
```
4. Installation ausführen:
```bash
$ cd /srv/www/lernecken/
$ ./install.sh
```
5. Secret settings anpassen: in `/srv/www/lernecken/schnuffelecken/schnuffelecken/settings_secret.py` die entsprechenden Settings anpassen

6. Apache neu starten:
```bash
$ systemctl restart apache2
```

## Update
Zum Updaten das Skript `update.sh` ausführen:

```bash
$ cd /srv/www/lernecken
$ ./update.sh
```

Änderungen werden aus github gepulled, alle DB Migrations neu ausgeführt und der Webserver neu gestartet.

## Admin-Interface
Das Admin-Interface erlaubt das verwalten aller für die Verwaltung registrierten Model-Objekte in Django. Dazu muss ein superuser angelegt werden:

```bash
$ cd /srv/www/faculty-schnuffelecke/schnuffelecken/
$ python3 manage.py createsuperuser
```

Das Backend ist dann über [https://lernecken.hs-mannheim.de/admin/](https://lernecken.hs-mannheim.de/admin/) erreichbar
