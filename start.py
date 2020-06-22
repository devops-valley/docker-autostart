import argparse
import json
import os
import subprocess
import logging
import sys

log = logging.getLogger(__name__)

def run(cmd, kwargs={}, dry_run=False):
	if dry_run:
		log.info(f"tried to run: `{cmd}, {kwargs}`, dry_run=True", extra={"path": "/dry/run/", "cmd": cmd, "returncode": -99})
		return subprocess.CompletedProcess(cmd, -99)
	return subprocess.run(cmd, **kwargs)

def change_service(path, action, pre_cmd=None, post_cmd=None, dry_run=False):
	cmd = ["docker-compose"] + action.split()
	if path.endswith("/docker-compose.yml"):
		path = path[:-len("/docker-compose.yml")]
	args = {
		"cwd": path,
	}
	if post_cmd:
		args["capture_output"] = True
		args["text"] = True
	if pre_cmd:
		run(pre_cmd.format(path=path, cmd=cmd, step="pre").split(), dry_run=dry_run)
	r = run(cmd, args, dry_run=dry_run)
	log.info(f"processed {path} (status {r.returncode})", extra={"path": path, "cmd": cmd, "returncode": r.returncode})
	if post_cmd:
		if r.stdout: print(r.stdout)
		if r.stderr: print(r.stderr, file=sys.stderr)
		run(post_cmd.format(path=path, cmd=cmd, step="post", returncode=r.returncode, stdout=r.stdout, stderr=r.stderr).split(), dry_run=dry_run)
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

def apply(config_file, action, pre=None, post=None, dry_run=False):
	load = get_loader(config_file)
	for path in load(config_file):
		change_service(path, action, pre_cmd=pre, post_cmd=post, dry_run=dry_run)

def base_args(desc):
	parser = argparse.ArgumentParser(description=desc)
	parser.add_argument("--action", "-a", default="up -d", help="docker-compose action to apply, default: up -d")
	parser.add_argument("--pre", "-s", help="pre-exec: command to run before each action")
	parser.add_argument("--post", "-e", help="post-exec: command to run after each action")
	parser.add_argument("--dry-run", "-d", action="store_true", help="dry run: only print commands")
	parser.add_argument("--log", default="INFO", choices=["INFO","DEBUG","WARNING"], help="log level (default: %(default)s)")
	return parser
	

if __name__ == "__main__":
	parser = base_args("Docker-compose Autostart")
	parser.add_argument("config_file", default="-", help="json file, plain text list or - for stdin")
	args = parser.parse_args()
	logging.basicConfig(format="%(message)s", level=getattr(logging, args.log))

	apply(args.config_file, args.action, pre=args.pre, post=args.post, dry_run=args.dry_run)
