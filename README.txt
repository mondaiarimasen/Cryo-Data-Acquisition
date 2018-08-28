%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%% Cryo-Data-Acquisition %%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

mondaiarimasen
Created August 14, 2018

*****************************************************************************
I. Motivation

  - have a place to read and monitor:
        > temperature of the channels of the cryostat / dilution
          refrigerator (DR)
        > flow rate of the cooling water of the He compressor outside
          building
        > temperature of the He compressor (not yet implemented)
        > temperature, pressure, and relative humidity of the lab room
        > amount of nitrogen left in the nitrogen trap (not yet implemented)

  - send email warnings when readings are not in desired range

  - monitor instruments from the office room while the DR is operating,
    without having to go to the lab room

*****************************************************************************
II. Program Descriptions

  - arduino_LabPTH/arduino_LabPTH.ino
        > gets the lab temperature, pressure, and relative humidity from
          connected Arduino device
        > sends the data to serial port, which cryo-RealTime.py reads and
          updates to cryo-Environment-Data.dat

  - cryo-DataView.html
        > website to view all data read by cryo-RealTime.py
        > refreshes at user-decided frequency
        > currently, data table with temperature readings from LS372 can
          only be displayed in Firefox, independent of operating system
        > displays plots produced in real time by cryo-RealTime.py
        > sends email notifications

  - cryo-Environment-Data.dat
        > text file containing data from the environment around the cryostat
        > PLEASE DO NOT DELETE WHITESPACES/EMPTY LINES BETWEEN LINES AS
          IN cryo-DataView.html AND cryo-RealTime.py THE POSITIONS OF SEVERAL
          VARIABLES BELOW ARE HARDCODED
        > stores the values in the following order (please do not change):
              * chl1_Low (lower temp limit, K, of Chl 1, PT2 Head)
              * chl1_Up (upper temp limit, K, of Chl 1, PT2 Head)
              * chl2_Low (lower temp limit, K, of Chl 2, PT2 Plate)
              * chl2_Up (upper temp limit, K, of Chl 2, PT2 Plate)
              * chl3_Low (lower temp limit, K, of Chl 3, 1 K Plate)
              * chl3_Up (upper temp limit, K, of Chl 3, 1 K Plate)
              * chl4_Low (lower temp limit, K, of Chl 4, Still)
              * chl4_Up (upper temp limit, K, of Chl 4, Still)
              * chl5_Low (lower temp limit, K, of Chl 5, mK Plate Cernox)
              * chl5_Up (upper temp limit, K, of Chl 5, mK Plate Cernox)
              * chl6_Low (lower temp limit, K, of Chl 6, PT1 Head)
              * chl6_Up (upper temp limit, K, of Chl 6, PT1 Head)
              * chl7_Low (lower temp limit, K, of Chl 7, PT1 Plate)
              * chl7_Up (upper temp limit, K, of Chl 7 PT1 Plate)
              * chl8_Low (lower temp limit, K, of Chl 8, mK Plate RuOx)
              * chl8_Up (upper temp limit, K, of Chl 8, mK Plate RuOx)
              * coolWaterFR (cooling water flow rate, L/min)
              * coolWaterFR_Low (lower limit of coolWaterFR, L/min)
              * coolWaterFR_Up (upper limit of coolWaterFR, L/min)
              * tempHeComp (temp. of He compressor, K)
              * tempHeComp_Low (lower temp. limit of tempHeComp, K)
              * tempHeComp_Up (upper temp. limit of tempHeComp, K)
              * tempLab (temp. of lab room with cryostat, C)
              * tempLab_Low (lower temp. limit of tempLab, C)
              * tempLab_Up (lower temp. limit of tempLab, C)
              * presLab (pres. of lab room with cryostat, hPa)
              * presLab_Low (lower temp. limit of presLab, hPa)
              * presLab_Up (lower temp. limit of presLab, hPa)
              * humLab (humidity of lab room with cryostat, %)
              * humLab_Low (lower hum. limit of humLab, %)
              * humLab_Up (upper hum. limit of humLab, %)
              * nitroTrapWght (weight of N2 trap, kg)
              * nitroTrapWght_Low (lower limit of nitroTrapWght, kg)
              * nitroTrapWght_Up (upper limit of nitroTrapWght, kg)
              * dataBWTDisChlTemp (# of data pts. between each displayed chl
                temp on HTML page)
              * dataDisNum (# of data rows in chl temp displayed)

  - cryo-Lab-TPH.dat
        > text file containing all lab temperature, pressure, and relative
          humidity, as measured by Arduino device in one run
        > most recent value is stored in cryo-Environment-Data.dat

  - cryo-LS372-Temp.dat
        > text file containing temperature readings of all 8 channels of the
          LS372 and time of measurement, over a period of time and frequency
          set in cryo-RealTime.py
        > cryo-RealTime.py writes to this file
        > cryo-DataView.html reads this file to display on the website

  - cryo-RealTime.py
        > gets DR data from the Lake Shore 372 (LS372) device; records to
          cryo-LS372-Temp.dat
        > two types of plots are drawn: 'static' graph (x-axis is not
          fixed length, so accommodates more and more data with time) and
          'shifting' graph (x-axis is fixed length so plot moves to always
          show most recent data; how recent is user-decided)
        > plots all 8 channels on static graph, and PT1, PT2, 1K, and mK
          plate temp. on separate shifting graphs
        > gets lab temp., pres., and rel. hum. from Arduino device; records
          to cryo-Lab-TPH.dat; plots data on sep. shifting graphs; saves
          most recent data to cryo-Environment-Data.dat
        > gets cooling water flow rate data from LabJack U3-LV; records to
          cryo-WaterMeas.dat; plots data on shifting graph; saves most
          recent data to cryo-Environment-Data.dat
        > saves all plots generated
        > as of August 24, 2018, the x-axis date and time labels of the
          plots generated in real time are NOT accurate, but saved date
          and time values in cryo-LS372-Temp.dat ARE accurate

  - cryo-WaterMeas.dat
        > text file containing the calculated cooling water flow rate from
          the measured voltage from the LabJack U3-LV
        > most recent value stored in cryo-Environment-Data.dat

*****************************************************************************
III. Comments

  - DataView is currently not on a domain or server, as that is a bit
    complicated for current purposes

*****************************************************************************
