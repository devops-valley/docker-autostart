#!/bin/bash

cmd=${2:-"up -d"}
while read service; do
	docker-compose -f "${service%/docker-compose.yml}/docker-compose.yml" "$cmd";
done < "$1"