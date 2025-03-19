import os
import sys
import numpy as np
from netCDF4 import Dataset


##############################
# get args
if (len(sys.argv) != 5): 
        for i, arg in enumerate(sys.argv):
                print(f"Argument {i}: {arg}")
        str = f" ** Error: expecting 5 arguments: \n ** YYYYMMDDHH resolution static_file directory_tiles directory_vector"
        sys.exit(str)

datestring   = sys.argv[1]
res          = sys.argv[2]
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
vec_snd = ncid.variables['snow_depth'][0, :]
vec_swe = ncid.variables['snow_water_equiv'][0, :]

ncid.close()

num_in_vector = len(vec_stc[0, :])
print(f"Num in vector: {num_in_vector}")

##############################
# Loop over tile files
nloc = -1
high_snow_removal = 0
low_snow_removal = 0

for itile in range(1, 7):
    print(f"Starting tile: {itile}")

    tile_file = tile_dir+"sfc_data.tile"+str(itile)+".nc"

    ncid = Dataset(tile_file, 'r+')

    tile_veg = ncid.variables['vtype'][0, :, :]
    tile_smc = ncid.variables['smc'][:]
    tile_slc = ncid.variables['slc'][:]
    tile_stc = ncid.variables['stc'][:]
    tile_swe = ncid.variables['weasdl'][:]
    tile_snd = ncid.variables['snodl'][:]

    ndims = tile_veg.shape

    for idim0 in range(ndims[0]):
        for idim1 in range(ndims[1]):
            if tile_veg[idim0, idim1] != 0:
                nloc += 1

                # insert vector values
                tile_smc[0, :, idim0, idim1] = vec_smc[:, nloc]
                tile_slc[0, :, idim0, idim1] = vec_slc[:, nloc]
                tile_stc[0, :, idim0, idim1] = vec_stc[:, nloc]
                tile_swe[0, idim0, idim1] = vec_swe[nloc]
                tile_snd[0, idim0, idim1] = vec_snd[nloc]

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

                if (0.0 < tile_snd[0,idim0,idim1] < 1.0) or (0.0 < tile_swe[0,idim0,idim1] < 0.01):
                    if print_low_snow_removal:
                        print(f"Removing location with SWE = {tile_swe[0,idim0,idim1]} and depth = {tile_snd[0,idim0,idim1]}")
                    tile_snd[0,idim0,idim1] = 0.0
                    tile_swe[0,idim0,idim1] = 0.0
                    low_snow_removal += 1

    num_in_tiles = nloc + 1
    print(f"Number of cumulative locs: {num_in_tiles}")

    # Update the NetCDF variables
    ncid.variables['smc'][:] = tile_smc
    ncid.variables['slc'][:] = tile_slc
    ncid.variables['stc'][:] = tile_stc
    ncid.variables['weasdl'][:] = tile_swe
    ncid.variables['snodl'][:] = tile_snd

    ncid.close()

if num_in_tiles != num_in_vector:
    str = f" ** Error: Number in tiles != number in vector"
    sys.exit(str)

print(f"Num high_snow_removal: {high_snow_removal}")
print(f"Num low_snow_removal: {low_snow_removal}")
print("Processing completed.")

