// Victor Zhang, created August 20, 2018
// Arduino program to get Temperature, Pressure, and Relative Humidity of Lab
// version 1.0.0
// Arduino


#include "SparkFunBME280.h"
// Library allows either I2C or SPI, so include both.
#include "Wire.h"
#include "SPI.h" // will be using I2C connection
 
BME280 sensor ;
 
void setup ( )  {
 
   Serial. begin ( 9600 ) ;
  while  ( ! Serial )  {
    // Waiting for the serial port to open for Arduino LEONARDO
  }
  // sensor configuration
  sensor. settings . commInterface  = I2C_MODE ; 
  sensor. settings . I2CAddress  =  0x76 ;
  sensor. settings . runMode  =  3 ; 
  sensor. settings . tStandby  =  0 ;
  sensor. settings . filter  =  0 ;
  sensor. settings . tempOverSample  =  1  ;
  sensor. settings . pressOverSample  =  1 ;
  sensor. settings . humidOverSample  =  1 ;
 
  // loading the sensor configuration
  sensor. begin ( ) ;
    
}
 
void loop ( )  {
  Serial. print ( sensor.readTempC ( ) ) ;
  Serial.print(",");
  Serial. print ( sensor.readFloatPressure ( ) / 100 ) ; // converts from Pa to HPa
  Serial.print(",");
  Serial. println ( sensor.readFloatHumidity ( ) ) ;
  delay ( 10*1000 ) ;
}
