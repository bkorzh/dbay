from src.client import DBay
import time

dbay = DBay("0.0.0.0")


dbay.modules[0].voltage_set(0, 1)
time.sleep(1)
dbay.modules[0].voltage_set(0, 2)
time.sleep(1)
dbay.modules[0].voltage_set(0, 3)
time.sleep(1)
dbay.modules[0].voltage_set(0, 4, activated=False)
time.sleep(1)
dbay.modules[0].voltage_set(0, 5, activated=False)
time.sleep(1)
dbay.modules[0].voltage_set(0, 3.33)


dbay.modules[4].voltage_set(0, 1, activated=True)
time.sleep(1)
dbay.modules[4].voltage_set(1, 2, activated=True)
time.sleep(1)

dbay.modules[4].voltage_set(0, 0, activated=False)
dbay.modules[4].voltage_set(1, 0, activated=False)

ch = [True, False] * 8
for i in range(16):
    dbay.modules[4].voltage_set_shared(i * 0.1, channels=ch)
    time.sleep(0.3)
time.sleep(1)
