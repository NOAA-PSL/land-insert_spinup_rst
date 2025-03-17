import os
import numpy as np
from netCDF4 import Dataset

print_high_snow_removal = True
print_low_snow_removal = False

sfcdata_path = "/scratch1/NCEPDEV/stmp2/Helin.Wei/spinup/cycle/C384/sfc_data"
spinup_path  = "/scratch2/NCEPDEV/stmp1/Youlong.Xia/landDA/cycle_land/C384/DA_GHCN_HR4/mem000/restarts/vector"

# Identify directories starting with 'gfs.'
dirs_to_process = sorted([os.path.join(sfcdata_path, d) for d in os.listdir(sfcdata_path) if d.startswith('gfs.') and os.path.isdir(os.path.join(sfcdata_path, d))])

# Check if directories were found
if not dirs_to_process:
    print("No directories found starting with 'gfs.'. Please check the path or the pattern.")
    exit(1)

numdates = len(dirs_to_process)
print(f"Processing {numdates} dates")

# Open vegetation file
try:
    vegetation_file = Dataset("/scratch2/NCEPDEV/land/Michael.Barlage/forcing/C384/vector/ufs-land_C384_hr3_static_fields.nc", 'r')
except IOError as e:
    print("Error opening vegetation file:", e)
    exit()

vegetation_type = vegetation_file.variables['vegetation_category'][:]

# Loop over dates
for date_to_process in dirs_to_process:
    datestring = date_to_process.split('gfs.')[1]  # Extract date part from directory name

    sfc_date = datestring
    spin_date = f"{datestring[:4]}-{datestring[4:6]}-{datestring[6:8]}"

    print(f"Moving: {spin_date} to {sfc_date}")

    spinup_file_path = f"{spinup_path}/ufs_land_restart_anal.{spin_date}_00-00-00.nc"
    if not os.path.exists(spinup_file_path):
        print(f"Spinup file not found: {spinup_file_path}")
        continue

    # Open spinup file
    try:
        spinup_file = Dataset(spinup_file_path, 'r')
    except IOError as e:
        print("Error opening spinup file:", e)
        continue

    spinsmc = spinup_file.variables['soil_moisture_vol'][0, :, :]
    spinslc = spinup_file.variables['soil_liquid_vol'][0, :, :]
    spinstc = spinup_file.variables['temperature_soil'][0, :, :]
    spinsnd = spinup_file.variables['snow_depth'][0, :]
    spinswe = spinup_file.variables['snow_water_equiv'][0, :]

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

        sfcdata_file_path = os.path.join(date_to_process, f"sfc_data.tile{itile}.nc")
        if not os.path.exists(sfcdata_file_path):
            print(f"Sfc data file not found: {sfcdata_file_path}")
            continue

        # Open sfc data file for writing
        try:
            sfcdata_file = Dataset(sfcdata_file_path, 'r+')
        except IOError as e:
            print("Error opening sfc data file:", e)
            continue

        inmask = sfcdata_file.variables['vtype'][0, :, :]
        sfcsmc = sfcdata_file.variables['smc'][:]
        sfcslc = sfcdata_file.variables['slc'][:]
        sfcstc = sfcdata_file.variables['stc'][:]
        sfcswe = sfcdata_file.variables['weasdl'][:]
        sfcsnd = sfcdata_file.variables['snodl'][:]

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
        sfcdata_file.variables['smc'][:] = sfcsmc
        sfcdata_file.variables['slc'][:] = sfcslc
        sfcdata_file.variables['stc'][:] = sfcstc
        sfcdata_file.variables['weasdl'][:] = sfcswe
        sfcdata_file.variables['snodl'][:] = sfcsnd

        sfcdata_file.close()

    if num_in_tiles != num_in_spinup:
        print("Number in tiles != number in spinup")
        exit()

print("Processing completed.")

