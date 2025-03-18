Collection of scripts to generate land restarts for GFS/GDAS ensemble 
experiments.

Instructions: 
Set desired dates, resolutions, and directories in config_restarts 

1. Extract (operational) restarts from archives.

>sh get_restarts.sh

2. Change to desired resolution 

>sbatch chgres_restarts.sh

3. Insert
