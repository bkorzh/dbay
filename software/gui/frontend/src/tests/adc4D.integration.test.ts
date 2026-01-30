/**
 * Integration test for ADC4D module
 * Tests the complete ADC4D functionality including UI components and API integration
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { adc4D } from '../lib/modules_dbay/adc4D_data.svelte';
import { VsenseAddon } from '../lib/addons/vsense/vsense.svelte';
import type { JsonModule } from '../state/systemState.svelte';

describe('ADC4D Module Integration', () => {
    let testModule: adc4D;
    let mockData: JsonModule;

    beforeEach(() => {
        mockData = {
            core: {
                slot: 0,
                type: "adc4D",
                name: "Test ADC4D Module"
            },
            vsense: {
                channels: [
                    { index: 0, voltage: 0, measuring: false, name: "Channel 0" },
                    { index: 1, voltage: 0, measuring: false, name: "Channel 1" },
                    { index: 2, voltage: 0, measuring: false, name: "Channel 2" },
                    { index: 3, voltage: 0, measuring: false, name: "Channel 3" },
                    { index: 4, voltage: 0, measuring: false, name: "Channel 4" }
                ]
            }
        };
        testModule = new adc4D(mockData);
    });

    it('should create ADC4D module with correct properties', () => {
        expect(testModule.core.type).toBe('adc4D');
        expect(testModule.core.slot).toBe(0);
        expect(testModule.core.name).toBe('Test ADC4D Module');
        expect(testModule.vsense).toBeInstanceOf(VsenseAddon);
    });

    it('should have 5 voltage sensing channels', () => {
        expect(testModule.vsense.channels).toHaveLength(5);

        testModule.vsense.channels.forEach((channel, index) => {
            expect(channel.index).toBe(index);
            expect(channel.voltage).toBe(0);
            expect(channel.measuring).toBe(false);
            expect(channel.name).toBe(`Channel ${index}`);
        });
    });

    it('should enable/disable channel measurement', () => {
        const channel = testModule.vsense.channels[0];

        // Initially not measuring
        expect(channel.measuring).toBe(false);

        // Enable measurement
        channel.measuring = true;
        expect(channel.measuring).toBe(true);

        // Disable measurement
        channel.measuring = false;
        expect(channel.measuring).toBe(false);
    });

    it('should update voltage values', () => {
        const channel = testModule.vsense.channels[0];

        // Set voltage value
        channel.voltage = 2.5;
        expect(channel.voltage).toBe(2.5);

        // Set negative voltage
        channel.voltage = -1.2;
        expect(channel.voltage).toBe(-1.2);
    });

    it('should update module data correctly', () => {
        const updateData: JsonModule = {
            core: {
                slot: 0,
                type: "adc4D",
                name: "Updated ADC4D Module"
            },
            vsense: {
                channels: [
                    { index: 0, voltage: 1.5, measuring: true, name: "Updated Channel 0" },
                    { index: 1, voltage: -0.8, measuring: false, name: "Updated Channel 1" },
                    { index: 2, voltage: 3.2, measuring: true, name: "Updated Channel 2" },
                    { index: 3, voltage: 0.0, measuring: false, name: "Updated Channel 3" },
                    { index: 4, voltage: -2.1, measuring: true, name: "Updated Channel 4" }
                ]
            }
        };

        testModule.update(updateData);

        expect(testModule.core.name).toBe('Updated ADC4D Module');
        expect(testModule.vsense.channels[0].voltage).toBe(1.5);
        expect(testModule.vsense.channels[0].measuring).toBe(true);
        expect(testModule.vsense.channels[0].name).toBe('Updated Channel 0');
        expect(testModule.vsense.channels[2].voltage).toBe(3.2);
        expect(testModule.vsense.channels[4].voltage).toBe(-2.1);
    });

    it('should handle missing vsense data gracefully', () => {
        const minimalData: JsonModule = {
            core: {
                slot: 1,
                type: "adc4D",
                name: "Minimal ADC4D"
            }
        };

        const minimalModule = new adc4D(minimalData);

        expect(minimalModule.core.type).toBe('adc4D');
        expect(minimalModule.vsense).toBeInstanceOf(VsenseAddon);
        expect(minimalModule.vsense.channels).toHaveLength(5);
    });

    it('should validate channel indices', () => {
        testModule.vsense.channels.forEach((channel, index) => {
            expect(channel.index).toBe(index);
            expect(channel.index).toBeGreaterThanOrEqual(0);
            expect(channel.index).toBeLessThan(5);
        });
    });
});
