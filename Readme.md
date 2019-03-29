# Usage

## json config
* create config.json from sample.json
* add `python3 /opt/docker-autostart/start.py /path/to/your/config.json -t json` to `/etc/rc.local`

## raw config
* create config.lst from sample.lst
* add `python3 /opt/docker-autostart/start.py /path/to/your/config.lst` to `/etc/rc.local`

## other actions
* default action: up -d
* add argument -a "<compose action>"