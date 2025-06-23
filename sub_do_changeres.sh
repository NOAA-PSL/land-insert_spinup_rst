#!/bin/bash
#-----------------------------------------------------------
# Script to extract regrid ICS extracted from archives
# Clara Draper, based on reg_test in UFS_UTILS
# Invoke as: sbatch $script
#-----------------------------------------------------------

#SBATCH --ntasks-per-node=6 
#SBATCH --nodes=1
#SBATCH -t 2:00:00
#SBATCH -A gsienkf
#SBATCH -q batch
#SBATCH -J cube_to_cube
#SBATCH -o cube_to_cube.out
#SBATCH -e cube_to_cube.out

# read in settings

source config_restarts



##############################################
# set up environment 
##############################################

source "${UFS_UTILS}/sorc/machine-setup.sh"

compiler=${compiler:-"intelllvm"}

module use ${UFS_UTILS}/modulefiles
if [[ "$compiler" == "intelllvm" ]]; then
if [[ ! -f ${UFS_UTILS}/modulefiles/build.$target.$compiler.lua ]];then
  echo "IntelLLVM not available. Will use Intel Classic."
  compiler=intel
fi
fi

module load build.${target}.${compiler}
module list

export OMP_NUM_THREADS=1
export OMP_STACKSIZE=2048M
export APRUN=srun

export UFS_UTILS
export CYCL_DATE

#############################################
# control

export CRES=${RES_CTL} # RES_OUT
export CRES_IN=${RES_CTL_IN} # RES_IN

export COMIN=${CHNGRESDIR}/C${CRES_IN}/${VALID_DATE}/control/ # input
export DATA=${CHNGRESDIR}/C${CRES}/ #output
rm -fr $DATA

${HERE}/do_changeres.sh


#############################################
# ensembles

export CRES=${RES_ENS} # RES_OUT
export CRES_IN=${RES_ENS_IN} # RES_IN
nanal=1
while [ $nanal -le $nanals ]; do
    charnanal="mem`printf %03i $nanal`"
    echo "charnanal=$charnanal"


    export DATA=${CHNGRESDIR}/C${CRES}/${charnanal}/ #output
    export COMIN=${CHNGRESDIR}/C${CRES_IN}/${VALID_DATE}/${charnanal}/ # input
    rm -fr $DATA

    ${HERE}/do_changeres.sh

    nanal=$((nanal+1))
done

exit 0
