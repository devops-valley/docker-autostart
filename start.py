import argparse
import json
import os
import subprocess

def start(config):
	with open(config, "r") as src:
		data = json.load(src)
	if data:
		for base in data:
			for service in data[base]:
				path = os.path.join(base, service)
				print(path)
				r = subprocess.run(["docker-compose", "up", "-d"], cwd=path)
				print(r)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Docker-compose Autostart")
	parser.add_argument("config_file")
	
	args = parser.parse_args()
	
	start(args.config_file)
	