from src.client import DBay
import time

dbay = DBay("0.0.0.0")


dbay.modules[0].voltage_set(0, 1)
time.sleep(1)
dbay.modules[0].voltage_set(0, 2)
time.sleep(1)
dbay.modules[0].voltage_set(0, 3)
time.sleep(1)
dbay.modules[0].voltage_set(0, 4)
time.sleep(1)
dbay.modules[0].voltage_set(0, 5)
time.sleep(1)
dbay.modules[0].voltage_set(0, 3.33)
