# this is Clara's version of Helin's original code to insert land ICS spun-up 
# offline (vector) format into cold start tile files. 
# I stripped out the assumed directory structure, and looping on dates.
# Based on Mike Barlage's earlier code. March 2025.
# 
import os
import numpy as np
from netCDF4 import Dataset

# set these variables

datestring="2021060121"
res="C192"

sfcdata_dir = "/scratch2/BMC/gsienkf/Clara.Draper/ensICS/insert/C"+res+"/"+datestring+"/"
spinup_dir  = "/scratch2/BMC/gsienkf/Clara.Draper/ensICS/spinup/C"+res+"/"

static_file = "/scratch2/NCEPDEV/land/data/ufs-land-driver/vector_inputs/C"+res+".mx025/ufs-land_C"+res+".mx025_hr3_static_fields.nc"

##################################

print_high_snow_removal = True
print_low_snow_removal = False

# get veg type
ncid = Dataset(static_file,'r')
vegetation_type = ncid['vegetation_category'][:]
ncid.close()

# read in spun-up variables
spin_date = f"{datestring[:4]}-{datestring[4:6]}-{datestring[6:8]}_{datestring[8:10]}"
spinup_file = spinup_dir+"ufs_land_restart."+spin_date+"-00-00.nc"

ncid = Dataset(spinup_file, 'r')

spinsmc = ncid.variables['soil_moisture_vol'][0, :, :]
spinslc = ncid.variables['soil_liquid_vol'][0, :, :]
spinstc = ncid.variables['temperature_soil'][0, :, :]
spinsnd = ncid.variables['snow_depth'][0, :]
spinswe = ncid.variables['snow_water_equiv'][0, :]

ncid.close()

high_snow_removal = 0
low_snow_removal = 0

# Adjust snow parameters based on thresholds
for iloc in range(len(spinsnd)):
    if spinsnd[iloc] > 2000.0 and vegetation_type[iloc] == 15:
        reduction_factor = 2000.0 / spinsnd[iloc]
        if print_high_snow_removal:
            print(f"Reducing glacier location with depth = {spinsnd[iloc]} by factor = {reduction_factor}")
        spinsnd[iloc] = 2000.0
        spinswe[iloc] *= reduction_factor
        high_snow_removal += 1

    if spinsnd[iloc] > 10000.0:
        reduction_factor = 10000.0 / spinsnd[iloc]
        if print_high_snow_removal:
            print(f"Reducing non-glacier location with depth = {spinsnd[iloc]} by factor = {reduction_factor}")
        spinsnd[iloc] = 10000.0
        spinswe[iloc] *= reduction_factor
        high_snow_removal += 1

    if (0.0 < spinsnd[iloc] < 1.0) or (0.0 < spinswe[iloc] < 0.01):
        if print_low_snow_removal:
            print(f"Removing location with SWE = {spinswe[iloc]} and depth = {spinsnd[iloc]}")
        spinsnd[iloc] = 0.0
        spinswe[iloc] = 0.0
        low_snow_removal += 1

num_in_spinup = len(spinstc[0, :])
print(f"Num in spinup: {num_in_spinup}")
print(f"Num high_snow_removal: {high_snow_removal}")
print(f"Num low_snow_removal: {low_snow_removal}")

nloc = -1

# Loop over tiles
for itile in range(1, 7):
    print(f"Starting tile: {itile}")

    sfcdata_file = sfcdata_dir+"sfc_data.tile"+str(itile)+".nc"

    ncid = Dataset(sfcdata_file, 'r+')

    inmask = ncid.variables['vtype'][0, :, :]
    sfcsmc = ncid.variables['smc'][:]
    sfcslc = ncid.variables['slc'][:]
    sfcstc = ncid.variables['stc'][:]
    sfcswe = ncid.variables['weasdl'][:]
    sfcsnd = ncid.variables['snodl'][:]

    ndims = inmask.shape
    print(f"Num vtype /= 0: {np.sum(inmask > 0)}")

    for idim0 in range(ndims[0]):
        for idim1 in range(ndims[1]):
            if inmask[idim0, idim1] != 0:
                nloc += 1

                sfcsmc[0, :, idim0, idim1] = spinsmc[:, nloc]
                sfcslc[0, :, idim0, idim1] = spinslc[:, nloc]
                sfcstc[0, :, idim0, idim1] = spinstc[:, nloc]
                sfcswe[0, idim0, idim1] = spinswe[nloc]
                sfcsnd[0, idim0, idim1] = spinsnd[nloc]

    num_in_tiles = nloc + 1
    print(f"Number of cumulative locs: {num_in_tiles}")

    # Update the NetCDF variables
    ncid.variables['smc'][:] = sfcsmc
    ncid.variables['slc'][:] = sfcslc
    ncid.variables['stc'][:] = sfcstc
    ncid.variables['weasdl'][:] = sfcswe
    ncid.variables['snodl'][:] = sfcsnd

    ncid.close()

if num_in_tiles != num_in_spinup:
    print("Number in tiles != number in spinup")
    exit()

print("Processing completed.")

