
# Rack Customisation

The rack is custom made from VectorInc and is modified as specified in this document:
[[2025_02_09_VectorInc_rack_specs_for_dbay.pdf]].

*Note:* Some pins of the connectors in the backplane are removed. This is necessary for the address circuitry to work (see [[Install a Module#1. Setting the I2C Address#1a. Current method]]).

# Usage of the Slots
The picture below shows how the slots have to be used.
![[rack_slots.svg]]
The rightmost slot has to be populated with a control module and the second slot to the right has to be empty. The reason is that the addressing uses 3 bits only and thus this slot cannot be controlled by the control module.

The slots 0 to 7 can be populated with any module except for the control module.
# Further reading:
- [[Install the Control Module]]
- [[Install a Module]]