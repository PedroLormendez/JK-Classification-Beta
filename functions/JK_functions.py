#!/usr/bin/env python
# coding: utf-8

# In[ ]:
"""
@Author: Pedro Herrera-Lormendez
"""
#Importing neccesary modules
import numpy as np
import pandas as pd
import xarray as xr

def checking_lon_coords(mslp, lon_name):
    """
    This function checks and fixed the longitude coordinate
    values going from 180 to -180 º.
    
    :param mslp: mean sea level pressure data in xarray format
    :param lon_name: name of longitude coordinate
    """
    if mslp[lon_name][-1] > 180:
        # Adjust lon values to make sure they are within (-180, 180)
        mslp['_longitude_adjusted'] = xr.where(
            mslp[lon_name] > 180,
            mslp[lon_name] - 360,
            mslp[lon_name])

        # reassign the new coords to as the main lon coords
        # and sort DataArray using new coordinate values
        mslp = (
            mslp
            .swap_dims({lon_name: '_longitude_adjusted'})
            .sel(**{'_longitude_adjusted': sorted(mslp._longitude_adjusted)})
            .drop(lon_name))

        mslp = mslp.rename({'_longitude_adjusted': lon_name})
    else:
        pass
    return(mslp)

def constants(phi, lon):
    """
    Computing values of constants dependant on latitude and longitude
    They represent the constants referred to the relative differences
    between the grid-point spacing in the E-W and N-S direction
    
    :param phi: values of central latitude gridpoints
    :param lon: longitude values
    """
    SC = 1/np.cos(np.deg2rad(phi))
    SC.name="longitue"
    sc=xr.concat([SC]*len(lon),'logitude').T

    ZWA = np.sin(np.deg2rad(phi)) / np.sin (np.deg2rad(phi - 5))
    ZWA.name="longitue"
    zwa=xr.concat([ZWA]*len(lon),'logitude').T

    ZWB = np.sin(np.deg2rad(phi)) / np.sin (np.deg2rad(phi + 5))
    ZWB.name="longitue"
    zwb=xr.concat([ZWB]*len(lon),'logitude').T

    ZSC = (1/(2*(np.cos(np.deg2rad(phi))**2)))
    ZSC.name="longitue"
    zsc=xr.concat([ZSC]*len(lon),'logitude').T
    return (sc, zwa, zwb, zsc)

def direction_def_NH(deg_used):
    '''
    This function assigns the wind direction labels of the circulation types for 
    the Northern Hemisphere
    
    :param deg_used: xarray of wind direction values in degrees

    '''
    direction = xr.where( (deg_used>247) & (deg_used<=292), 'W', np.nan)
    direction = xr.where( (deg_used>292) & (deg_used<=337), 'NW', direction)
    direction = xr.where( (deg_used>337), 'N', direction)
    direction = xr.where( (deg_used>=0) & (deg_used<=22), 'N', direction)
    direction = xr.where( (deg_used>22) & (deg_used<=67), 'NE', direction)
    direction = xr.where( (deg_used>67) & (deg_used<=112), 'E', direction)
    direction = xr.where( (deg_used>112) & (deg_used<=157), 'SE', direction)
    direction = xr.where( (deg_used>157) & (deg_used<=202), 'S', direction)
    direction = xr.where( (deg_used>202) & (deg_used<=247), 'SW', direction)
    return(direction)

def direction_def_SH(deg_used):
    '''
    This function assigns the wind direction labels of the circulation types for 
    the Southern Hemisphere
    
    :param deg_used: xarray of wind direction values in degrees
    '''    
    direction = xr.where( (deg_used>247) & (deg_used<=292), 'E', np.nan)
    direction = xr.where( (deg_used>292) & (deg_used<=337), 'SE', direction)
    direction = xr.where( (deg_used>337), 'S', direction)
    direction = xr.where( (deg_used>=0) & (deg_used<=22), 'S', direction)
    direction = xr.where( (deg_used>22) & (deg_used<=67), 'SW', direction)
    direction = xr.where( (deg_used>67) & (deg_used<=112), 'W', direction)
    direction = xr.where( (deg_used>112) & (deg_used<=157), 'NW', direction)
    direction = xr.where( (deg_used>157) & (deg_used<=202), 'N', direction)
    direction = xr.where( (deg_used>202) & (deg_used<=247), 'NE', direction)
    return(direction)

