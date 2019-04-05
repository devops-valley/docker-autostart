import argparse
import json
import os
import subprocess
import logging
import sys

log = logging.getLogger(__name__)


def change_service(path, action):
	cmd = ["docker-compose"] + action.split()
	if path.endswith("/docker-compose.yml"):
		path = path[:-len("/docker-compose.yml")]
	r = subprocess.run(cmd, cwd=path)
	log.info(f"processed {path}", extra={"path": path, "cmd": cmd, "returncode": r.returncode})


def load_json(config_file):
	with open(config_file, "r") as src:
		data = json.load(src)
		return [os.path.join(base, service) for base in data for service in data[base]]

def load_raw(config_file):
	with open(config_file) as src:
		return [line.strip() for line in src]

def load_stdin(_):
	for line in sys.stdin:
		yield line.strip()

def get_loader(config_file):
	if config_file.endswith(".json"):
		return load_json
	if "-" == config_file:
		return load_stdin
	return load_raw

def apply(config_file, action):
	load = get_loader(config_file)
	for path in load(config_file):
		change_service(path, action)


if __name__ == "__main__":
	logging.basicConfig(format="%(message)s (status %(returncode)s)", level=logging.INFO)
	parser = argparse.ArgumentParser(description="Docker-compose Autostart")
	parser.add_argument("config_file", default="-", help="json file, plain text list or - for stdin")
	parser.add_argument("--action", "-a", default="up -d", help="docker-compose action to apply, default: up -d")
	args = parser.parse_args()

	apply(args.config_file, args.action)
