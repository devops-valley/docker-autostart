# Usage

## autodiscover

usage: `python3 discover.py [-a <action>] [-l] service_dir [service_dir …]`

add label "de.wie-ei.autostart=true" to any service in a docker-compose-file

!! This label is discovered as string, not by parsing Yaml. Commenting will not work!

Examples:

* start services (up -d) `python3 discover.py /srv/services/ /opt/docker/testing/`
* which services are configured for autostart? `python3 discover.py -l /srv/services/ /opt/docker/testing/`
* check status `python3 discover.py -a ps /opt/docker/testing/`
* stop services `python3 discover.py -a "down -v /srv/testing/`

## manual config

### json config
* create config.json from sample.json
* add `python3 /opt/docker-autostart/start.py /path/to/your/config.json -t json` to `/etc/rc.local`

### raw config
* create config.lst from sample.lst
* add `python3 /opt/docker-autostart/start.py /path/to/your/config.lst` to `/etc/rc.local`

### other actions
* default action: up -d
* add argument -a "<compose action>"
