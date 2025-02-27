from dbay.client import DBay
import time

client = DBay("0.0.0.0")


# with the GUI, place a dac4D in slot 1 and a dac16D in slot 2

client.modules[0].voltage_set(0, 1)
time.sleep(1)
client.modules[0].voltage_set(0, 2, activated=True)
time.sleep(1)
client.modules[0].voltage_set(0, 3, activated=True)
time.sleep(1)
client.modules[0].voltage_set(0, 4, activated=False)
time.sleep(1)
client.modules[0].voltage_set(0, 5, activated=False)
time.sleep(1)
client.modules[0].voltage_set(0, 3.33)


client.modules[1].voltage_set(0, 1, activated=True)
time.sleep(1)
client.modules[1].voltage_set(1, 2, activated=True)
time.sleep(1)

client.modules[1].voltage_set(0, 0, activated=False)
client.modules[1].voltage_set(1, 0, activated=False)

ch = [True, False] * 8
for i in range(16):
    client.modules[1].voltage_set_shared(i * 0.1, channels=ch)
    time.sleep(0.3)
time.sleep(1)
