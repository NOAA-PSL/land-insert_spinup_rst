# inserting spun-up (vector) restrarts.
# Clara Draper.
# Invoke as: sh $script
# requires module load cdo
#-----------------------------------------------------------

source config_restarts

# create clean directories

do_control="YES"
do_ensemble="NO"

if [ $do_control == "YES" ]; then

    new_dir=$DIRTILE/C${RES_CTL}/gdas.${YYYYMMDD}/${HH}/model/atmos/input/
    if [ -d $new_dir ]; then 
            rm -rf $new_dir
    fi
    mkdir -p $new_dir

    # copy restarts from change-res
    cp $CHNGRESDIR/C${RES_CTL}/${VALID_DATE}/*nc  $new_dir/

    # CSD - to do, copy gdas files
    mkdir -p $DIRTILE/C${RES_CTL}/gdas.${YYYYMMDD}/${HH}/analysis/atmos
    cp $CHNGRESDIR/inputs/C${RES_CTL}/${VALID_DATE}/gdas*abias* $DIRTILE/C${RES_CTL}/gdas.${YYYYMMDD}/${HH}/analysis/atmos
fi

if [ $do_ensemble == "YES" ]; then

    new_dir=$DIRTILE/C${RES_ENS}/enkfgdas.${YYYYMMDD}/${HH}
    if [ -d $new_dir ]; then 
            rm -rf $new_dir
    fi
    mkdir -p $new_dir

    # copy restarts from change-res
    n=1
    while [ $n -le 80 ]; do
     charnanal="mem`printf %03i $n`"
      # copy restarts from change-res
      mkdir -p ${new_dir}/${charnanal}/model/atmos/
      cp -r $CHNGRESDIR/C${RES_ENS}/${VALID_DATE}/${charnanal} ${new_dir}/${charnanal}/model/atmos/input

      n=$((n+1))
    done

    # calculate the ensemble mean

    mkdir -p ${new_dir}/ensmean_chgres
    for n in 1 2 3 4 5 6 
    do 
    cdo ensmean ${new_dir}/mem*/model/atmos/input/sfc_data.tile${n}.nc \
                        ${new_dir}/ensmean_chgres/sfc_data.tile${n}.nc

    done

fi
