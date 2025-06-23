#!/bin/bash

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

export HOMEufs=${UFS_UTILS}
export FIXufs=${HOMEufs}/fix/
# for the output
export FIXfv3=${FIXufs}/orog/C${CRES}/ # must be same as g-w!
export FIXsfc=${FIXfv3}/sfc/

set -x

export ocn=025
export VCOORD_FILE=${HOMEufs}/fix/am/global_hyblev.l128.txt
export INPUT_TYPE='restart'
export MOSAIC_FILE_INPUT_GRID="${INPUT_OROG}/C${CRES_IN}_mosaic.nc"
export OROG_DIR_INPUT_GRID=${INPUT_OROG}

# Note: no double quotes at the beginning or end.
export OROG_FILES_INPUT_GRID='C'${CRES_IN}'_oro_data.tile1.nc", "C'${CRES_IN}'_oro_data.tile2.nc","C'${CRES_IN}'_oro_data.tile3.nc","C'${CRES_IN}'_oro_data.tile4.nc","C'${CRES_IN}'_oro_data.tile5.nc","C'${CRES_IN}'_oro_data.tile6.nc'

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