def assign_lwt(F_i, Z_i, direction_i):
    '''
    This function assigns the corresponding circulation types' coding
    
    :param         F_i: xarray of Total Flow term (F)
    :param         Z_i: xarry of Total Shear Vorticity term (Z)
    :param direction_i: xarray of Flow Direction
    '''
    lwt = xr.where( (Z_i<0) & (direction_i=='NE'), 1, np.nan)    
    lwt = xr.where( (Z_i<0) & (direction_i=='E'),  2, lwt)
    lwt = xr.where( (Z_i<0) & (direction_i=='SE'), 3, lwt)
    lwt = xr.where( (Z_i<0) & (direction_i=='S'),  4, lwt)
    lwt = xr.where( (Z_i<0) & (direction_i=='SW'), 5, lwt)
    lwt = xr.where( (Z_i<0) & (direction_i=='W'),  6, lwt)
    lwt = xr.where( (Z_i<0) & (direction_i=='NW'), 7, lwt)
    lwt = xr.where( (Z_i<0) & (direction_i=='N'),  8, lwt)

    lwt = xr.where( (xr.ufuncs.fabs(Z_i)<F_i) & (direction_i=='NE'), 11, lwt)    
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)<F_i) & (direction_i=='E'),  12, lwt)
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)<F_i) & (direction_i=='SE'), 13, lwt)
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)<F_i) & (direction_i=='S'),  14, lwt)
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)<F_i) & (direction_i=='SW'), 15, lwt)
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)<F_i) & (direction_i=='W'),  16, lwt)
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)<F_i) & (direction_i=='NW'), 17, lwt)
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)<F_i) & (direction_i=='N'),  18, lwt)

    lwt = xr.where( ( (xr.ufuncs.fabs(Z_i)) > (2*F_i) ) & (Z_i>0), 20, lwt)
    lwt = xr.where( ( (xr.ufuncs.fabs(Z_i)) > (2*F_i) ) & (Z_i<0),  0, lwt)

    lwt = xr.where( (xr.ufuncs.fabs(Z_i)>F_i) & (xr.ufuncs.fabs(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='NE'), 21, lwt)    
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)>F_i) & (xr.ufuncs.fabs(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='E'),  22, lwt)
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)>F_i) & (xr.ufuncs.fabs(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='SE'), 23, lwt)
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)>F_i) & (xr.ufuncs.fabs(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='S'),  24, lwt)
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)>F_i) & (xr.ufuncs.fabs(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='SW'), 25, lwt)
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)>F_i) & (xr.ufuncs.fabs(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='W'),  26, lwt)
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)>F_i) & (xr.ufuncs.fabs(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='NW'), 27, lwt)
    lwt = xr.where( (xr.ufuncs.fabs(Z_i)>F_i) & (xr.ufuncs.fabs(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='N'),  28, lwt)

    lwt = xr.where( (F_i<6) & (xr.ufuncs.fabs(Z_i) < 6), -1, lwt)
    #lwt = -9 #Default value does not belong to any Circulation

    return lwt,Z_i

def extracting_gridpoints_rean_area(mslp, lat, lon):
    """
    This function extracts the 16 moving gridded points over a defined area (not globe)
    given a Reanalysis (ERA5 or ERA20). This gridpoints are
    neccesary for the computation of the terms
    """
    #Gridpoint 1
    lat1 = lat+10
    lon1 = lon-5
    lat1 = lat.sel(latitude = lat1, method = 'nearest')        
    lon1 = lon.sel(longitude = lon1, method = 'nearest')     
    p1 = np.array(mslp.sel(latitude = lat1, longitude = lon1))
    #Gridpoint 2
    lat2 = lat + 10
    lon2 = lon + 5
    lat2 = lat.sel(latitude = lat2, method = 'nearest')        
    lon2 = lon.sel(longitude = lon2, method = 'nearest')     
    p2 = np.array(mslp.sel(latitude = lat2, longitude = lon2))
    #Gridpoint 3
    lat3 = lat + 5
    lon3 = lon - 15
    lat3 = lat.sel(latitude = lat3, method = 'nearest')        
    lon3 = lon.sel(longitude = lon3, method = 'nearest')     
    p3 = np.array(mslp.sel(latitude = lat3, longitude = lon3))
    #Gridpoint 4
    lat4 = lat + 5
    lon4 = lon  -5
    lat4 = lat.sel(latitude = lat4, method = 'nearest')        
    lon4 = lon.sel(longitude = lon4, method = 'nearest')     
    p4 = np.array(mslp.sel(latitude = lat4, longitude = lon4))
    #Gridpoint 5
    lat5 = lat + 5
    lon5 = lon + 5
    lat5 = lat.sel(latitude = lat5, method = 'nearest')        
    lon5 = lon.sel(longitude = lon5, method = 'nearest')     
    p5 = np.array(mslp.sel(latitude = lat5, longitude = lon5))
    #Gridpoint 6
    lat6 = lat + 5
    lon6 = lon + 15
    lat6 = lat.sel(latitude = lat6, method = 'nearest')        
    lon6 = lon.sel(longitude = lon6, method = 'nearest')     
    p6 = np.array(mslp.sel(latitude = lat6, longitude = lon6))
    #Gridpoint 7
    lat7 = lat
    lon7 = lon - 15
    lat7 = lat.sel(latitude = lat7, method = 'nearest')        
    lon7 = lon.sel(longitude = lon7, method = 'nearest')     
    p7 = np.array(mslp.sel(latitude = lat7, longitude = lon7))
    #Gridpoint 8
    lat8 = lat
    lon8 = lon -5
    lat8 = lat.sel(latitude = lat8, method = 'nearest')        
    lon8 = lon.sel(longitude = lon8, method = 'nearest')     
    p8 = np.array(mslp.sel(latitude = lat8, longitude = lon8))
    #Gridpoint 9
    lat9 = lat
    lon9 = lon + 5
    lat9 = lat.sel(latitude = lat9, method = 'nearest')        
    lon9 = lon.sel(longitude = lon9, method = 'nearest')     
    p9 = np.array(mslp.sel(latitude = lat9, longitude = lon9))
    #Gridpoint 10
    lat10 = lat
    lon10 = lon + 15
    lat10 = lat.sel(latitude = lat10, method = 'nearest')        
    lon10 = lon.sel(longitude = lon10, method = 'nearest')     
    p10 = np.array(mslp.sel(latitude = lat10, longitude = lon10))
    #Gridpoint 11
    lat11 = lat - 5
    lon11 = lon - 15
    lat11 = lat.sel(latitude = lat11, method = 'nearest')        
    lon11 = lon.sel(longitude = lon11, method = 'nearest')     
    p11 = np.array(mslp.sel(latitude = lat11, longitude = lon11))
    #Gridpoint 12
    lat12 = lat - 5
    lon12 = lon - 5
    lat12 = lat.sel(latitude = lat12, method = 'nearest')        
    lon12 = lon.sel(longitude = lon12, method = 'nearest')     
    p12 = np.array(mslp.sel(latitude = lat12, longitude = lon12))
    #Gridpoint 13
    lat13 = lat - 5
    lon13 = lon + 5
    lat13 = lat.sel(latitude = lat13, method = 'nearest')        
    lon13 = lon.sel(longitude = lon13, method = 'nearest')     
    p13 = np.array(mslp.sel(latitude = lat13, longitude = lon13))
    #Gridpoint 14
    lat14 = lat - 5
    lon14 = lon + 15
    lat14 = lat.sel(latitude = lat14, method = 'nearest')        
    lon14 = lon.sel(longitude = lon14, method = 'nearest')    
    p14 = np.array(mslp.sel(latitude = lat14, longitude = lon14))
    #Gridpoint 15
    lat15 = lat - 10
    lon15 = lon - 5
    lat15 = lat.sel(latitude = lat15, method = 'nearest')        
    lon15 = lon.sel(longitude = lon15, method = 'nearest')       
    p15 = np.array(mslp.sel(latitude = lat15, longitude = lon15))
    #Gridpoint 16
    lat16 = lat - 10
    lon16 = lon + 5
    lat16 = lat.sel(latitude = lat16, method = 'nearest')        
    lon16 = lon.sel(longitude = lon16, method = 'nearest')       
    p16 = np.array(mslp.sel(latitude = lat16, longitude = lon16))
    return (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16)

    
def extracting_gridpoints_gcm_area(mslp, lat, lon):
    """
    This function extracts the 16 moving gridded points over a defined area (not globe)
    given a Global Climate Model Dataset. This gridpoints are
    neccesary for the computation of the terms
    """
    #Gridpoint 1
    lat1 = lat+10
    lon1 = lon-5
    lat1 = lat.sel(lat = lat1, method = 'nearest')        
    lon1 = lon.sel(lon = lon1, method = 'nearest')     
    p1 = np.array(mslp.sel(lat = lat1, lon = lon1))
    #Gridpoint 2
    lat2 = lat + 10
    lon2 = lon + 5
    lat2 = lat.sel(lat = lat2, method = 'nearest')        
    lon2 = lon.sel(lon = lon2, method = 'nearest')    
    p2 = np.array(mslp.sel(lat = lat2, lon = lon2))
    #Gridpoint 3
    lat3 = lat + 5
    lon3 = lon - 15
    lat3 = lat.sel(lat = lat3, method = 'nearest')        
    lon3 = lon.sel(lon = lon3, method = 'nearest')    
    p3 = np.array(mslp.sel(lat = lat3, lon = lon3))
    #Gridpoint 4
    lat4 = lat + 5
    lon4 = lon  -5
    lat4 = lat.sel(lat = lat4, method = 'nearest')        
    lon4 = lon.sel(lon = lon4, method = 'nearest')    
    p4 = np.array(mslp.sel(lat = lat4, lon = lon4))
    #Gridpoint 5
    lat5 = lat + 5
    lon5 = lon + 5
    lat5 = lat.sel(lat = lat5, method = 'nearest')        
    lon5 = lon.sel(lon = lon5, method = 'nearest')    
    p5 = np.array(mslp.sel(lat = lat5, lon = lon5))
    #Gridpoint 6
    lat6 = lat + 5
    lon6 = lon + 15
    lat6 = lat.sel(lat = lat6, method = 'nearest')        
    lon6 = lon.sel(lon = lon6, method = 'nearest')    
    p6 = np.array(mslp.sel(lat = lat6, lon = lon6))
    #Gridpoint 7
    lat7 = lat
    lon7 = lon - 15
    lat7 = lat.sel(lat = lat7, method = 'nearest')        
    lon7 = lon.sel(lon = lon7, method = 'nearest')    
    p7 = np.array(mslp.sel(lat = lat7, lon = lon7))
    #Gridpoint 8
    lat8 = lat
    lon8 = lon -5
    lat8 = lat.sel(lat = lat8, method = 'nearest')        
    lon8 = lon.sel(lon = lon8, method = 'nearest')    
    p8 = np.array(mslp.sel(lat = lat8, lon = lon8))
    #Gridpoint 9
    lat9 = lat
    lon9 = lon + 5
    lat9 = lat.sel(lat = lat9, method = 'nearest')        
    lon9 = lon.sel(lon = lon9, method = 'nearest')    
    p9 = np.array(mslp.sel(lat = lat9, lon = lon9))
    #Gridpoint 10
    lat10 = lat
    lon10 = lon + 15
    lat10 = lat.sel(lat = lat10, method = 'nearest')        
    lon10 = lon.sel(lon = lon10, method = 'nearest')    
    p10 = np.array(mslp.sel(lat = lat10, lon = lon10))
    #Gridpoint 11
    lat11 = lat - 5
    lon11 = lon - 15
    lat11 = lat.sel(lat = lat11, method = 'nearest')        
    lon11 = lon.sel(lon = lon11, method = 'nearest')    
    p11 = np.array(mslp.sel(lat = lat11, lon = lon11))
    #Gridpoint 12
    lat12 = lat - 5
    lon12 = lon - 5
    lat12 = lat.sel(lat = lat12, method = 'nearest')        
    lon12 = lon.sel(lon = lon12, method = 'nearest')    
    p12 = np.array(mslp.sel(lat = lat12, lon = lon12))
    #Gridpoint 13
    lat13 = lat - 5
    lon13 = lon + 5
    lat13 = lat.sel(lat = lat13, method = 'nearest')        
    lon13 = lon.sel(lon = lon13, method = 'nearest')    
    p13 = np.array(mslp.sel(lat = lat13, lon = lon13))
    #Gridpoint 14
    lat14 = lat - 5
    lon14 = lon + 15
    lat14 = lat.sel(lat = lat14, method = 'nearest')        
    lon14 = lon.sel(lon = lon14, method = 'nearest')    
    p14 = np.array(mslp.sel(lat = lat14, lon = lon14))
    #Gridpoint 15
    lat15 = lat - 10
    lon15 = lon - 5
    lat15 = lat.sel(lat = lat15, method = 'nearest')        
    lon15 = lon.sel(lon = lon15, method = 'nearest')    
    p15 = np.array(mslp.sel(lat = lat15, lon = lon15))
    #Gridpoint 16
    lat16 = lat - 10
    lon16 = lon + 5
    lat16 = lat.sel(lat = lat16, method = 'nearest')        
    lon16 = lon.sel(lon = lon16, method = 'nearest')    
    p16 = np.array(mslp.sel(lat = lat16, lon = lon16))
    return (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16)
    


def extracting_gridpoints_rean_globe(mslp, lat, lon):
    """
    This function extracts the 16 moving gridded points over the whole globe
    given a Reanalysis dataset (ERA5 or ERA20). This gridpoints are
    neccesary for the computationo of the terms
    """
    #Gridpoint 1
    lat1 = lat + 10
    lon1 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat1 = lat.sel(latitude = lat1, method = 'nearest')        
    lon1 = lon.sel(longitude = lon1, method = 'nearest')     
    p1 = np.array(mslp.sel(latitude = lat1, longitude = lon1))

    #Gridpoint 2
    lat2 = lat + 10
    lon2 = xr.where(lon>175, lon+5-360, lon+5)
    lon2 = xr.where(lon2 == 180, -180, lon2)
    lat2 = lat.sel(latitude = lat2, method = 'nearest')        
    lon2 = lon.sel(longitude = lon2, method = 'nearest')     
    p2 = np.array(mslp.sel(latitude = lat2, longitude = lon2))

    #Gridpoint 3
    lat3 = lat + 5
    lon3 = xr.where(lon<-165, 360+lon-15, lon-15)
    lat3 = lat.sel(latitude = lat3, method = 'nearest')        
    lon3 = lon.sel(longitude = lon3, method = 'nearest')     
    p3 = np.array(mslp.sel(latitude = lat3, longitude = lon3))

    #Gridpoint 4
    lat4 = lat + 5
    lon4 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat4 = lat.sel(latitude = lat4, method = 'nearest')        
    lon4 = lon.sel(longitude = lon4, method = 'nearest')     
    p4 = np.array(mslp.sel(latitude = lat4, longitude = lon4))

    #Gridpoint 5
    lat5 = lat + 5
    lon5 = xr.where(lon>175, lon+5-360, lon+5)
    lon5 = xr.where(lon5 == 180, -180, lon5)
    lat5 = lat.sel(latitude = lat5, method = 'nearest')        
    lon5 = lon.sel(longitude = lon5, method = 'nearest')     
    p5 = np.array(mslp.sel(latitude = lat5, longitude = lon5))

    #Gridpoint 6
    lat6 = lat + 5
    lon6 = xr.where(lon>165, lon+15-360,lon+15)
    lon6 = xr.where(lon6 == 180, -180, lon6)
    lat6 = lat.sel(latitude = lat6, method = 'nearest')        
    lon6 = lon.sel(longitude = lon6, method = 'nearest')     
    p6 = np.array(mslp.sel(latitude = lat6, longitude = lon6))

    #Gridpoint 7
    lat7 = lat
    lon7 = xr.where(lon<-165, 360+lon-15, lon-15)
    lat7 = lat.sel(latitude = lat7, method = 'nearest')        
    lon7 = lon.sel(longitude = lon7, method = 'nearest')     
    p7 = np.array(mslp.sel(latitude = lat7, longitude = lon7))

    #Gridpoint 8
    lat8 = lat
    lon8 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat8 = lat.sel(latitude = lat8, method = 'nearest')        
    lon8 = lon.sel(longitude = lon8, method = 'nearest')     
    p8 = np.array(mslp.sel(latitude = lat8, longitude = lon8))

    #Gridpoint 9
    lat9 = lat
    lon9 = xr.where(lon>175, lon+5-360, lon+5)
    lon9 = xr.where(lon9 == 180, -180, lon9)
    lat9 = lat.sel(latitude = lat9, method = 'nearest')        
    lon9 = lon.sel(longitude = lon9, method = 'nearest')     
    p9 = np.array(mslp.sel(latitude = lat9, longitude = lon9))

    #Gridpoint 10
    lat10 = lat
    lon10 = xr.where(lon>165, lon+15-360, lon+15)
    lon10 = xr.where(lon10 == 180, -180, lon10)
    lat10 = lat.sel(latitude = lat10, method = 'nearest')        
    lon10 = lon.sel(longitude = lon10, method = 'nearest')     
    p10 = np.array(mslp.sel(latitude = lat10, longitude = lon10))

    #Gridpoint 11
    lat11 = lat - 5
    lon11 = xr.where(lon<-165, 360+lon-15, lon-15)
    lat11 = lat.sel(latitude = lat11, method = 'nearest')        
    lon11 = lon.sel(longitude = lon11, method = 'nearest')     
    p11 = np.array(mslp.sel(latitude = lat11, longitude = lon11))

    #Gridpoint 12
    lat12 = lat - 5
    lon12 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat12 = lat.sel(latitude = lat12, method = 'nearest')        
    lon12 = lon.sel(longitude = lon12, method = 'nearest')     
    p12 = np.array(mslp.sel(latitude = lat12, longitude = lon12))

    #Gridpoint 13
    lat13 = lat - 5 
    lon13 = xr.where(lon>175, lon+5-360, lon+5)
    lon13 = xr.where(lon13 == 180, -180, lon13)
    lat13 = lat.sel(latitude = lat13, method = 'nearest')        
    lon13 = lon.sel(longitude = lon13, method = 'nearest')     
    p13 = np.array(mslp.sel(latitude = lat13, longitude = lon13))

    #Gridpoint 14
    lat14 = lat - 5
    lon14 = xr.where(lon>165, lon+15-360, lon+15)
    lon14 = xr.where(lon14 == 180, -180, lon14) 
    lat14 = lat.sel(latitude = lat14, method = 'nearest')        
    lon14 = lon.sel(longitude = lon14, method = 'nearest')     
    p14 = np.array(mslp.sel(latitude = lat14, longitude = lon14))

    #Gridpoint 15
    lat15 = lat - 10
    lon15 = xr.where(lon<-175, 360+lon-5, lon-5) 
    lat15 = lat.sel(latitude = lat15, method = 'nearest')        
    lon15 = lon.sel(longitude = lon15, method = 'nearest')     
    p15 = np.array(mslp.sel(latitude = lat15, longitude = lon15))

    #Gridpoint 16
    lat16 = lat - 10
    lon16 = xr.where(lon>175, lon+5-360, lon+5)
    lon16 = xr.where(lon16 == 180, -180, lon16)
    lat16 = lat.sel(latitude = lat16, method = 'nearest')        
    lon16 = lon.sel(longitude = lon16, method = 'nearest')     
    p16 = np.array(mslp.sel(latitude = lat16, longitude = lon16))
    
    return (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16)

def extracting_gridpoints_gcm_globe(mslp, lat, lon):
    """
    This function extracts the 16 moving gridded points over the whole globe
    given a Global Climate Model dataset. These gridpoints are
    neccesary for the computation fo the terms
    """
    #Gridpoint 1
    lat1 = lat + 10
    lon1 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat1 = lat.sel(lat = lat1, method = 'nearest')        
    lon1 = lon.sel(lon = lon1, method = 'nearest')    
    p1 = np.array(mslp.sel(lat = lat1, lon = lon1))

    #Gridpoint 2
    lat2 = lat + 10
    lon2 = xr.where(lon>175, lon+5-360, lon+5)
    lon2 = xr.where(lon2 == 180, -180, lon2)
    lat2 = lat.sel(lat = lat2, method = 'nearest')        
    lon2 = lon.sel(lon = lon2, method = 'nearest')    
    p2 = np.array(mslp.sel(lat = lat2, lon = lon2))

    #Gridpoint 3
    lat3 = lat + 5
    lon3 = xr.where(lon<-165, 360+lon-15, lon-15)
    lat3 = lat.sel(lat = lat3, method = 'nearest')        
    lon3 = lon.sel(lon = lon3, method = 'nearest')    
    p3 = np.array(mslp.sel(lat = lat3, lon = lon3))

    #Gridpoint 4
    lat4 = lat + 5
    lon4 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat4 = lat.sel(lat = lat4, method = 'nearest')        
    lon4 = lon.sel(lon = lon4, method = 'nearest')    
    p4 = np.array(mslp.sel(lat = lat4, lon = lon4))

    #Gridpoint 5
    lat5 = lat + 5
    lon5 = xr.where(lon>175, lon+5-360, lon+5)
    lon5 = xr.where(lon5 == 180, -180, lon5)
    lat5 = lat.sel(lat = lat5, method = 'nearest')        
    lon5 = lon.sel(lon = lon5, method = 'nearest')    
    p5 = np.array(mslp.sel(lat = lat5, lon = lon5))

    #Gridpoint 6
    lat6 = lat + 5
    lon6 = xr.where(lon>165, lon+15-360,lon+15)
    lon6 = xr.where(lon6 == 180, -180, lon6)
    lat6 = lat.sel(lat = lat6, method = 'nearest')        
    lon6 = lon.sel(lon = lon6, method = 'nearest')    
    p6 = np.array(mslp.sel(lat = lat6, lon = lon6))

    #Gridpoint 7
    lat7 = lat
    lon7 = xr.where(lon<-165, 360+lon-15, lon-15)
    lat7 = lat.sel(lat = lat7, method = 'nearest')        
    lon7 = lon.sel(lon = lon7, method = 'nearest')    
    p7 = np.array(mslp.sel(lat = lat7, lon = lon7))

    #Gridpoint 8
    lat8 = lat
    lon8 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat8 = lat.sel(lat = lat8, method = 'nearest')        
    lon8 = lon.sel(lon = lon8, method = 'nearest')    
    p8 = np.array(mslp.sel(lat = lat8, lon = lon8))

    #Gridpoint 9
    lat9 = lat
    lon9 = xr.where(lon>175, lon+5-360, lon+5)
    lon9 = xr.where(lon9 == 180, -180, lon9)
    lat9 = lat.sel(lat = lat9, method = 'nearest')        
    lon9 = lon.sel(lon = lon9, method = 'nearest')    
    p9 = np.array(mslp.sel(lat = lat9, lon = lon9))

    #Gridpoint 10
    lat10 = lat
    lon10 = xr.where(lon>165, lon+15-360, lon+15)
    lon10 = xr.where(lon10 == 180, -180, lon10)
    lat10 = lat.sel(lat = lat10, method = 'nearest')        
    lon10 = lon.sel(lon = lon10, method = 'nearest')    
    p10 = np.array(mslp.sel(lat = lat10, lon = lon10))

    #Gridpoint 11
    lat11 = lat - 5
    lon11 = xr.where(lon<-165, 360+lon-15, lon-15)
    lat11 = lat.sel(lat = lat11, method = 'nearest')        
    lon11 = lon.sel(lon = lon11, method = 'nearest')    
    p11 = np.array(mslp.sel(lat = lat11, lon = lon11))

    #Gridpoint 12
    lat12 = lat - 5
    lon12 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat12 = lat.sel(lat = lat12, method = 'nearest')        
    lon12 = lon.sel(lon = lon12, method = 'nearest')    
    p12 = np.array(mslp.sel(lat = lat12, lon = lon12))

    #Gridpoint 13
    lat13 = lat - 5 
    lon13 = xr.where(lon>175, lon+5-360, lon+5)
    lon13 = xr.where(lon13 == 180, -180, lon13)
    lat13 = lat.sel(lat = lat13, method = 'nearest')        
    lon13 = lon.sel(lon = lon13, method = 'nearest')    
    p13 = np.array(mslp.sel(lat = lat13, lon = lon13))

    #Gridpoint 14
    lat14 = lat - 5
    lon14 = xr.where(lon>165, lon+15-360, lon+15)
    lon14 = xr.where(lon14 == 180, -180, lon14)
    lat14 = lat.sel(lat = lat14, method = 'nearest')        
    lon14 = lon.sel(lon = lon14, method = 'nearest')    
    p14 = np.array(mslp.sel(lat = lat14, lon = lon14))

    #Gridpoint 15
    lat15 = lat - 10
    lon15 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat15 = lat.sel(lat = lat15, method = 'nearest')        
    lon15 = lon.sel(lon = lon15, method = 'nearest')    
    p15 = np.array(mslp.sel(lat = lat15, lon = lon15))

    #Gridpoint 16
    lat16 = lat - 10
    lon16 = xr.where(lon>175, lon+5-360, lon+5)
    lon16 = xr.where(lon16 == 180, -180, lon16)
    lat16 = lat.sel(lat = lat16, method = 'nearest')        
    lon16 = lon.sel(lon = lon16, method = 'nearest')    
    p16 = np.array(mslp.sel(lat = lat16, lon = lon16))
    
    return (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16)

def flows_rean(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, sc, zwa, zsc, zwb, lat, lon, time, mslp):
    """
    This function computes the indices associated with the direction and vorticity
    of geostrophic flow given a reanalyses dataset
    More info: Jones, P. D., Hulme, M., & Briffa, K. R. (1993). 
    A comparison of Lamb circulation types with an objective classification scheme.  
    International Journal of Climatology(6), 655–663. https://doi.org/10.1002/joc.3370130606
    
    The function employs as parameters: 
    - the 16 gridded points of MSLP (p1 to p16)
    - The latitude dependant constants (sc, zwa, zsc  and zwb)
    - latitude, longitude, time and MSLP data
    
    This function also makes it possible to work with a dataset with an extra
    dimension named "number" which reffers to the number of a set of an ensemble. 
    This can be used for subseasonal forecasts coming from 
    the Climate Data Store: https://cds.climate.copernicus.eu/cdsapp#!/home
    """
    #Westerly Flow
    W = ((0.5)*( p12 + p13 )) - ((0.5)*( p4 + p5 ))
    if mslp.dims[1] == 'latitude':
        W = xr.DataArray(W, 
                          coords = {'time': time, 'latitude':lat, 'longitude':lon}, 
                          dims = ['time', 'latitude', 'longitude'])
    elif mslp.dims[1] == 'number':
        W = xr.DataArray(W, 
                          coords = {'time': time, 'number':mslp.number ,'latitude':lat, 'longitude':lon}, 
                          dims = ['time','number' ,'latitude', 'longitude'])
        
    #Southerly Flow
    S = np.array(sc)*(((0.25)*(p5 + (2 * p9) + p13)) - ((0.25)*(p4 + (2 * p8) + p12)))
    if mslp.dims[1] == 'latitude':
        S = xr.DataArray(S, 
                          coords = {'time': time, 'latitude':lat, 'longitude':lon}, 
                          dims = ['time', 'latitude', 'longitude'])
    elif mslp.dims[1] == 'number':
        S = xr.DataArray(S, 
                          coords = {'time': time, 'number':mslp.number ,'latitude':lat, 'longitude':lon}, 
                          dims = ['time','number', 'latitude', 'longitude'])        
    #Resultant Flow 
    F = np.sqrt(S**2 + W**2)
    #Westerly Shear Vorticity
    ZW = (np.array(zwa)*( (0.5)*(p15 + p16) - (0.5)*(p8 + p9))) - (np.array(zwb)*((0.5)*(p8 + p9) - (0.5)*(p1 + p2)))
    if mslp.dims[1] == 'latitude':
        ZW = xr.DataArray(ZW, 
                          coords = {'time': time, 'latitude':lat, 'longitude':lon}, 
                          dims = ['time', 'latitude', 'longitude'])
    elif mslp.dims[1] == 'number':
        ZW = xr.DataArray(ZW, 
                              coords = {'time': time, 'number':mslp.number ,'latitude':lat, 'longitude':lon}, 
                              dims = ['time', 'number', 'latitude', 'longitude'])        
    #Southerly Shear Vorticity
    ZS = np.array(zsc) * ( ((0.25)*(p6 + (2 * p10) + p14)) - ((0.25)*(p5 + (2 * p9) + p13)) -((0.25)*(p4 + (2 * p8) + p12)) +((0.25)*(p3 + (2 * p7) + p11)) )
    #Total Shear Vorticity
    if mslp.dims[1] == 'latitude':    
        ZS = xr.DataArray(ZS, 
                          coords = {'time': time, 'latitude':lat, 'longitude':lon}, 
                          dims = ['time', 'latitude', 'longitude'])
    elif mslp.dims[1] == 'number':
        ZS = xr.DataArray(ZS, 
                          coords = {'time': time,'number':mslp.number ,'latitude':lat, 'longitude':lon}, 
                          dims = ['time', 'number', 'latitude', 'longitude'])
        
    Z = ZW + ZS
    return(W, S, F, ZW, ZS, Z)
    
def flows_gcm(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, sc, zwa, zsc, zwb, lat, lon, time):
    """
    This function computes the indices associated with the direction and vorticity
    of geostrophic flow given a CMIP6 Global Climate Model dataset
    More info: Jones, P. D., Hulme, M., & Briffa, K. R. (1993). 
    A comparison of Lamb circulation types with an objective classification scheme.  
    International Journal of Climatology(6), 655–663. https://doi.org/10.1002/joc.3370130606
    
    The function employs as parameters: 
    - the 16 gridded points of MSLP (p1 to p16)
    - The latitude dependant constants (sc, zwa, zsc  and zwb)
    - latitude, longitude, time and MSLP data
    """    
    W = ((0.5)*( p12 + p13 )) - ((0.5)*( p4 + p5 ))
    W = xr.DataArray(W, 
                      coords = {'time': time, 'lat':lat, 'lon':lon}, 
                      dims = ['time', 'lat', 'lon'])
    #Southerly Flow
    S = np.array(sc)*(((0.25)*(p5 + (2 * p9) + p13)) - ((0.25)*(p4 + (2 * p8) + p12)))
    S = xr.DataArray(S, 
                      coords = {'time': time, 'lat':lat, 'lon':lon}, 
                      dims = ['time', 'lat', 'lon'])
    #Resultant Flow 
    F = np.sqrt(S**2 + W**2)
    #Westerly Shear Vorticity
    ZW = (np.array(zwa)*( (0.5)*(p15 + p16) - (0.5)*(p8 + p9))) - (np.array(zwb)*((0.5)*(p8 + p9) - (0.5)*(p1 + p2)))
    ZW = xr.DataArray(ZW, 
                      coords = {'time': time, 'lat':lat, 'lon':lon}, 
                      dims = ['time', 'lat', 'lon'])
    #Southerly Shear Vorticity
    ZS = np.array(zsc) * ( ((0.25)*(p6 + (2 * p10) + p14)) - ((0.25)*(p5 + (2 * p9) + p13)) -((0.25)*(p4 + (2 * p8) + p12)) +((0.25)*(p3 + (2 * p7) + p11)) )
    #Total Shear Vorticity 
    ZS = xr.DataArray(ZS, 
                      coords = {'time': time, 'lat':lat, 'lon':lon}, 
                      dims = ['time', 'lat', 'lon'])
    Z = ZW + ZS
    return(W, S, F, ZW, ZS, Z)

