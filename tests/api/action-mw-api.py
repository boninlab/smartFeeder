#!/usr/bin/python3
import requests


payload = {'params': {'cmd': 'reset'}}
actType = 'system'
devid = "jinhae-feeder-3"
act = 'cmd'

response = requests.post(
    "https://aquafarmdb.koast.tech/edge/feeder/{actType}/{act}/{devid}".format(actType=actType, act=act, devid=devid), json=payload)

print(response.status_code)
