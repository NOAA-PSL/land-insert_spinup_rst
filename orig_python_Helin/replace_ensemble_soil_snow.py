import os
import numpy as np
from netCDF4 import Dataset

# Clara's orginal ensemble insert script
# replace soil and snow in each member with mem_rescaled + (spunup - <mem_rescaled>)

# set these variables

datestring="2021060121"
res="96"

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

spinslc = ncid.variables['soil_liquid_vol'][0, :, :]
spinsic = ncid.variables['soil_moisture_vol'][0, :, :] - spinslc # soil ice content
spinstc = ncid.variables['temperature_soil'][0, :, :]
spinsnd = ncid.variables['snow_depth'][0, :]
spinswe = ncid.variables['snow_water_equiv'][0, :]

ncid.close()


high_snow_removal = 0
low_snow_removal = 0
low_smc_removal = 0 

for n in np.arange(1,81):

    nloc = -1

    # Loop over tiles
    for itile in range(1, 7):
        print(f"Starting tile: {itile}")

        sfcdata_file = sfcdata_dir+"mem"+str(n).zfill(3)+"/sfc_data.tile"+str(itile)+".nc"
        ncid = Dataset(sfcdata_file, 'r+')

        # read in the ensemblemean
        ensmean_file = sfcdata_dir+"ensmean/sfc_data.tile"+str(itile)+".nc"
        ncid_em = Dataset(ensmean_file)

        # read in the diffs
        inmask = ncid.variables['vtype'][0, :, :]
        sfcslc = ncid.variables['slc'][:]
        sfcsic = ncid.variables['smc'][:] - sfcslc # soil ice content
        sfcstc = ncid.variables['stc'][:]
        sfcswe = ncid.variables['weasdl'][:]
        sfcsnd = ncid.variables['snodl'][:]

        ensmean_sfcslc = ncid_em.variables['slc'][:]
        ensmean_sfcsic = ncid_em.variables['smc'][:] - ensmean_sfcslc #soil ice content
        ensmean_sfcstc = ncid_em.variables['stc'][:]
        ensmean_sfcswe = ncid_em.variables['weasdl'][:]
        ensmean_sfcsnd = ncid_em.variables['snodl'][:]

        ndims = inmask.shape
        print(f"Num vtype /= 0: {np.sum(inmask > 0)}")

        for idim0 in range(ndims[0]):
            for idim1 in range(ndims[1]):
                if inmask[idim0, idim1] != 0:
                    nloc += 1

                    for l in np.arange(4):
                        if ( spinsic[l, nloc] < 0.001 ): # if spinup has no ice, give all members no ice
                                sfcsic[0, l, idim0, idim1] = 0.
                        else: 
                                sfcsic[0, l, idim0, idim1] = max(0.0,spinsic[l, nloc] \
                                + sfcsic[0, l, idim0, idim1]-ensmean_sfcsic[0, l, idim0, idim1]) 

                        sfcslc[0, l, idim0, idim1] = max(0.02,spinslc[l, nloc] \
                                + sfcslc[0, l, idim0, idim1]-ensmean_sfcslc[0, l, idim0, idim1]) 
                        sfcstc[0, l, idim0, idim1] = spinstc[l, nloc] \
                                + sfcstc[0, l, idim0, idim1]-ensmean_sfcstc[0, l, idim0, idim1]
                    # if spinup has no snow, set all members to no snow.
                    if (0.0 < spinsnd[nloc] < 1.0) or (0.0 < spinswe[nloc] < 0.01):
                        sfcswe[0, idim0, idim1] = 0.
                        sfcsnd[0, idim0, idim1] = 0.
                    else:
                        sfcswe[0, idim0, idim1] = spinswe[nloc] \
                            + sfcswe[0, idim0, idim1]-ensmean_sfcswe[0, idim0, idim1]
                        sfcsnd[0, idim0, idim1] = spinsnd[nloc] \
                            + sfcsnd[0, idim0, idim1]-ensmean_sfcsnd[0, idim0, idim1]

                    # Adjust snow parameters based on thresholds
                    if sfcsnd[0,idim0,idim1] > 2000.0 and inmask[idim0, idim1] == 15:
                        reduction_factor = 2000.0 / sfcsnd[0,idim0,idim1]
                        if print_high_snow_removal:
                            print(f"Reducing glacier location with depth = {sfcsnd[0,idim0,idim1]} by factor = {reduction_factor}")
                        sfcsnd[0,idim0,idim1] = 2000.0
                        sfcsnd[0,idim0,idim1] *= reduction_factor
                        high_snow_removal += 1

                    if sfcsnd[0,idim0,idim1] > 10000.0:
                        reduction_factor = 10000.0 / sfcsnd[0,idim0,idim1]
                        if print_high_snow_removal:
                            print(f"Reducing non-glacier location with depth = {spinsnd[iloc]} by factor = {reduction_factor}")
                        sfcsnd[0,idim0,idim1] = 10000.0
                        sfcswe[0,idim0,idim1] *= reduction_factor
                        high_snow_removal += 1

                    if (0.0 < sfcsnd[0,idim0,idim1] < 1.0) or (0.0 < sfcswe[0,idim0,idim1] < 0.01):
                        if print_low_snow_removal:
                            print(f"Removing location with SWE = {spinswe[iloc]} and depth = {spinsnd[iloc]}")
                        sfcsnd[0,idim0,idim1] = 0.0
                        sfcswe[0,idim0,idim1] = 0.0
                        low_snow_removal += 1

        num_in_tiles = nloc + 1
        print(f"Number of cumulative locs: {num_in_tiles}")

        # Update the NetCDF variables
        sfcsmc = sfcslc + sfcsic
        ncid.variables['smc'][:] = sfcsmc
        ncid.variables['slc'][:] = sfcslc
        ncid.variables['stc'][:] = sfcstc
        ncid.variables['weasdl'][:] = sfcswe
        ncid.variables['snodl'][:] = sfcsnd

        ncid.close()

num_in_spinup = len(spinstc[0, :])
print(f"Num in spinup: {num_in_spinup}")
print(f"Num high_snow_removal: {high_snow_removal}")
print(f"Num low_snow_removal: {low_snow_removal}")

if num_in_tiles != num_in_spinup:
    print("Number in tiles != number in spinup")
    exit()

print("Processing completed.")

