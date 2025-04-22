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
        str_err = f" ** Error: expecting 5 arguments: \n ** YYYYMMDDHH resolution n_ens directory_tiles directory_vector"
        sys.exit(str_err)

datestring   = sys.argv[1]
res          = sys.argv[2]
n_ens        = int(sys.argv[3])
tile_dir     = sys.argv[4] 
vector_dir   = sys.argv[5]

print_high_snow_removal = True
print_low_snow_removal = False

##############################
# read in spun-up variables on vector
vec_date = f"{datestring[:4]}-{datestring[4:6]}-{datestring[6:8]}_{datestring[8:10]}"
vector_file = vector_dir+"ufs_land_restart."+vec_date+"-00-00.nc"

ncid = Dataset(vector_file, 'r')

vec_smc = ncid.variables['soil_moisture_vol'][0, :, :]
vec_slc = ncid.variables['soil_liquid_vol'][0, :, :]
vec_stc = ncid.variables['temperature_soil'][0, :, :]
vec_snd = ncid.variables['snow_depth'][0, :]
vec_swe = ncid.variables['snow_water_equiv'][0, :]

ncid.close()

num_in_vector = len(vec_stc[0, :])
print(f"Num in vector: {num_in_vector}")

##############################
# Loop over tile files

for n in range(0,n_ens):

    print(f"Starting ensemble: {n+1}")
    nloc = -1
    high_snow_removal = 0
    low_snow_removal = 0

    for itile in range(1, 7):
        #print(f"Starting tile: {itile}")

        if (n_ens==1): # control
                tile_file = tile_dir+"sfc_data.tile"+str(itile)+".nc"
        else:
                tile_file = tile_dir+"mem"+str(n+1).zfill(3)+"/sfc_data.tile"+str(itile)+".nc"

        ncid_tile = Dataset(tile_file, 'r+')

        tile_veg = ncid_tile.variables['vtype'][0, :, :]
        tile_smc = ncid_tile.variables['smc'][:]
        tile_slc = ncid_tile.variables['slc'][:]
        tile_stc = ncid_tile.variables['stc'][:]
        tile_swe = ncid_tile.variables['weasdl'][:]
        tile_snd = ncid_tile.variables['snodl'][:]

        ndims = tile_veg.shape

        # read in the ensemble mean
        if (n_ens>1):

            ensmean_file = tile_dir+"ensmean_chgres/sfc_data.tile"+str(itile)+".nc"
            ncid = Dataset(ensmean_file)

            # pert = ensemble value - mean
            pert_slc = tile_slc - ncid.variables['slc'][:]
            pert_stc = tile_stc - ncid.variables['stc'][:]
            pert_swe = tile_swe - ncid.variables['weasdl'][:]
            pert_snd = tile_snd - ncid.variables['snodl'][:]

        else:

            pert_slc = np.full(np.shape(tile_slc),0.0)
            pert_stc = np.full(np.shape(tile_stc),0.0)
            pert_swe = np.full(np.shape(tile_swe),0.0)
            pert_snd = np.full(np.shape(tile_snd),0.0)

        for idim0 in range(ndims[0]):
            for idim1 in range(ndims[1]):
                if tile_veg[idim0, idim1] != 0:
                    nloc += 1

                    ################################
                    # insert vector values plus ensembel pert
                    tile_stc[0, :, idim0, idim1] = vec_stc[:, nloc] + pert_stc[0, :, idim0, idim1]

                    # note: applying slc pert to slc and smc (frozen soil moisture same for all members)
                    # note: potentially allowing soil moisture above porosity. I think the model fixes this.

                    for l in np.arange(4):
                        tile_smc[0, l, idim0, idim1] = max(smc_min, vec_smc[l, nloc] + pert_slc[0, l, idim0, idim1])
                        tile_slc[0, l, idim0, idim1] = max(smc_min, vec_slc[l, nloc] + pert_slc[0, l, idim0, idim1])

                    tile_swe[0, idim0, idim1] = max(0.0, vec_swe[nloc] + pert_swe[0,idim0,idim1])
                    tile_snd[0, idim0, idim1] = max(0.0, vec_snd[nloc] + pert_snd[0,idim0,idim1])

                    #################################
                    # santity checks

                    # if spinup had little snow, set all members to no snow.
                    if (0.0 < vec_snd[nloc] < 1.0) or (0.0 < vec_swe[nloc] < 0.01):
                        if print_low_snow_removal:
                            print(f"Removing location with SWE = {tile_swe[0,idim0,idim1]} and depth = {tile_snd[0,idim0,idim1]}")
                        tile_swe[0, idim0, idim1] = 0.
                        tile_snd[0, idim0, idim1] = 0.
                        low_snow_removal += 1

                    # boundary checks
                    if tile_snd[0,idim0,idim1] > 2000.0 and tile_veg[idim0,idim1] == 15: # glaciers
                        reduction_factor = 2000.0 / tile_snd[0,idim0,idim1]
                        if print_high_snow_removal:
                            print(f"Reducing glacier location with depth = {tile_snd[0,idim0,idim1]} by factor = {reduction_factor}")
                        tile_snd[0,idim0,idim1] = 2000.0
                        tile_swe[0,idim0,idim1] *= reduction_factor
                        high_snow_removal += 1

                    if tile_snd[0,idim0,idim1] > 10000.0:
                        reduction_factor = 10000.0 / tile_snd[0,idim0,idim1]
                        if print_high_snow_removal:
                            print(f"Reducing non-glacier location with depth = {tile_snd[0,idim0,idim1]} by factor = {reduction_factor}")
                        tile_snd[0,idim0,idim1] = 10000.0
                        tile_swe[0,idim0,idim1] *= reduction_factor
                        high_snow_removal += 1


        num_in_tiles = nloc + 1

        # Update the NetCDF variables
        ncid_tile.variables['smc'][:] = tile_smc
        ncid_tile.variables['slc'][:] = tile_slc
        ncid_tile.variables['stc'][:] = tile_stc
        ncid_tile.variables['weasdl'][:] = tile_swe
        ncid_tile.variables['snodl'][:] = tile_snd

        ncid.close()

    if num_in_tiles != num_in_vector:
        str_err = f" ** Error: Number in tiles != number in vector"
        sys.exit(str_err)

    print(f"Num high_snow_removal: {high_snow_removal}")
    print(f"Num low_snow_removal: {low_snow_removal}")
    print("Processing completed.")

