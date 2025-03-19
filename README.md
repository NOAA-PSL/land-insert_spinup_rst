Collection of scripts to generate land restarts for GFS/GDAS ensemble 
experiments.

Instructions: 
Set desired dates, resolutions, and directories in config_restarts 

1. Extract (operational) restarts from archives.

>sh get_restarts.sh

2. Change to desired resolution 

>sbatch chgres_restarts.sh

3. Copy the output of chgres, and calculate the ensemble mean

>module load cdo
>sh stage_restarts.sh

4. Insert the spun-up vector states into the control and ensemble 

>sh insert_control.sh 
>sh insert_ensemble.sh

will need python
