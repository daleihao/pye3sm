import os #operate folder
import sys
import numpy as np
import platform #os
from scipy.interpolate import griddata #generate grid
from pathlib import Path #get the home directory
from netCDF4 import Dataset #read netcdf
from osgeo import gdal #the default operator


sPath_library_python = sWorkspace_code +  slash + 'python' + slash + 'library' + slash + 'eslib_python'
print(sPath_library_python)
sys.path.append(sPath_library_python)
from envi.envi_write_header import envi_write_header

missing_value = -9999.0 #used to save binary
sExtension_nc = '.nc'
sExtension_envi ='.dat'
sExtension_header ='.hdr'
sExtension_tif = '.tif'

sModel = 'h2sc'
iCase = 179
nlayer = 15
iYear_start = 1948
iYear_end = 2013
#vsdm dimension
#aDimension = [ nlayer, 96, 144]
mms2mmd = 24 * 3600.0
dConversion = 1.0
sVariable = 'H2OSOI'
#for the sake of simplicity, all directory will be the same, no matter on mac or cluster
sWorkspace_data = home + slash + 'data'
sWorkspace_simulation = sWorkspace_scratch + slash + 'csmruns'
sWorkspace_analysis = sWorkspace_scratch + slash + '03model' + slash \
    + sModel + slash + 'analysis'
if not os.path.isdir(sWorkspace_analysis):
    os.makedirs(sWorkspace_analysis)

#we only need to change the case number, all variables will be processed one by one

sCase = sModel + "{:0d}".format(iCase)
sWorkspace_simulation_case = sWorkspace_simulation + slash + sCase + slash + 'run'
sWorkspace_analysis_case = sWorkspace_analysis + slash + sCase

if not os.path.exists(sWorkspace_analysis_case):
    os.makedirs(sWorkspace_analysis_case)

iMonth_start = 1
iMonth_end = 12

#read in global 0.5 * 0.5 mask
sFilename_mask = sWorkspace_data + slash \
    + 'h2sc' + slash + 'raster' + slash + 'dem' + slash \
    + 'MOSART_Global_half_20180606c.chang_9999.nc'
aDatasets = Dataset(sFilename_mask)
netcdf_format = aDatasets.file_format
print(netcdf_format)
print("Print dimensions:")
print(aDatasets.dimensions.keys())
print("Print variables:")
print(aDatasets.variables.keys())
for sKey, aValue in aDatasets.variables.items():
    if "ele0" == sKey:
        aEle0 = (aValue[:]).data
        aMask = np.where(aEle0 == missing_value)
        break
    
print('Prepare the map grid')
longitude = np.arange(-180, 180, 0.5)
latitude = np.arange(-90, 90, 0.5)
grid_x, grid_y = np.meshgrid(longitude, latitude)
#prepare the header in
headerParameters = {}

headerParameters['ncolumn'] = '720'
headerParameters['nrow'] = '360'
headerParameters['ULlon'] = '-180'
headerParameters['ULlat'] = '90'
headerParameters['pixelSize'] = '0.5'
headerParameters['nband'] = '1'
headerParameters['offset'] = '0'
headerParameters['data_type'] = '4'
headerParameters['bsq'] = 'bsq'
headerParameters['byte_order'] = '0'
headerParameters['missing_value'] = '-9999'

for iYear in range(iYear_start, iYear_end + 1):
    sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)

    for iMonth in range(iMonth_start, iMonth_end + 1):
        sMonth = str(iMonth).zfill(2)

        sDummy = '.clm2.h0.' + sYear + '-' + sMonth + sExtension_nc
        sFilename = sWorkspace_simulation_case + slash + sCase + sDummy

        #read before modification

        if os.path.exists(sFilename):
            print("Yep, I can read that file!")
        else:
            print(sFilename)
            print("Nope, the path doesn't reach your file. Go research filepath in python")
            quit()

        aDatasets = Dataset(sFilename)
    

        for sKey, aValue in aDatasets.variables.items():

            if (sKey == 'lon'):
                #print(aValue.datatype)
                #print(aValue.dimensions)
                aLongitude = (aValue[:]).data
                continue
            if (sKey == 'lat'):
                #print(aValue.datatype)
                #print(aValue.dimensions)
                aLatitude = (aValue[:]).data
                continue
        
        #quality control the longitude data
        dummy_index = np.where(aLongitude > 180)
        aLongitude[dummy_index] = aLongitude[dummy_index] - 360.0

        #read the actual data
        for sKey, aValue in aDatasets.variables.items():
            if sVariable == sKey:
                #for attrname in aValue.ncattrs():
                #print("{} -- {}".format(attrname, getattr(aValue, attrname)))
                
                missing_value1 = getattr(aValue, 'missing_value')
                aData = (aValue[:]).data
                print(aValue.datatype)
                print(aValue.dimensions)
                dummy1 =  len(aData[0][0])
                #reshape dimension
                #aData_all = aData.reshape(aDimension)   
                
                aData_all = aData.reshape(nlayer,  dummy1)   
                aData_layer =  aData_all[0, :]         
                #dummy_index = np.where( (aData != missing_value1) & ( np.isfinite(aData) ) )

                dummy_index = np.where( (aLongitude < 180 ) & ( aLatitude < 90 ) \
                              &(aData_layer != missing_value1 ) )

                

                aLongitude_subset = aLongitude[dummy_index]
                aLatitude_subset = aLatitude[dummy_index]
                aData_subset = aData_layer[dummy_index] 


                points = np.vstack((aLongitude_subset, aLatitude_subset))
                points = np.transpose(points)
                values = aData_subset * dConversion
                #resample
                grid_z3 = griddata(points, values,\
                         (grid_x, grid_y), method='nearest')
                #save outside
                grid_z3[aMask] = missing_value

                if(np.isnan( values ).any()) :
                    print('nan')

                sWorkspace_variable_dat = sWorkspace_analysis_case + slash \
                    + sVariable.lower() + slash + 'dat'
                if not os.path.exists(sWorkspace_variable_dat):
                    os.makedirs(sWorkspace_variable_dat)
                sWorkspace_variable_tif = sWorkspace_analysis_case + slash + sVariable.lower() + slash + 'tiff'
                if not os.path.exists(sWorkspace_variable_tif):
                    os.makedirs(sWorkspace_variable_tif)
                
                sFilename_envi = sWorkspace_variable_dat + slash + sVariable.lower() + sYear + sMonth + sExtension_envi
                a = np.flip(grid_z3, 0)
                a.astype('float32').tofile(sFilename_envi)
                #write header
                sFilename_header = sWorkspace_variable_dat + slash + sVariable.lower() + sYear + sMonth + sExtension_header
                headerParameters['sFilename'] = sFilename_header
                envi_write_header(sFilename_header, headerParameters)

                #Open output format driver, see gdal_translate --formats for list
                src_ds = gdal.Open( sFilename_envi )
                sFormat = "GTiff"
                driver = gdal.GetDriverByName( sFormat )

                #Output to new format
                sFilename_tiff = sWorkspace_variable_tif + slash + sVariable.lower() + sYear + sMonth + sExtension_tif
                dst_ds = driver.CreateCopy( sFilename_tiff, src_ds, 0 )

                #Properly close the datasets to flush to disk
                dst_ds = None
                src_ds = None



    print("finished")
