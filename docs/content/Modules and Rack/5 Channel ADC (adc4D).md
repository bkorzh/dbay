# 5 Channel ADC (adc4D)

![[adc4D_icon.svg| 50]]

The ADC4D module is a 5-channel differential analog-to-digital converter (ADC) that provides high-precision voltage sensing capabilities for the D-Bay system.

## Features

- **5 Differential Channels**: Each channel can measure differential voltages
- **High Precision**: Built on the AD7124-4 ADC chip
- **Real-time Monitoring**: Continuous voltage measurement and display
- **Individual Channel Control**: Each channel can be enabled/disabled independently
- **Modern UI**: Clean, intuitive interface for voltage monitoring

## Hardware Specifications

- **ADC Resolution**: 24-bit
- **Input Range**: Configurable (typically ±2.5V with internal reference)
- **Sampling Rate**: Configurable
- **Input Impedance**: High impedance differential inputs
- **Communication**: SPI interface with D-Bay controller

## Software Components

### Frontend Components

- **`adc4D.svelte`**: Main module component
- **`adc4D_data.svelte.ts`**: Data management and state handling
- **`SenseChannel.svelte`**: Individual channel component
- **`SenseChannelBar.svelte`**: Channel grouping component
- **`SenseDisplay.svelte`**: Voltage value display
- **`SenseChannelContent.svelte`**: Channel control content

### Backend Integration

- **API Endpoint**: `/adc4D/vsense/`
- **Controller**: `adc4DController` for hardware communication
- **Data Structure**: `VsenseChange` interface for voltage sensing operations

## Usage

### Basic Operation

1. **Channel Activation**: Enable individual channels for measurement
2. **Voltage Monitoring**: Real-time voltage values displayed in the UI
3. **Measurement Control**: Start/stop measurements per channel
4. **Data Export**: Voltage readings available through API

### API Integration

```javascript
// Request voltage measurement update
const senseUpdate = await requestSenseUpdate(
  {
    module_index: 0,
    index: 0,
    voltage: 0,
    measuring: true,
    name: "Channel 1",
  },
  "/adc4D/vsense/"
);
```

### Code Example

```typescript
// Create ADC4D module instance
const adc = new adc4D({
  core: { slot: 0, type: "adc4D", name: "Voltage Sensor" },
});

// Enable channel 0 for measurement
adc.vsense.channels[0].measuring = true;
```

## Channel Configuration

Each channel supports the following properties:

- **`index`**: Channel number (0-4)
- **`voltage`**: Current measured voltage value
- **`measuring`**: Enable/disable measurement
- **`name`**: Custom channel name for identification

## Integration with D-Bay System

The ADC4D module integrates seamlessly with the D-Bay module system:

- **Automatic Discovery**: Detected and registered automatically
- **Hot-swap Support**: Can be added/removed during operation
- **State Persistence**: Settings maintained across sessions
- **Error Handling**: Robust error detection and reporting

## Technical Details

### Hardware Communication

- **SPI Protocol**: High-speed serial communication
- **Chip Select**: Individual CS pin for each module
- **Reference Voltage**: Internal or external reference options
- **Filtering**: Hardware and software filtering options

### Data Processing

- **Real-time Updates**: Continuous measurement updates
- **Noise Filtering**: Software filtering for stable readings
- **Calibration**: Built-in calibration routines
- **Error Detection**: Input range and connection monitoring

## Troubleshooting

### Common Issues

1. **No Voltage Readings**

   - Check channel enable status
   - Verify hardware connections
   - Confirm module power

2. **Inaccurate Readings**

   - Check reference voltage
   - Verify calibration
   - Check for noise sources

3. **Communication Errors**
   - Verify SPI connections
   - Check module addressing
   - Restart module controller

### Error Codes

- **Channel Out of Range**: Invalid channel index (0-4)
- **Communication Timeout**: SPI communication failure
- **Reference Error**: Reference voltage issue
- **Overrange**: Input voltage exceeds range

## Development Notes

### Adding New Features

The ADC4D module follows the standard D-Bay module architecture:

1. **Frontend**: Svelte components for UI
2. **Data Layer**: TypeScript classes for state management
3. **API Layer**: FastAPI endpoints for backend communication
4. **Hardware Layer**: Firmware drivers for ADC control

### Testing

- **Unit Tests**: Component and function testing
- **Integration Tests**: Full system testing
- **Hardware Tests**: Real hardware validation
- **Performance Tests**: Speed and accuracy validation

## See Also

- [DAC4D Module](<4%20Channel%20Differential%20(dac4D).md>) - Complementary voltage source
- [DAC16D Module](<16%20Channel%20Differential%20(dac16D).md>) - Higher channel count DAC
- [Module Development Guide](../Development/Tutorial%20-%20creating%20a%20new%20module.md)
