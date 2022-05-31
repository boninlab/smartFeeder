#!/usr/bin/python3
import requests

payload = {
    "switchPress0": {
        "0": {"taskType": "vibHopper", "params": {"hopperNum": 0, "duration": {"min": 1, "sec": 0}}},
        "1": {"taskType": "vibHopper", "params": {"hopperNum": 1, "duration": {"min": 1, "sec": 0}}},
        "2": {"taskType": "waterClean", "params": {"duration": {"min": 1, "sec": 0}}},
        "3": {"taskType": "blowerClean", "params": {"duration": {"min": 1, "sec": 0}}}
    }
}

devid = "jinhae-feeder-3"
setting = 'switch'

response = requests.post(
    "https://aquafarmdb.koast.tech/edge/feeder/settings/{setting}/{devid}".format(setting=setting, devid=devid), json=payload)

print(response.status_code)
print(response.text)
