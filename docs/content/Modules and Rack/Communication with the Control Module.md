Commands can be sent via USB-to-serial or via UDP (Ethernet). All commands are case-sensitive.


The following commands can be used:

To use in terminal: echo 'help' | netcat -u 192.168.0.108 8880 -w 1
# USB-to-Serial communication
- Baud rate: TODO
- other settings: TODO

# Commands
All commands and arguments are case-sensitive.
# General Commands

```
help
```
Returns a helpful information TODO: what exactly?

Arguments: None

```
debug mode
```
Turns the debug mode on or off

Arguments:
- `mode`: either `on` or `off`

```
SETDEV slot module_type
```
Configures a module. This command has to be run before module-specific commands can be used.

Arguments:
- `slot`: Slot of the rack. See [[The Rack#Usage of the Slots|Usage of the Slots]]. Allowed values range from 0 to 7.
- `module_type`: Type of module. Currently, these values are allowed: `DAC4D`, TODO: complete list here

```
reset
```

# DAC4D Module
These commands are specific to the DAC4D module.
```
DAC4D mode slot output_channel voltage
```
Arguments:
- `mode`: either `VS` for single-ended voltage source (each of the two inner triax conductor is independent) or `VSD` for differential voltage source (given value is difference between inner triax conductors).
- `slot`: Slot of the rack. See [[The Rack#Usage of the Slots|Usage of the Slots]]. Allowed values range from 0 to 7.
- `output_channel`: Output on the module front panel. If `mode` is `VS`, this value can be between 0 and 7.  If `mode` is `VSD`, this value can be between 0 and 3.
- `voltage`: voltage to apply in Volts. Ranges from -10V to 10V.

  
# DAC16D Module
TODO: clean this up once a DAC16D has been tested

DAC 16 differential + 500mA 5V + 8V 1mA + 1 diff ADC
```
DAC16D VS [board (0 - 7)] [channel (0-31)] [voltage (-10/10)]
```

-DAC16D VSD [board (0 - 7)] [channel (-3-15) ] [voltage (-10/10)]

*ch -1 first half, ch -2 second, ch -3 all of them 

-DAC16D VR [board (0 - 7)] 

-DAC16D VSB [board (0 - 7)] [voltage (0 to 8)]

# ADC4 Module
TODO: clean this up once a ADC4 has been tested

4ADC + 4DAC

-FAFD VR [board (0 - 7)] [channel (0-3)] 

-FAFD VS [board (0 - 7)] [channel (0-3)] [voltage (0/2.5)]

  

4DAC high current

-HIC4 VS [board (0 - 7)] [channel (0-3)] [voltage (TBD)]

  

4ADC differential

-ADC4D VRD [board (0 - 7)] [channel (0 - 4)]
# DAC16  differential RJ45 Module
TODO: clean this up once a DAC16D has been tested
DAC 16 differential RJ45

-DAC4ETH VS [board (0 - 7)] [channel (0-31)] [voltage (-10/10)]

-DAC4ETH VSD [board (0 - 7)] [channel (0-15) ] [voltage (-10/10)]