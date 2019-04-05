import argparse
import json
import os
import subprocess
import logging

log = logging.getLogger(__name__)

COMPOSE_FILE = "docker-compose.yml"
CONFIG_CMD = "docker-compose -f {path} config "
AUTOSTART_KEY = 'de.wie-ei.autostart: "true"'
AUTOSTART_KEY = 'de.wie-ei.autostart=true'

def complete_compose(entry):
	path = entry.path
	if not path.endswith(COMPOSE_FILE):
		return os.path.join(path, COMPOSE_FILE)
	return path

def has_compose(path):
	return os.path.exists(path)

def find_services(dirs):
	entries = [entry for base in dirs for entry in os.scandir(base) if entry.is_dir()]
	return filter(has_compose, map(complete_compose, entries))

def should_autostart(service):
	#r = subprocess.run(CONFIG_CMD.format(path=service).split(), capture_output=True, encoding="utf8")
	#return AUTOSTART_KEY in r.stdout
	with open(service) as src:
		return AUTOSTART_KEY in src.read()

def find_autostart_services(services):
	return list(filter(should_autostart, services))
			

if __name__ == "__main__":
	logging.basicConfig(format="%(message)s (status %(returncode)s)", level=logging.INFO)
	parser = argparse.ArgumentParser(description="Docker-compose Autostart discovery")
	parser.add_argument("service_dir", nargs="+")
	parser.add_argument("--action", "-a", default="up -d")
	parser.add_argument("--list", "-l", action="store_true", help="list autostart services only, no action")
	parser.add_argument("--key", "-k", help="alternative label")
	args = parser.parse_args()
	
	if args.key:
		AUTOSTART_KEY = args.key
	services = find_services(args.service_dir)
	autostarts = find_autostart_services(services)
	if args.list:
		print("\n".join(autostarts))
	else:
		import start
		for service in autostarts:
			start.change_service(service, args.action)