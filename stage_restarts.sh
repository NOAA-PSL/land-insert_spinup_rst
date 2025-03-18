# inserting spun-up (vector) restrarts.
# Clara Draper.
# Invoke as: sh $script
#-----------------------------------------------------------

source config_restarts

# create clean directories

for new_dir in $DIRTILE/C${RES_ENS}/${VALID_DATE} $DIRTILE/C${RES_CTL}/${VALID_DATE}
do
    if [ -d $new_dir ]; then 
            rm -rf $new_dir
    fi
    mkdir -p $new_dir
done

# copy restarts from change-res
cp -r  $DIROUT/C${RES_ENS}/${VALID_DATE}/mem*  $DIRTILE/C${RES_ENS}/${VALID_DATE}/
cp $DIROUT/C${RES_CTL}/${VALID_DATE}/*  $DIRTILE/C${RES_CTL}/${VALID_DATE}/

# calculate the ensemble mean
