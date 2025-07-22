import os
import sys
import numpy as np
from netCDF4 import Dataset

# minimum allowed smc (and slc) value 
smc_min=0.02

print_lims=True # print min / max change for each variable

##############################
# get args
if (len(sys.argv) != 5): 
        for i, arg in enumerate(sys.argv):
                print(f"Argument {i}: {arg}")
        str_err = f" ** Error: expecting 4 arguments: \n ** YYYYMMDDHH n_ens directory_tiles directory_vector"
        sys.exit(str_err)

datestring   = sys.argv[1]
n_ens        = int(sys.argv[2])
tile_dir     = sys.argv[3] 
vector_dir   = sys.argv[4]

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
vec_snd = ncid.variables['snow_depth'][0, :] # mm
vec_swe = ncid.variables['snow_water_equiv'][0, :]

ncid.close()

num_in_vector = len(vec_stc[0, :])
print(f"Num in vector: {num_in_vector}")

##############################
# Loop over tile files

var_list = ['smc','slc','stc','weasdl','snodl']
n_var = len(var_list)

for n in range(0,n_ens):

    print(f"Starting ensemble: {n+1}")
    nloc = -1
    high_snow_removal = 0
    low_snow_removal = 0

    for itile in range(1, 7):
        print(f"Starting tile: {itile}")
        min_val = np.full((n_var,4),0.)
        max_val = np.full((n_var,4),0.)

        if (n_ens==1): # control
                tile_file = tile_dir+"model/atmos/input/sfc_data.tile"+str(itile)+".nc"
        else:
                tile_file = tile_dir+"mem"+str(n+1).zfill(3)+"/model/atmos/input/sfc_data.tile"+str(itile)+".nc"

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
            pert_smc = tile_smc - ncid.variables['smc'][:]
            pert_stc = tile_stc - ncid.variables['stc'][:]

        else:

            pert_smc = np.full(np.shape(tile_smc),0.0)
            pert_stc = np.full(np.shape(tile_stc),0.0)

        for idim0 in range(ndims[0]):
            for idim1 in range(ndims[1]):
                if tile_veg[idim0, idim1] != 0:
                    nloc += 1

                    ################################
                    # insert vector values plus ensemble pert
                    # snow

                    orig = tile_swe[0, idim0, idim1]
                    tile_swe[0, idim0, idim1] = vec_swe[nloc]
                    min_val[3,0] = min(min_val[3,0],tile_swe[0,  idim0, idim1] - orig)
                    max_val[3,0] = max(max_val[3,0],tile_swe[0,  idim0, idim1] - orig)

                    orig = tile_snd[0, idim0, idim1]
                    tile_snd[0, idim0, idim1] = vec_snd[nloc]
                    min_val[4,0] = min(min_val[4,0],tile_snd[0,  idim0, idim1] - orig)
                    max_val[4,0] = max(max_val[4,0],tile_snd[0,  idim0, idim1] - orig)

                    # soil temperatures
                    for l in np.arange(4):
                        orig = tile_stc[0, l, idim0, idim1]
                        tile_stc[0, l, idim0, idim1] = vec_stc[l, nloc] + pert_stc[0, l, idim0, idim1]
                        min_val[2,l] = min(min_val[2,l],tile_stc[0, l, idim0, idim1] - orig)
                        max_val[2,l] = max(max_val[2,l],tile_stc[0, l, idim0, idim1] - orig)


                    if (tile_veg[idim0,idim1] != 15):

                        # don't use soil moisture values under glaciers
                        # note: spun-up vector restarts have slc=0, smc=1 under glaciers
                        #       tile restarts from change_res have slc=1, smc=1

                        # note: applying slc pert to slc and smc (frozen soil moisture same for all members)
                        # note: potentially allowing soil moisture above porosity. I think the model fixes this.
                        for l in np.arange(4):
                            orig = tile_smc[0, l, idim0, idim1]
                            tile_smc[0, l, idim0, idim1] = max(smc_min, vec_smc[l, nloc] + pert_smc[0, l, idim0, idim1])

                            min_val[0,l] = min(min_val[0,l],tile_smc[0, l, idim0, idim1] - orig)
                            max_val[0,l] = max(max_val[0,l],tile_smc[0, l, idim0, idim1] - orig)

                            orig = tile_slc[0, l, idim0, idim1]
                            tile_slc[0, l, idim0, idim1] = max(smc_min, vec_slc[l, nloc])
                            min_val[1,l] = min(min_val[1,l],tile_slc[0, l, idim0, idim1] - orig)
                            max_val[1,l] = max(max_val[1,l],tile_slc[0, l, idim0, idim1] - orig)


                        #  check glacier tiles match
                        if ( tile_smc[0, 0, idim0, idim1] > 0.99 or vec_smc[0,nloc]>0.99):
                            print(f"tile_smc: {tile_smc[0, l, idim0, idim1]}") 
                            print(f"vec_smc: {vec_smc[0,nloc]}") 
                            str_err = f" ** Error:  expecting soil moisture value, got 1."
                            sys.exit(str_err)

                    else: # return error if glacier locations dont' match

                        if ( vec_smc[0,nloc]<1.):
                            str_err = f" ** Error:  check glacier masks match"
                            sys.exit(str_err)
                    
                    #################################
                    # sanity checks

                    # remove low snow (includes negative check)
                    if (tile_snd[0,idim0,idim1] < 1.0) or (tile_swe[0,idim0,idim1] < 0.1):
                        if print_low_snow_removal:
                            print(f"Removing location with SWE = {tile_swe[0,idim0,idim1]} and depth = {tile_snd[0,idim0,idim1]}")
                        tile_swe[0, idim0, idim1] = 0.
                        tile_snd[0, idim0, idim1] = 0.
                        low_snow_removal += 1

                    # boundary checks 2m over glaciers.
                    if tile_snd[0,idim0,idim1] > 2000.0 and tile_veg[idim0,idim1] == 15: # glaciers
                        reduction_factor = 2000.0 / tile_snd[0,idim0,idim1]
                        if print_high_snow_removal:
                            print(f"Reducing glacier location with depth = {tile_snd[0,idim0,idim1]} by factor = {reduction_factor}")
                        tile_snd[0,idim0,idim1] = 2000.0
                        tile_swe[0,idim0,idim1] *= reduction_factor
                        high_snow_removal += 1

                    # max limit 10 m. 10 m non-glacier
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
 
    if print_lims:
        for v in np.arange(3):
            for l in np.arange(4):
                print(f"min {var_list[v]}, level {l}:  {min_val[v,l]}")
                print(f"max {var_list[v]}, level {l}:  {max_val[v,l]}")

        for v in [3,4]:
            l=0
            print(f"min {var_list[v]}, level {l}:  {min_val[v,l]}")
            print(f"max {var_list[v]}, level {l}:  {max_val[v,l]}")

    print(f"Num high_snow_removal: {high_snow_removal}")
    print(f"Num low_snow_removal: {low_snow_removal}")
    print("Processing completed.")

