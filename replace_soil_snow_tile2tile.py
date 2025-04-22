import os
import sys
import numpy as np
from netCDF4 import Dataset

# minimum allowed smc (and slc) value 
smc_min=0.02


##############################
# get args
if (len(sys.argv) != 6): 
        for i, arg in enumerate(sys.argv):
                print(f"Argument {i}: {arg}")
        string = f" ** Error: expecting 5 arguments: \n ** YYYYMMDDHH resolution n_ens directory_source directory_target"
        sys.exit(string)

datestring   = sys.argv[1]
res          = sys.argv[2]
n_ens        = int(sys.argv[3])
source_dir   = sys.argv[4] 
target_dir   = sys.argv[5]

print_high_snow_removal = True
print_low_snow_removal = False

##############################
# Loop over tile files

for n in range(0,n_ens):

    print(f"Starting ensemble: {n+1}")
    high_snow_removal = 0
    low_snow_removal = 0
    source_nloc = 0
    target_nloc = 0

    for itile in range(1, 7):
        #print(f"Starting tile: {itile}")

        if (n_ens==1): # control
                source_file = source_dir+"/sfc_data.tile"+str(itile)+".nc"
        else:
                source_file = source_dir+"/mem"+str(n+1).zfill(3)+"/sfc_data.tile"+str(itile)+".nc"
        str_date = f"{datestring[:8]}.{datestring[8:10]}"
        target_file = target_dir+"/mem"+str(n+1).zfill(3)+"/"+str_date+"0000.sfc_data.tile"+str(itile)+".nc"

        source_tile = Dataset(source_file, 'r')
        target_tile = Dataset(target_file, 'r+')

        source_veg = source_tile.variables['vtype'][0, :, :]
        source_smc = source_tile.variables['smc'][:]
        source_slc = source_tile.variables['slc'][:]
        source_stc = source_tile.variables['stc'][:]
        source_swe = source_tile.variables['sheleg'][:]
        source_snd = source_tile.variables['snwdph'][:]

        target_veg = target_tile.variables['vtype'][0, :, :]
        target_smc = target_tile.variables['smc'][:]
        target_slc = target_tile.variables['slc'][:]
        target_stc = target_tile.variables['stc'][:]
        target_swe = target_tile.variables['sheleg'][:]
        target_snd = target_tile.variables['snwdph'][:]

        source_ndims = source_veg.shape
        ndims = target_veg.shape
        if ndims[0] != source_ndims[0] or ndims[1] != source_ndims[1]:
            string = f" ** Error: resolution for source and target tiles does not match"
            sys.exit(string)

        # read in the ensemble mean
        if (n_ens>1):

            ensmean_file = source_dir+"/ensmean_chgres/sfc_data.tile"+str(itile)+".nc"
            ncid = Dataset(ensmean_file)

            # pert = ensemble value - mean
            pert_slc = source_slc - ncid.variables['slc'][:]
            pert_stc = source_stc - ncid.variables['stc'][:]
            pert_swe = source_swe - ncid.variables['sheleg'][:]
            pert_snd = source_snd - ncid.variables['snwdph'][:]

        else:

            pert_slc = np.full(np.shape(source_slc),0.0)
            pert_stc = np.full(np.shape(source_stc),0.0)
            pert_swe = np.full(np.shape(source_swe),0.0)
            pert_snd = np.full(np.shape(source_snd),0.0)

        for idim0 in range(ndims[0]):
            for idim1 in range(ndims[1]):
                if source_veg[idim0, idim1] != 0:
                    source_nloc += 1
                if target_veg[idim0, idim1] != 0:
                    target_nloc += 1

                    ################################
                    # insert vector values plus ensembel pert
                    target_stc[0, :, idim0, idim1] = target_stc[0, :, idim0, idim1] + pert_stc[0, :, idim0, idim1]

                    # note: applying slc pert to slc and smc (frozen soil moisture same for all members)
                    # note: potentially allowing soil moisture above porosity. I think the model fixes this.

                    for l in np.arange(4):
                        target_smc[0, l, idim0, idim1] = max(smc_min, target_smc[0, l, idim0, idim1] + pert_slc[0, l, idim0, idim1])
                        target_slc[0, l, idim0, idim1] = max(smc_min, target_slc[0, l, idim0, idim1] + pert_slc[0, l, idim0, idim1])

                    target_swe[0, idim0, idim1] = max(0.0, target_swe[0, idim0, idim1] + pert_swe[0,idim0,idim1])
                    target_snd[0, idim0, idim1] = max(0.0, target_snd[0, idim0, idim1] + pert_snd[0,idim0,idim1])

                    #################################
                    # santity checks

                    # if perturbed fields show little snow, set it to no snow.
                    if (0.0 < target_snd[0, idim0, idim1] < 1.0) or (0.0 < target_swe[0, idim0, idim1] < 0.01):
                        if print_low_snow_removal:
                            print(f"Removing location with SWE = {target_swe[0,idim0,idim1]} and depth = {target_snd[0,idim0,idim1]}")
                        target_swe[0, idim0, idim1] = 0.
                        target_snd[0, idim0, idim1] = 0.
                        low_snow_removal += 1

                    # boundary checks
                    if target_snd[0,idim0,idim1] > 2000.0 and target_veg[idim0,idim1] == 15: # glaciers
                        reduction_factor = 2000.0 / target_snd[0,idim0,idim1]
                        if print_high_snow_removal:
                            print(f"Reducing glacier location with depth = {target_snd[0,idim0,idim1]} by factor = {reduction_factor}")
                        target_snd[0,idim0,idim1] = 2000.0
                        target_swe[0,idim0,idim1] *= reduction_factor
                        high_snow_removal += 1

                    if target_snd[0,idim0,idim1] > 10000.0:
                        reduction_factor = 10000.0 / target_snd[0,idim0,idim1]
                        if print_high_snow_removal:
                            print(f"Reducing non-glacier location with depth = {target_snd[0,idim0,idim1]} by factor = {reduction_factor}")
                        target_snd[0,idim0,idim1] = 10000.0
                        target_swe[0,idim0,idim1] *= reduction_factor
                        high_snow_removal += 1

        # Update the NetCDF variables
        target_tile.variables['smc'][:] = target_smc
        target_tile.variables['slc'][:] = target_slc
        target_tile.variables['stc'][:] = target_stc
        target_tile.variables['sheleg'][:] = target_swe
        target_tile.variables['snwdph'][:] = target_snd

        if (n_ens>1):
          ncid.close()
        source_tile.close()
        target_tile.close()

    if source_nloc != target_nloc:
        string = f" ** Error: land points in source tiles != land points in target tiles"
        #sys.exit(string)

    print(f"Num high_snow_removal: {high_snow_removal}")
    print(f"Num low_snow_removal: {low_snow_removal}")
    print("Processing completed.")
