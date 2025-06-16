#!/bin/bash
#-----------------------------------------------------------
# Script to extract regrid ICS extracted from archives
# Clara Draper, based on reg_test in UFS_UTILS
# Invoke as: sbatch $script
#-----------------------------------------------------------

#SBATCH --ntasks-per-node=6 
#SBATCH --nodes=1
#SBATCH -t 0:15:00
#SBATCH -A gsienkf
#SBATCH -q debug
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

#############################################
# set variables required by ush script 
#############################################

# Set up environment paths needed by ush/chgres_cube.sh
#
# HOMEufs - Location of root ufs_utils directory.
# EXECufs - Location of ufs_utils executable directory.
# FIXufs  - Location of ufs_utils root fixed data directory.
# FIXfv3  - Location of target grid orography and 'grid' files.
# FIXsfc  - Location of target grid surface climatological files.
# FIXam   - Location of vertical coordinate definition file for target grid.

export APRUN=srun
export CRES=${RES_CTL}

export HOMEufs=${UFS_UTILS}
export FIXufs=${HOMEufs}/fix/
# for the output
export FIXfv3=${FIXufs}/orog/C${CRES}/ # must be same as g-w!
export FIXsfc=${FIXfv3}/sfc/

set -x

export DATA=${CHNGRESDIR}/C${RES_CTL}/
rm -fr $DATA

export ocn=025
export COMIN=${CHNGRESDIR}/C${RES_CTL_IN}/${VALID_DATE}/control/
export VCOORD_FILE=${HOMEufs}/fix/am/global_hyblev.l64.txt
export INPUT_TYPE='restart'
export INPUT_OROG="/scratch1/NCEPDEV/global/glopara/fix/orog/20230615/C${RES_CTL_IN}/"
export MOSAIC_FILE_INPUT_GRID="${INPUT_OROG}/C${RES_CTL_IN}_mosaic.nc"
export OROG_DIR_INPUT_GRID=${INPUT_OROG}

# Note: no double quotes at the beginning or end.
export OROG_FILES_INPUT_GRID='C'${RES_CTL_IN}'_oro_data.tile1.nc", "C'${RES_CTL_IN}'_oro_data.tile2.nc","C'${RES_CTL_IN}'_oro_data.tile3.nc","C'${RES_CTL_IN}'_oro_data.tile4.nc","C'${RES_CTL_IN}'_oro_data.tile5.nc","C'${RES_CTL_IN}'_oro_data.tile6.nc'

export ATM_CORE_FILES_INPUT='fv_core.res.tile1.nc","fv_core.res.tile2.nc","fv_core.res.tile3.nc","fv_core.res.tile4.nc","fv_core.res.tile5.nc","fv_core.res.tile6.nc","fv_core.res.nc'
export ATM_TRACER_FILES_INPUT='fv_tracer.res.tile1.nc","fv_tracer.res.tile2.nc","fv_tracer.res.tile3.nc","fv_tracer.res.tile4.nc","fv_tracer.res.tile5.nc","fv_tracer.res.tile6.nc'
export SFC_FILES_INPUT='sfc_data.tile1.nc","sfc_data.tile2.nc","sfc_data.tile3.nc","sfc_data.tile4.nc","sfc_data.tile5.nc","sfc_data.tile6.nc'

export TRACERS_TARGET='"sphum","liq_wat","o3mr","ice_wat","rainwat","snowwat","graupel"'
export TRACERS_INPUT='"sphum","liq_wat","o3mr","ice_wat","rainwat","snowwat","graupel"'

export CDATE=$CYCL_DATE

#-----------------------------------------------------------------------------
# Invoke chgres program.
#-----------------------------------------------------------------------------

echo "Starting at: " `date`

${HOMEufs}/ush/chgres_cube.sh

exit 0
