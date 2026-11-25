#include "dbay_4triaxADC.h"

dbay4triaxADC::dbay4triaxADC(int address, TwoWire *bus):dbayDev(address, bus){

    thisDeviceType = ADC4D;
    if (!BoardSel->pinMode(dbay4ADC_ADC_CS,OUTPUT)) {
        sprintf(_err, "Error setting pin mode for address 0x%1x ADC. Aborting...\n", BoardSel->boardN);
        Serial.print(_err);
        //rv = -1;
    }
    if (!BoardSel->digitalWrite(dbay4ADC_ADC_CS, HIGH)) {
        sprintf(_err, "Error setting address pin for board %i HIGH\n", BoardSel->boardN);
        Serial.print(_err);
        //rv = -1;
   }

        
    this->reset();
}

dbay4triaxADC::~dbay4triaxADC(){

}

int dbay4triaxADC::reset(){
    int adcCS = dbay4ADC_ADC_CS;
    adc = new Ad7124Chip();
    adc->begin(this->BoardSel, adcCS);
    // Setting the configuration 0:
    // - use of the internal reference voltage 2.5V
    // - gain of 1 for a bipolar measurement +/- 2.5V
    //adc->setConfig (0, Ad7124::RefIn1, Ad7124::Pga1, true);


    // Setting the configuration 0:
    // - use of the external reference 1
    // - gain of 1 for a bipolar measurement -> max/min voltages: +/- |external reference|
    adc->setConfig (0, Ad7124::RefIn1, Ad7124::Pga1, true);
    adc->setConfig (1, Ad7124::RefIn1, Ad7124::Pga1, true);
    adc->setConfig (2, Ad7124::RefIn1, Ad7124::Pga1, true);
    adc->setConfig (3, Ad7124::RefIn1, Ad7124::Pga1, true);

      // Setting channel 0 using pins AIN1(+)/AIN0(-)
    adc->setChannel (0, 0, Ad7124::AIN0Input, Ad7124::AIN1Input);
    adc->setChannel (1, 1, Ad7124::AIN2Input, Ad7124::AIN3Input);
    adc->setChannel (2, 2, Ad7124::AIN4Input, Ad7124::AIN5Input);
    adc->setChannel (3, 3, Ad7124::AIN6Input, Ad7124::AIN7Input);
      // Configuring ADC in Full Power Mode (Fastest)
    adc->setAdcControl (Ad7124::StandbyMode, Ad7124::FullPower, true);

return 0;

}

double dbay4triaxADC::ReadVoltage(int channel){
    long value;
    double voltage;
    Serial.print("Channel: ");
    Serial.println(channel);
    value = adc->read (channel);
    voltage = Ad7124Chip::toVoltage (value, 1, 3.4, true);
    // Serial.print("voltage on dac class TBD: ");
    // Serial.print(value);
    // Serial.print(" = ");
    // Serial.println(voltage);
   return voltage;

}
