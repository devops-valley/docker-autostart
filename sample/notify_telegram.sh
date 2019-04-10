#!/bin/bash
key="$1"
room="$2"
shift 2
url="https://api.telegram.org/bot${key}/sendMessage"
json='{"chat_id":'${room}', "text":"'"$@"'"}'
curl "$url" --data "$json" -X POST -H 'Content-Type: application/json'