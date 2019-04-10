import os
import logging

from collections import namedtuple

from start import base_args, change_service

log = logging.getLogger(__name__)

COMPOSE_FILE = "docker-compose.yml"
CONFIG_CMD = "docker-compose -f {path} config "
AUTOSTART_KEY = "{prefix}.autostart=true"
PRIORITY_KEY = "{prefix}.autostart.priority="
PREFIX = "de.wie-ei"

Service = namedtuple("Service", ("path", "prio"))

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
	with open(service) as src:
		service_definitions = src.read()
		key = AUTOSTART_KEY.format(prefix=PREFIX)
		if not key in service_definitions:
			return False
		prio_key = PRIORITY_KEY.format(prefix=PREFIX)
		pos = service_definitions.find(prio_key)
		if pos >= 0:
			start = pos + len(prio_key)
			end = pos + service_definitions[pos:].find('"\n')
			prio = service_definitions[start:end]
			return int(prio)
		return True

def find_autostart_services(services):
	start_services = []
	for service in services:
		prio = should_autostart(service)
		if prio:
			start_services.append(Service(path=service, prio=prio))
	return [x.path for x in sorted(start_services, key=lambda x:x.prio, reverse=True)]
			

if __name__ == "__main__":
	logging.basicConfig(format="%(message)s (status %(returncode)s)", level=logging.INFO)
	parser = base_args("Docker-compose Autostart discovery")
	parser.add_argument("service_dir", nargs="+", help="One or more directories containing docker-compose services, only direct subdirectories are scanned")
	parser.add_argument("--list", "-l", action="store_true", help="list autostart services only, no action")
	parser.add_argument("--key", "-k", help=f"alternative label prefix, default: '{PREFIX}'")
	args = parser.parse_args()
	
	if args.key:
		PREFIX = args.key
	services = find_services(args.service_dir)
	autostarts = find_autostart_services(services)
	if args.list:
		if autostarts:
			print("\n".join(autostarts))
	else:
		import start
		for service in autostarts:
			start.change_service(service, args.action, pre_cmd=args.pre, post_cmd=args.post)