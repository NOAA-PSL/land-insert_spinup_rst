#!/bin/bash
#-----------------------------------------------------------
# Script to extract ICS from the arhives.
# Clara Draper, based on Jeff Whitaker's script.
# Invoke as: sh $script
#-----------------------------------------------------------

source config_restarts

module load hpss
module list

mkdir -p $WORKDIR
mkdir -p $DIROUT/C${RES_ENS}/${datep3}
mkdir -p $DIROUT/C${RES_CTL}/${datep3}
mkdir -p $DIROUT/C${RES_ENS_IN}/${datep3}
mkdir -p $DIROUT/C${RES_CTL_IN}/${datep3}


datestring="${YYYYMMDDp3}.${HHp3}0000."
echo $datestring

hpsspath=/NCEPPROD/hpssprod/runhistory/rh${YYYY}/${YYYYMM}/${YYYYMMDD}

 cd $WORKDIR

# get control

htar -xvf $hpsspath/com_gfs_${arch_tag}_gdas.${YYYYMMDD}_${HH}.gdas_restart.tar

# copy required files

OUTDIR=$DIROUT/C${RES_CTL}/${datep3}
/bin/cp -f gdas.${YYYYMMDD}/${HH}/atmos/gdas.t${HH}z.abias $OUTDIR/gdas.t${HHp3}z.abias
/bin/cp -f gdas.${YYYYMMDD}/${HH}/atmos/gdas.t${HH}z.abias_pc $OUTDIR/gdas.t${HHp3}z.abias_pc
/bin/cp -f gdas.${YYYYMMDD}/${HH}/atmos/gdas.t${HH}z.abias_air $OUTDIR/gdas.t${HHp3}z.abias_air
/bin/cp -f gdas.${YYYYMMDD}/${HH}/atmos/gdas.t${HH}z.abias_int $OUTDIR/gdas.t${HHp3}z.abias_int

pushd gdas.${YYYYMMDD}/${HH}/atmos/RESTART
datestring="${YYYYMMDDp3}.${HHp3}0000."
mkdir $OUTDIR/control
for file in ${datestring}*nc; do
  file2=`echo $file | cut -f3-10 -d"."`
  /bin/cp -f $file $OUTDIR/control/$file2
done
popd 
ls -l $OUTDIR/control
/bin/rm -rf gdas.${YYYYMMDD}

# get ens restarts
ngrp=1
#ngrps=8 
ngrps=1 # CSD -testing
while [ $ngrp -le $ngrps ]; do
  htar -xvf $hpsspath/com_gfs_${arch_tag}_enkfgdas.${YYYYMMDD}_${HH}.enkfgdas_restart_grp${ngrp}.tar
  ngrpm1=$((ngrp-1))
  n=1
  while [ $n -le 10 ]; do
     nanal=`expr $ngrpm1 \* 10 + $n`
     charnanal="mem`printf %03i $nanal`"
     pushd enkfgdas.${YYYYMMDD}/${HH}/atmos/${charnanal}/RESTART
     n=$((n+1))
     OUTDIR=$DIROUT/C${RES_ENS_IN}/${datep3}/${charnanal}
     mkdir $OUTDIR
     for file in ${datestring}*nc; do
        file2=`echo $file | cut -f3-10 -d"."`
        /bin/cp -f $file $OUTDIR/$file2
     done
     popd
     ls -l $OUTDIR
  done
  ngrp=$((ngrp+1))
done
/bin/rm -rf enkfgdas.${YYYYMMDD}
