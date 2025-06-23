Collection of scripts to generate land restarts for GFS/GDAS ensemble 
experiments.

Inserts a spun-up (vector) land restart into the cold start tile files. 
Inserts, soil moisture (total and liquid), soil temperature, snow depth, 
and snow water equivalent. 

To-do: think some more about snow temperature.

Clara Draper, March 2025: using insert script from Mike Barlage, and Helin Wei.

===================================

Instructions: 

1. Set desired dates, resolutions, and directories in config_restarts 

IF NEED TO EXTRACT FILES FROM THE ARCHIVE:
    2. Extract (operational) restarts from archives.

    >module load hpss
    >sbatch get_restarts.sh

    3. Change to desired resolution 

    >sbatch sub_do_changeres.sh

4. Copy the spun-up vector files into ./spin_vec/$RES\_[ENS/CTL]/

5. Copy the output of chgres into new directories, and calculate the ensemble mean

>module load cdo
>sh stage_restarts.sh

6. Insert the spun-up vector states into the control and ensemble 

>source env_python
>sh insert_control.sh 
>sh insert_ensemble.sh

OUTPUT: The sfc_data files with the spun-values inserted are in ./spin_tile

./chgres and ./spin_tile/$RES_ENS/$date/ensmean_chgres can be deleted.



