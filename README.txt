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
        > flow rate of the cooling water of the He compressor outside building
        > temperature of the He compressor
        > temperature and humidity of the lab room
        > amount of nitrogen left in the nitrogen trap

  - send email warnings when readings are not in desired range

  - monitor instruments from the office room while the DR is operating,
    without having to go to the lab room

*****************************************************************************
II. Program Descriptions

  - cryo-RealTime.py
        > gets data from the Lake Shore 372 (LS372) device, records to
           cryo-LS372-Temp.dat, and plots in real time
        > two types of plots are available: 'static' graph (x-axis is not
          fixed length, so accommodates more and more data with time) and
          'shifting' graph (x-axis is fixed length so plot moves to always
          show most recent data; how recent is user-decided)

  - cryo-DataView.html
        > website to view all data read by the programs
        > refreshes at user-decided frequency
        > currently, data table with temperature readings from LS372 is only
          displayed in Firefox, independent on operating system
        > no images are supposed to be displayed on the website (except for
          the two images from hardcoded URLS); they are just placeholders
          at this point

  - cryo-LS372-Temp.dat
        > text file containing temperature readings of all 8 channels of the
          LS372 and time of measurement, over a period of time and frequency
          set in cryo-RealTime.py
        > cryo-RealTime.py writes to this file
        > cryo-DataView.html reads this file to display on the website

  - cryo-Environment-Data.dat
        > text file containing data from the environment around the cryostat
        > stores the values in the following order (please do not change):
              * coolWaterFR (cooling water flow rate, L/min)
              * coolWaterFR_Low (lower limit of coolWaterFR, L/min)
              * coolWaterFR_Up (upper limit of coolWaterFR, L/min)
              * tempHeComp (temp. of He compressor, K)
              * tempHeComp_Low (lower temp. limit of tempHeComp, K)
              * tempHeComp_Up (upper temp. limit of tempHeComp, K)
              * tempLab (temp. of lab room with cryostat, K)
              * tempLab_Low (lower temp. limit of tempLab, K)
              * tempLab_Up (lower temp. limit of tempLab, K)
              * humLab (humidity of lab room with cryostat, %)
              * humLab_Low (lower hum. limit of humLab, %)
              * humLab_Up (upper hum. limit of humLab, %)
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

*****************************************************************************
III. Comments

  - dataView will most likely not be on a domain or server, as that is a bit
    complicated for current purposes

*****************************************************************************
