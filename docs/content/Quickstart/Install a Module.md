# 1. Setting the I2C Address
On the card, there is a switch array controlling three bits (labelled A0, A1, A2 on the board). The switch array is displayed on the image below for the Dac4D module card. 
![[2025_12_11_address_switch.jpg]]This switch array defines the address of the module. Each card in a rack must have another address (except for the control module, which does not have an address). If there are already cards installed in the rack, check their address switch array and choose an unused address configuration for the switch. A0 is the least significant bit and A2 the most significant bit. 

**Examples** 
A0 = ON, A1 = OFF and A2 = OFF corresponds to an address 1. 
A0 = ON, A1 = OFF and A2 = ON corresponds to 0b101 = 5.

# 2. Inserting the Card
Please make sure that the rack is switched off and disconnect it from the mains power supply. Then insert the card in a free slots. The plastic rails guiding the card might not be in the correct position for the connector at the back to mate to the rack. You can take them out an insert them at the correct location.

# 3. Check if the Control Module Recognizes the Card
Now, power on the rack, connect the control module to the computer via USB and open the Arduino IDE (or any other software allowing to monitor serial communication) and connect to the board. If you use Arduino IDE, go to *Tools>Serial Monitor* . Send the command `reset` and check the reply. It should contain the line
```shell
I2C device found at address XXX !
```
where `XXX`is the value of the address you set.

# 4. Initializing the Module
This step depends on the way the rack is going to be used. Either, the initialization can be done in the frontendor directly via serial communication.
## Option 1: Via Serial Communication
With the serial monitor still open from step [[#3. Check if the Control Module Recognizes the Card]], send the command
```
SETDEV [address] [device_type]
```
with the address set in step [[#1. Setting the I2C Address]] and `device_type` is either `DAC4D` or TODO: what are the other devices?.  The `device_type` is case-sensitive. 

When `device_type` was `DAC4D`, then the control module answers with
```
deviceType: 1
DAC4D created
LTC268X initialization error 0
+ok
```
if there is no error. TODO: add answers for other modules.

Now, you can send module-specific commands via serial communication.


## Option 2: In the Frontend
### With the development environment
If you have the development environment set up ([[Development Setup]]), start the UI by following [[Development Setup#5. Start the Application]]. 

In the UI, click on the menu bar (![[menu_bar.png]]) and select *Add a module*. Then, in the newly opened box, select the module slot (it is the address value +1). Then select the module type and click *Add Module*.

### With Docker
TODO test and write