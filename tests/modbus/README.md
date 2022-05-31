### 테스트 프로그램(smart_feeder/tests/modbus/)
```
rotation-motor-test.py
  :먹이 공급기 2개 (inverter, relay read)
  ex) ./rotation-motor-test.py ./json/rotation-motor/hopper1-rotation-motor-test.json
  
inverter-test.py 
  :사료 진동 2개 (inverter), 블로어 1개 (inverter)
  ex) ./inverter-test.py json/inverter/vibration1-inverter-test.json
  
mode-write-test.py
  :릴레이 onoff 모드(blowClean,waterClean,tankOpen)
  ex) ./mode-write-test.py json/relay-mode/blowerClean-write-test.json
  
read-adam5-test.py, write-adam5-test.py
  :릴레이 r/w (slot0,1,2,3)
```