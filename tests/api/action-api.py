#!/usr/bin/python3
import requests

jobj = {'params': {'cmd': 'reset'}}

response = requests.post(
    'http://localhost:3100/feeder/system/cmd', json=jobj)

print(response.status_code)
