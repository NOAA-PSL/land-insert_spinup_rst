
Insert a spun-up (vector) land restart into cold start tile files. 
Also applies the ensemble pertubations from the operational ensemble into the ensemble of tile files. 

Inserts, soil moisture (total and liquid), soil temperature, snow depth (and SWE), and snow water equivalent from the spin up.
Inserts pertubations in soil moisture and soil temperature. 

To-do: think some more about snow temperature.
     : parallelize the python calls.

Clara Draper, March 2025: using insert script from Mike Barlage, and Helin Wei.

===================================

Instructions: 

1. Extract (operational) restarts from archives, and re-grid using UFS_UTILS/util/gdas_init 

In config file: 
* may need to change PROJECT_CODE in driver.$MACHINE.sh
* in set_fixed_files.sh check that OCNRES is set correctly for chosen resolutions
* set details in config, including: 
    LEVS=128
    CDUMP=gdas
 
2. Either copy config file from UFS_UTILS/util/gdas_init into this directory, or fill in the existing config file.

3. Copy the spun-up vector restarts valid at the time in the config file into $DIRTILE/spin_vec/C${RES}/

3. Insert the spun-up vectors. 
>insert_spinup.sh





