import argparse
import json
import os
import subprocess
import logging

log = logging.getLogger(__name__)


def change_service(path, cmd):
	r = subprocess.run(cmd, cwd=path)
	log.info(f"processed {path}", extra={"path": path, "cmd": cmd, "returncode": r.returncode})


def load_json(config_file):
	with open(config_file, "r") as src:
		data = json.load(src)
		return [os.path.join(base, service) for base in data for service in data[base]]


def load_raw(config_file):
	with open(config_file) as src:
		return [line.strip() for line in src]


config_types = {
	"json": load_json,
	"raw": load_raw
}


def apply(config_file, action, type):
	cmd = ["docker-compose"] + action.split()
	for path in config_types[type](config_file):
		change_service(path, cmd)


if __name__ == "__main__":
	logging.basicConfig(format="%(message)s (status %(returncode)s)", level=logging.INFO)
	parser = argparse.ArgumentParser(description="Docker-compose Autostart")
	parser.add_argument("config_file")
	parser.add_argument("--type", "-t", default="raw", choices=config_types)
	parser.add_argument("--action", "-a", default="up -d")
	args = parser.parse_args()

	apply(args.config_file, args.action, args.type)
