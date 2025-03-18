import os
import sys
import numpy as np
from netCDF4 import Dataset

if (len(sys.argv) != 6): 
        for i, arg in enumerate(sys.argv):
                print(f"Argument {i}: {arg}")
        str = f" ** Error: expecting 5 arguments: \n ** YYYYMMDDHH resolution static_file directory_tiles directory_vector"
        sys.exit(str)

datestring   = sys.argv[1]
res          = sys.argv[2]
static_file  = sys.argv[3]
tile_dir     = sys.argv[4] 
vector_dir   = sys.argv[5]

print_high_snow_removal = True
print_low_snow_removal = False

# get veg type
ncid = Dataset(static_file,'r')
vegetation_type = ncid['vegetation_category'][:]
ncid.close()

# read in spun-up variables
vec_date = f"{datestring[:4]}-{datestring[4:6]}-{datestring[6:8]}_{datestring[8:10]}"
vector_file = vector_dir+"ufs_land_restart."+vec_date+"-00-00.nc"

ncid = Dataset(vector_file, 'r')

vec_smc = ncid.variables['soil_moisture_vol'][0, :, :]
vec_slc = ncid.variables['soil_liquid_vol'][0, :, :]
vec_stc = ncid.variables['temperature_soil'][0, :, :]
vec_snd = ncid.variables['snow_depth'][0, :]
vec_swe = ncid.variables['snow_water_equiv'][0, :]

ncid.close()

high_snow_removal = 0
low_snow_removal = 0

# Adjust snow parameters based on thresholds
for iloc in range(len(vec_snd)):
    if vec_snd[iloc] > 2000.0 and vegetation_type[iloc] == 15:
        reduction_factor = 2000.0 / vec_snd[iloc]
        if print_high_snow_removal:
            print(f"Reducing glacier location with depth = {vec_snd[iloc]} by factor = {reduction_factor}")
        vec_snd[iloc] = 2000.0
        vec_swe[iloc] *= reduction_factor
        high_snow_removal += 1

    if vec_snd[iloc] > 10000.0:
        reduction_factor = 10000.0 / vec_snd[iloc]
        if print_high_snow_removal:
            print(f"Reducing non-glacier location with depth = {vec_snd[iloc]} by factor = {reduction_factor}")
        vec_snd[iloc] = 10000.0
        vec_swe[iloc] *= reduction_factor
        high_snow_removal += 1

    if (0.0 < vec_snd[iloc] < 1.0) or (0.0 < vec_swe[iloc] < 0.01):
        if print_low_snow_removal:
            print(f"Removing location with SWE = {vec_swe[iloc]} and depth = {vec_snd[iloc]}")
        vec_snd[iloc] = 0.0
        vec_swe[iloc] = 0.0
        low_snow_removal += 1

num_in_vector = len(vec_stc[0, :])
print(f"Num in vector: {num_in_vector}")
print(f"Num high_snow_removal: {high_snow_removal}")
print(f"Num low_snow_removal: {low_snow_removal}")

nloc = -1

# Loop over tiles
for itile in range(1, 7):
    print(f"Starting tile: {itile}")

    tile_file = tile_dir+"sfc_data.tile"+str(itile)+".nc"

    ncid = Dataset(tile_file, 'r+')

    inmask = ncid.variables['vtype'][0, :, :]
    sfc_smc = ncid.variables['smc'][:]
    sfc_slc = ncid.variables['slc'][:]
    sfc_stc = ncid.variables['stc'][:]
    sfc_swe = ncid.variables['weasdl'][:]
    sfc_snd = ncid.variables['snodl'][:]

    ndims = inmask.shape
    print(f"Num vtype /= 0: {np.sum(inmask > 0)}")

    for idim0 in range(ndims[0]):
        for idim1 in range(ndims[1]):
            if inmask[idim0, idim1] != 0:
                nloc += 1

                sfc_smc[0, :, idim0, idim1] = vec_smc[:, nloc]
                sfc_slc[0, :, idim0, idim1] = vec_slc[:, nloc]
                sfc_stc[0, :, idim0, idim1] = vec_stc[:, nloc]
                sfc_swe[0, idim0, idim1] = vec_swe[nloc]
                sfc_snd[0, idim0, idim1] = vec_snd[nloc]

    num_in_tiles = nloc + 1
    print(f"Number of cumulative locs: {num_in_tiles}")

    # Update the NetCDF variables
    ncid.variables['smc'][:] = sfc_smc
    ncid.variables['slc'][:] = sfc_slc
    ncid.variables['stc'][:] = sfc_stc
    ncid.variables['weasdl'][:] = sfc_swe
    ncid.variables['snodl'][:] = sfc_snd

    ncid.close()

if num_in_tiles != num_in_vector:
    print("Number in tiles != number in vector")
    exit()

print("Processing completed.")

