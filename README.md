# SpaceWeather

This code calculates the average proton/alpha particle flux for a given date/time interval. It is calculated using data extracted directly the freely available SWPC / NOAA (Space Weather Prediction Center / National Oceanic And Atmospheric Administration) geostationary satellite dataset. More details on the GOES satellite instrumentation and data acquisition can be found [here](http://www.swpc.noaa.gov/products/goes-proton-flux).


## Data sample

The data is directly extracted from the following directory of the data base:

    http://satdat.ngdc.noaa.gov/sem/goes/data/new_avg

which contains data from 1986 until the present day. Specifically, the data file (csv) describe the 5-minute averaged integral proton flux as measured by the SWPC primary GOES satellite for energy thresholds of >=10, >=50, and >=100 MeV. An extensive description of the jargon used in the data files is provided [here](http://www.ngdc.noaa.gov/stp/satellite/goes/index.html).


## Usage

The user should provide an input csv file "runTimes.csv" (see example *runTimes.csv*) containing pairs of date/time strings in the form: *start time*,*end time*. The user can then specify the following parameters (see example *SpaceWeather.py*) which are currently hard-coded to:

    satellites = ["g13","g15"]

where the list items `"g13"` and `"g15"` corresponds to the GOES-13 and GOES-15 satellites respectively, and 

    sample_keyword = {"_hepad_ap_":"_FLUX",
        		      "_epead_p17ew_":"_COR_FLUX"}

where the variable pairs correspond to keywords in the file name (i.e. `"_hepad_ap_"` and `"_epead_p17ew_"`) and data column (i.e. `"_FLUX"` and `"_COR_FLUX"`) respectively, that you wish to extract. For more information on the data column names, please refer to the metadata in files such as:

      http://satdat.ngdc.noaa.gov/sem/goes/data/new_avg/2013/02/goes15/csv/g15_hepad_ap_5m_20130201_20130228.csv

which, as you may note contains the keyword `"_hepad_ap_"` for satellite `"g15"` and data columns containing the keyword `"_FLUX"`.

      http://satdat.ngdc.noaa.gov/sem/goes/data/new_avg/2013/03/goes13/csv/g13_epead_p17ew_5m_20130301_20130331.csv

which, as you may note contains the keyword `"_epead_p17ew_"` for satellite `"g13"` and data columns containing the keyword `"_COR_FLUX"`.
