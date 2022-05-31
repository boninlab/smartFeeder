### TASK
```
# 상태 초기화
mosquitto_pub -t 'feeder/add/task' -m "{'taskType':'initState'}"

# 물 청소
mosquitto_pub -t 'feeder/add/task' -m "{'taskType':'waterClean','params':{'duration':{'min': 0, 'sec': 1}}}"

# 블로워 청소
mosquitto_pub -t 'feeder/add/task' -m "{'taskType':'blowerClean','params':{'duration':{'min': 0, 'sec': 1}}}"

# 먹이 털기(진동 모터)
mosquitto_pub -t 'feeder/add/task' -m "{'taskType':'vibHopper','params':{'duration':{'min': 0, 'sec': 1}}}"

# 수조 먹이 공급
mosquitto_pub -t 'feeder/add/task' -m "{'taskType':'feedTank','params':{'hopperNum':0,'tankNum':5,'count':5}}"
```

### JOB
```
# 타이머
mosquitto_pub -t 'feeder/add/job' -m "{'jobType':'jobTimer','params':{'duration':{'min': 0, 'sec': 1}}}"

# feeder
mosquitto_pub -t 'feeder/add/job' -m "{'jobType':'feeder','params':{'devNum':0,'action':{'freq':25,'count':1}}}"

# vibrationMotor
mosquitto_pub -t 'feeder/add/job' -m "{'jobType':'vibMotor','params':{'devNum':0,'action':40}}"

# tank
mosquitto_pub -t 'feeder/add/job' -m "{'jobType':'tankValve','params':{'devNum':1,'action':'open'}}"

# blower
mosquitto_pub -t 'feeder/add/job' -m "{'jobType':'blower','params':{'devNum':0,'action':40}}"

# startValve
mosquitto_pub -t 'feeder/add/job' -m "{'jobType':'startValve','params':{'devNum':0,'action':'water'}}"

# waterValve
mosquitto_pub -t 'feeder/add/job' -m "{'jobType':'waterValve','params':{'devNum':0,'action':'open'}}"
```
