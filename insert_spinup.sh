#!/bin/bash
#
# inserting spun-up (vector) restrarts.
# Clara Draper.
#-----------------------------------------------------------

do_control="YES"
do_ensemble="YES"

source env_python # hera only
module load cdo

source config

DIRTILE=$OUTDIR

#### 

DIRVEC=$DIRTILE/spin_vec/ # spun-up land restarts on vector

#################
# CONTROL 
#################

# insert control

if [ $do_control == "YES" ]; then
   python  replace_soil_snow.py ${yy}${mm}${dd}${hh} 1 $DIRTILE/gdas.${yy}${mm}${dd}/${hh}/  ${DIRVEC}/${CRES_HIRES}/
fi

#################
# ENSEMBLE
#################

# calculate the means

if [ $do_ensemble == "YES" ]; then

    ens_dir=$DIRTILE/enkfgdas.${yy}${mm}${dd}/${hh}
    mkdir -p ${ens_dir}/ensmean_chgres
    for n in 1 2 3 4 5 6 
    do 
    cdo ensmean ${ens_dir}/mem*/model/atmos/input/sfc_data.tile${n}.nc \
                        ${ens_dir}/ensmean_chgres/sfc_data.tile${n}.nc

    done

    # insert ensemble
    nanals=80
    python  replace_soil_snow.py ${yy}${mm}${dd}${hh} ${nanals} $DIRTILE/enkfgdas.${yy}${mm}${dd}/${hh}/ ${DIRVEC}/${CRES_ENKF}/

fi
