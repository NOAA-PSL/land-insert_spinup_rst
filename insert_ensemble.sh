#!/bin/bash
#-----------------------------------------------------------
# Script to stage regridded restarts, ready for
# inserting spun-up (vector) restrarts.
# Clara Draper.
# Invoke as: sh $script
#-----------------------------------------------------------

source config_restarts

#example python on hera that has required packages:
#module use -a /contrib/anaconda/modulefiles/
#module load gnu
#module load intel/2023.2.0
#module load anaconda/latest
#python=/contrib/anaconda/anaconda3/latest/bin/python # hera!

python  replace_soil_snow.py ${VALID_DATE} ${RES_ENS} ${nanals} $DIRTILE/C${RES_CTL}/enkfgdas.${YYYYMMDD}/${HH}/ ${DIRVEC}/C${RES_ENS}/







