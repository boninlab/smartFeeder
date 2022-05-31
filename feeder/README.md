# MQTT

### TASK
```
# 전체 초기화
mosquitto_pub -t 'feeder/system/cmd' -m "{'params':{'cmd':'reset'}}"

# Task 일시정지
mosquitto_pub -t 'feeder/task/cmd' -m "{'params':{'cmd':'pause'}}"

# Task 재개
mosquitto_pub -t 'feeder/task/cmd' -m "{'params':{'cmd':'resume'}}"

# 물 청소
mosquitto_pub -t 'feeder/task/add' -m "{'taskType':'waterClean','params':{'duration':{'min': 20, 'sec': 1},'startDateTime':'2022-04-18 13:50:10'}}"

# 블로워 청소
mosquitto_pub -t 'feeder/task/add' -m "{'taskType':'blowerClean','params':{'duration':{'min': 0, 'sec': 10},'startDateTime':'2022-04-18 13:50:10'}}"

# 먹이 털기(진동 모터)
mosquitto_pub -t 'feeder/task/add' -m "{'taskType':'vibHopper','params':{'hopperNum':0,'duration':{'min': 0, 'sec': 1},'startDateTime':'2022-04-18 13:50:10'}}"

# 수조 먹이 공급
mosquitto_pub -t 'feeder/task/add' -m "{'taskType':'feedTank','params':{'hopperNum':0,'tankNum':5,'count':5,'startDateTime':'2022-04-18 13:50:10'}}"
```

### JOB
```
# --- timer

mosquitto_pub -t 'feeder/job/add' -m "{'jobType':'jobTimer','params':{'duration':{'min': 0, 'sec': 1}}}"

# --- inverter

# feeder
mosquitto_pub -t 'feeder/job/add' -m "{'jobType':'feeder','params':{'devNum':0,'action':{'value':60,'count':20}}}"

# vibrationMotor
mosquitto_pub -t 'feeder/job/add' -m "{'jobType':'vibMotor','params':{'devNum':0,'action':60}}"

# blower
mosquitto_pub -t 'feeder/job/add' -m "{'jobType':'blower','params':{'devNum':0,'action':30}}"

# --- on/off

# tank
mosquitto_pub -t 'feeder/job/add' -m "{'jobType':'tankValve','params':{'devNum':1,'action':'open'}}"

# startValve
mosquitto_pub -t 'feeder/job/add' -m "{'jobType':'startValve','params':{'devNum':0,'action':'water'}}"

# waterValve
mosquitto_pub -t 'feeder/job/add' -m "{'jobType':'waterValve','params':{'devNum':0,'action':'open'}}"

# warnLight
mosquitto_pub -t 'feeder/job/add' -m "{'jobType':'warnLight','params':{'devNum':0,'action':'on'}}"
```

# Redis
### 형태

```
status/<장치 타입>/value # 장치 상태 값
status/<장치 타입>/lasttime # 읽은 마지막 시간

ex)
"status/tankValve8/value" "False" # 8번 수조 밸브 꺼짐 True/False (string)
"status/tankValve8/lasttime" "2022-05-17 14:13:06.838675" # 8번 수조 밸브 상태 읽은 마지막 시간 datetime (string)

list값을 가진 장치의 경우 hex로 기록
ex)
"status/relay0/value" "0x80" # relay0: [True, False, False, False, False, False, False, False] (string)
```

### device status key(value) 목록 참고
```
# ------------------------------------------------------ hex value
"status/valveStatus0/value" # 밸브 상태 (DI0)
"status/valveStatus1/value" # 밸브 상태 (DI1)
"status/switchPress0/value" # switch press DI
"status/proxiSensor0/value" # 근접 센서
"status/relay0/value" # 릴레이0
"status/relay1/value" # 릴레이1

# ------------------------------------------------------- bool value
"status/startValve0/value" # 시작 밸브(블로워on,물off)
"status/waterValve0/value" # 입수 밸브

"status/tankValve1/value" # 수조 밸브 1~11
"status/tankValve2/value"
"status/tankValve3/value"
"status/tankValve4/value"
"status/tankValve5/value"
"status/tankValve6/value"
"status/tankValve7/value"
"status/tankValve8/value"
"status/tankValve9/value"
"status/tankValve10/value"
"status/tankValve11/value"
```
