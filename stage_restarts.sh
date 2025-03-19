# inserting spun-up (vector) restrarts.
# Clara Draper.
# Invoke as: sh $script
# requires module load cdo
#-----------------------------------------------------------

source config_restarts

# create clean directories

do_control="NO"
do_ensemble="YES"

if [ $do_control == "YES" ]; then

    new_dir=$DIRTILE/C${RES_CTL}/${VALID_DATE}
    if [ -d $new_dir ]; then 
            rm -rf $new_dir
    fi
    mkdir -p $new_dir

    # copy restarts from change-res
    cp $DIROUT/C${RES_CTL}/${VALID_DATE}/*  $DIRTILE/C${RES_CTL}/${VALID_DATE}/
fi

if [ $do_ensemble == "YES" ]; then

    new_dir=$DIRTILE/C${RES_ENS}/${VALID_DATE} 
    if [ -d $new_dir ]; then 
            rm -rf $new_dir
    fi
    mkdir -p $new_dir

    # copy restarts from change-res
    cp -r  $DIROUT/C${RES_ENS}/${VALID_DATE}/mem*  $DIRTILE/C${RES_ENS}/${VALID_DATE}/

    # calculate the ensemble mean

    mkdir -p $DIRTILE/C${RES_ENS}/${VALID_DATE}/ensmean
    for n in 1 2 3 4 5 6 
    do 
    cdo ensmean $DIRTILE/C${RES_ENS}/${VALID_DATE}/mem*/sfc_data.tile${n}.nc \
                        $DIRTILE/C${RES_ENS}/${VALID_DATE}/ensmean/sfc_data.tile${n}.nc

    done

fi
