import argparse
import json
import os
import subprocess
import logging
import sys

log = logging.getLogger(__name__)


def change_service(path, action, pre_cmd=None, post_cmd=None):
	cmd = ["docker-compose"] + action.split()
	if path.endswith("/docker-compose.yml"):
		path = path[:-len("/docker-compose.yml")]
	args = {
		"args": cmd,
		"cwd": path,
	}
	if post_cmd:
		args["capture_output"] = True
		args["text"] = True
	if pre_cmd:
		subprocess.run(pre_cmd.format(path=path, cmd=cmd, step="pre").split())
	r = subprocess.run(**args)
	log.info(f"processed {path}", extra={"path": path, "cmd": cmd, "returncode": r.returncode})
	if post_cmd:
		if r.stdout: print(r.stdout)
		if r.stderr: print(r.stderr, file=sys.stderr)
		subprocess.run(post_cmd.format(path=path, cmd=cmd, step="post", returncode=r.returncode, stdout=r.stdout, stderr=r.stderr).split())
		print()


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

def apply(config_file, action, pre=None, post=None):
	load = get_loader(config_file)
	for path in load(config_file):
		change_service(path, action, pre_cmd=pre, post_cmd=post)

def base_args(desc):
	parser = argparse.ArgumentParser(description=desc)
	parser.add_argument("--action", "-a", default="up -d", help="docker-compose action to apply, default: up -d")
	parser.add_argument("--pre", "-s", help="pre-exec: command to run before each action")
	parser.add_argument("--post", "-e", help="post-exec: command to run after each action")
	return parser
	

if __name__ == "__main__":
	logging.basicConfig(format="%(message)s (status %(returncode)s)", level=logging.INFO)
	parser = base_args("Docker-compose Autostart")
	parser.add_argument("config_file", default="-", help="json file, plain text list or - for stdin")
	args = parser.parse_args()

	apply(args.config_file, args.action, pre=args.pre, post=args.post)
