#!/bin/bash
#-----------------------------------------------------------
# Script to extract regrid ICS extracted from archives
# Clara Draper, based on Jeff Whitaker's script.
# Invoke as: sbatch $script
#-----------------------------------------------------------

#SBATCH --ntasks-per-node=6 --nodes=4
#SBATCH -t 4:00:00
##SBATCH -t 0:30:00
#SBATCH -A gsienkf
##SBATCH -q debug
#SBATCH -J cube_to_cube
#SBATCH -o cube_to_cube.out
#SBATCH -e cube_to_cube.out

source config_restarts

##############################################

SLURM_SUBMIT_DIR=$PWD

module use ${UFS_UTILS}/modulefiles
module load build.hera.intel
module list

CHGRES_EXEC=${UFS_UTILS}/exec/chgres_cube

export OMP_NUM_THREADS=6
export OMP_STACKSIZE=2048M

datestring="${YYYYMMDDp3}.${HHp3}0000."
echo $datestring

cd $CHNGRESDIR

sed "s/<RES>/${RES_CTL}/g; s/<LEVSP1>/${LEVSP1}/g; s/<member>/control/g; s/<YYYYMMDD>/${YYYYMMDDp3}/g; s/<MM>/${MMp3}/g; s/<DD>/${DDp3}/g; s/<HH>/${HHp3}/g; s|<CHNGRESDIR>|${CHNGRESDIR}|g"  ${SLURM_SUBMIT_DIR}/config_control.nml.template > ./fort.41
cat fort.41

echo "srun $CHGRES_EXEC"

srun $CHGRES_EXEC

OUTDIR=$CHNGRESDIR/C${RES_CTL}/${VALID_DATE}
ls -l
/bin/mv -f gfs_ctrl.nc $OUTDIR
tiles="tile1 tile2 tile3 tile4 tile5 tile6"
for tile in $tiles; do
  /bin/mv -f out.atm.${tile}.nc $OUTDIR/gfs_data.${tile}.nc
  /bin/mv -f out.sfc.${tile}.nc $OUTDIR/sfc_data.${tile}.nc
done

nanal=1
while [ $nanal -le $nanals ]; do
    charnanal="mem`printf %03i $nanal`"
    echo "charnanal=$charnanal"

    sed "s/<RES>/${RES_ENS}/g; s/<LEVSP1>/${LEVSP1}/g; s/<member>/${charnanal}/g; s/<YYYYMMDD>/${YYYYMMDDp3}/g; s/<MM>/${MMp3}/g; s/<DD>/${DDp3}/g; s/<HH>/${HHp3}/g; s|<CHNGRESDIR>|${CHNGRESDIR}|g"  ${SLURM_SUBMIT_DIR}/config_ens.nml.template > ./fort.41
    cat fort.41

    echo "srun $CHGRES_EXEC"
    srun $CHGRES_EXEC

    OUTDIR=${CHNGRESDIR}/C${RES_ENS}/${VALID_DATE}/${charnanal}
    /bin/rm -rf $OUTDIR
    mkdir -p $OUTDIR

    ls -l
    /bin/mv -f gfs_ctrl.nc $OUTDIR
    tiles="tile1 tile2 tile3 tile4 tile5 tile6"
    for tile in $tiles; do
      /bin/mv -f out.atm.${tile}.nc $OUTDIR/gfs_data.${tile}.nc
      /bin/mv -f out.sfc.${tile}.nc $OUTDIR/sfc_data.${tile}.nc
    done

    nanal=$((nanal+1))
done

exit 0
