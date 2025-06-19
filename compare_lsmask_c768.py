import os
import sys
import numpy as np
from netCDF4 import Dataset

#ifname_gdas     = '/scratch2/NCEPDEV/stmp1/Zhichang.Guo/Work/Temp2/change_res/C384_ORIG/2025051421/mem001/sfc_data.nc'
ifname_gdas     = '/scratch2/NCEPDEV/stmp1/Zhichang.Guo/Work/Temp5/change_res/C768_ORIG/2024111503/control/sfc_data.nc'
#ifname_20230615 = '/scratch1/NCEPDEV/global/glopara/fix/orog/20230615/C768.mx025/sfc/C768.mx025.vegetation_type.nc'
ifname_20230615 = '/scratch1/NCEPDEV/global/glopara/fix/orog/20230615/C768/sfc/C768.vegetation_type.nc'
ifname_20231027 = '/scratch1/NCEPDEV/global/glopara/fix/orog/20231027/C768/sfc/C768.mx025.vegetation_type.nc'
ifname_20240917 = '/scratch1/NCEPDEV/global/glopara/fix/orog/20240917/C768/sfc/C768.mx025.vegetation_type.nc'

land_locations_gdas     = 0
land_locations_20230615 = 0
land_locations_20231027 = 0
land_locations_20240917 = 0
same_gdas_20230615      = True
same_20231027_20240917  = True

for itile in range(1, 7):
    fname_gdas     = ifname_gdas.replace('.nc','.tile'+str(itile)+'.nc')
    fname_20230615 = ifname_20230615.replace('.nc','.tile'+str(itile)+'.nc')
    fname_20231027 = ifname_20231027.replace('.nc','.tile'+str(itile)+'.nc')
    fname_20240917 = ifname_20240917.replace('.nc','.tile'+str(itile)+'.nc')

    ncid_gdas     = Dataset(fname_gdas, 'r')
    ncid_20230615 = Dataset(fname_20230615, 'r')
    ncid_20231027 = Dataset(fname_20231027, 'r')
    ncid_20240917 = Dataset(fname_20240917, 'r')

    vtype_gdas     = ncid_gdas.variables['vtype'][0, :, :]               #vegetation_type used for Noah
    vtype_20230615 = ncid_20230615.variables['vegetation_type'][0, :, :] #vegetation_type used for NoahMP
    vtype_20231027 = ncid_20231027.variables['vegetation_type'][0, :, :]
    vtype_20240917 = ncid_20240917.variables['vegetation_type'][0, :, :]

    vtype_water = 17

    ndims = vtype_gdas.shape
    for idim0 in range(ndims[0]):
        for idim1 in range(ndims[1]):
            lsmask_gdas     = 0
            lsmask_20230615 = 0
            ivtype_20231027 = 0
            ivtype_20240917 = 0
            if vtype_gdas[idim0, idim1] > 0.5:
                land_locations_gdas += 1
                lsmask_gdas = 1 
            if vtype_20230615[idim0, idim1] > 0.5 and int(round(vtype_20230615[idim0, idim1])) != vtype_water:
                land_locations_20230615 += 1
                lsmask_20230615 = 1
            if vtype_20231027[idim0, idim1] > 0.5 and int(round(vtype_20231027[idim0, idim1])) != vtype_water:
                land_locations_20231027 += 1
                ivtype_20231027 = int(round(vtype_20231027[idim0, idim1]))
            if vtype_20240917[idim0, idim1] > 0.5 and int(round(vtype_20240917[idim0, idim1])) != vtype_water:
                land_locations_20240917 += 1
                ivtype_20240917 = int(round(vtype_20240917[idim0, idim1]))
            if lsmask_gdas != lsmask_20230615:
                same_gdas_20230615 = False
                print(idim0, idim1, itile, lsmask_gdas, lsmask_20230615)
            if ivtype_20231027 != ivtype_20240917:
                same_20231027_20240917 = False
                print(idim0, idim1, itile, ivtype_20231027, ivtype_20240917)
    ncid_gdas.close()
    ncid_20230615.close()
    ncid_20231027.close()
    ncid_20240917.close()
if same_gdas_20230615:
    print("land-sea mask is same between GDAS C384 and version 20230615 C384")
else:
    print("land-sea mask is different between GDAS C384 and version 20230615 C384")
if same_20231027_20240917:
    print("vegetation mask is same between 20231027 C384 and 20240917 C384")
else:
    print("vegetation mask is different between 20231027 C384 and 20240917 C384")
print("Land locations for GDAS C384:     ",land_locations_gdas)
print("Land locations for 20230615 C384: ",land_locations_gdas)
print("Land locations for 20231027 C384: ",land_locations_20231027)
print("Land locations for 20240917 C384: ",land_locations_20240917)
