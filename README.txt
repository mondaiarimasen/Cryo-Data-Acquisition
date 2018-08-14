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

  - cryo-LS372-Temp.dat
        > text file containing temperature readings of all 8 channels of the
          LS372 and time of measurement, over a period of time and frequency
          set in cryo-RealTime.py
        > cryo-RealTime.py writes to this file
        > cryo-DataView.html reads this file to display on the website

*****************************************************************************
III. Comments

  - dataView will most likely not be on a domain or server, as that is a bit
    complicated for current purposes

*****************************************************************************
