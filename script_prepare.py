#!/usr/bin/python

# TME 7jun2012: This script should be copied to an analysis directory and edited slightly
# as appropriate for the given data set. It can then either be run from the shell command
# line using:
#
#         >> python script_prepare.py
#
# or alternatively, you can run it from within an ipython session using:
#
#         >> %run script_prepare.py
#
# Once you've run this script, you'll have all the image lists that are needed for the
# next steps, eg. find_wcs.py.

import numpy as np
import sys, os, glob, pdb, shutil
import pyfits
from pyraf import iraf

ddir = '/Volumes/Data/evanst/data/liverpool/rise/hst_support'
adir = '~/analysis/liverpool/rise/hst_support'
flat_dir = None
bias_dir = None
dark_dir = None

if 0:
    dates = [20120324]
elif 1:
    dates = 'all'


# Below here should be automatic:

if dates=='all':
    ddirs_full = glob.glob( '%s/2*_1' % ddir )
else:
    ddirs_full = []
    for date in dates:
        ddir_full = '%s/%s_1' % ( ddir, date )
        ddir_full = ddir_full.replace( '~', os.path.expanduser('~') )
        ddir_full = ddir_full.replace( '//', '/' )
        ddirs_full += [ ddir_full ]
    
date_strs = []
adirs_full = []
for i in range(len(ddirs_full)):
    date_strs += [os.path.basename( ddirs_full[i] )[:8]]
    adir_full = '%s/%s' % (adir, date_strs[i] )
    adir_full = adir_full.replace( '~', os.path.expanduser('~') )
    adir_full = adir_full.replace( '//', '/' )
    if os.path.isdir( adir_full )==False:
        os.makedirs( adir_full )
    adirs_full += [adir_full]


nddirs = len( ddirs_full )

for i in range(nddirs):

    ddir_i = ddirs_full[i]
    adir_i = adirs_full[i]

    if os.path.isdir( ddir_i )==True:
        search_str = '%s/q_e_%s_*.fits' % ( ddir_i, date_strs[i] )
        files = np.array( glob.glob( search_str ), dtype=str )
        nfiles = len(files)
        if nfiles>0:
            print '\nDATA DIRECTORY:\n  '+ddir_i

            objects = []
            datamins = np.zeros(nfiles)
            datamaxs = np.zeros(nfiles)
            exptimes = np.zeros(nfiles)
            exptotals = np.zeros(nfiles)
            airmasses = np.zeros(nfiles)
            backgrds = np.zeros(nfiles)
            stddevs = np.zeros(nfiles)
            humids = np.zeros(nfiles)
            seeing = np.zeros(nfiles)
            windspeeds = np.zeros(nfiles)
            exttemps = np.zeros(nfiles)
            rotangles = np.zeros(nfiles)
            mjds = np.zeros(nfiles)
            for j in range(nfiles):
                h = pyfits.getheader(files[j])
                objects = objects+[h['OBJECT']]
                try:
                    datamins[j] = h['DATAMIN']
                except:
                    iraf.minmax(files[j],verbose='no')
                    datamins[j] = iraf.minmax.minval
                try:
                    datamaxs[j] = h['DATAMAX']
                except:
                    iraf.minmax(files[j],verbose='no')
                    datamaxs[j] = iraf.minmax.maxval
                exptimes[j] = h['EXPTIME']
                exptotals[j] = h['EXPTOTAL']
                airmasses[j] = h['AIRMASS']
                backgrds[j] = h['BACKGRD']
                stddevs[j] = h['STDDEV']
                humids[j] = h['WMSHUMID']
                exttemps[j] = h['WMSTEMP']-273.15
                windspeeds[j] = h['WINDSPEE']
                rotangles[j] = h['ROTSKYPA']
                seeing[j] = h['SEEING']
                mjds[j] = h['MJD']
            # Rearrange everything into time order:
            ixs = np.argsort(mjds)
            mjds = mjds[ixs]
            files = files[ixs]
            objects = np.array(objects, dtype=str)[ixs]
            datamins = datamins[ixs]
            datamaxs = datamaxs[ixs]        
            exptimes = exptimes[ixs]
            exptotals = exptotals[ixs]
            airmasses = airmasses[ixs]
            backgrds = backgrds[ixs]
            stddevs = stddevs[ixs]
            humids = humids[ixs]
            exttemps = exttemps[ixs]
            windspeeds = windspeeds[ixs]
            rotangles = rotangles[ixs]
            seeing = seeing[ixs]
            # Split between different objects and print information to screen:
            objects = np.array(objects,dtype=str)
            unique_objects = np.unique(objects)
            nobjects = len(unique_objects)
            for j in range(nobjects):
                ixs = (objects==unique_objects[j])
                print '\n\nOBJECT = %s' % unique_objects[j]
                print '        datamin range = %.2f ... %.2f (counts)' % (min(datamins[ixs]), max(datamins[ixs]))
                print '        datamax range = %.2f ... %.2f (counts)' % (min(datamaxs[ixs]), max(datamaxs[ixs]))
                print '  datamax median/mean = %.2f ... %.2f (counts)' % (np.median(datamaxs[ixs]), np.mean(datamaxs[ixs]))    
                print '           sky value  = %.2f ... %.2f (counts)' % (np.median(backgrds[ixs]), np.mean(backgrds[ixs]))
                print '           sky stdv   = %.2f ... %.2f (counts)' % (np.median(stddevs[ixs]), np.mean(stddevs[ixs]))
                print '           exptime    = %.2f (seconds)' % (np.median(exptimes[ixs]))
                print '           nexposures = %.2f' % (np.median(exptotals[ixs]))
                print ' rot. sky pos. angle  = %.2f (degrees)' % np.median(rotangles[ixs])
                print '           airmass    = %.2f' % (np.median(airmasses[ixs]))
                print '           seeing     = %.2f' % (np.median(seeing[ixs]))
                print '           ext. temp  = %.2f (deg C)' % (np.median(exttemps[ixs]))
                print '           humidity   = %.2f (percent)' % (np.median(humids[ixs]))
                print '           windspeed  = %.2f ...  %.2f (m/s)' % (np.median(windspeeds[ixs]), np.mean(windspeeds[ixs]))
                print '\n     filename format  = %s' % (os.path.basename(files[ixs][0]))
                print '               .... --> %s' % (os.path.basename(files[ixs][-1]))
                print '              (use for make_lists.csh output key)'

                # Create a list for all the images of the current object:
                object_name = unique_objects[j].replace('-','').replace(' ','')
                analysis_subdir = str('%s/%s' % (adir_i,object_name)).replace('//','/')
                if os.path.isdir( analysis_subdir )==False:
                    os.makedirs( analysis_subdir )
                image_list_name = str('%s/images_%s.list' % (analysis_subdir,object_name)).replace('//','/')
                image_list_openfile = open( image_list_name, 'w' )
                image_files = files[ixs]

                for image_file in image_files:
                    # In general might be necessary to add some conditions here in case
                    # there are certain files we don't want to add to the image list.
                    image_list_openfile.write( '%s\n' % image_file )
                print '\nSaving %s' % image_list_name
                image_list_openfile.close()
            

                # Assume the images have already been reduced if there are no calibration files provided:
                if (flat_dir==None)*(dark_dir==None)*(bias_dir==None):
                    red_image_list_name = str('%s/red_images_%s.list' % (analysis_subdir,object_name)).replace('//','/')
                    print '\nSaving %s' % image_list_name
                    shutil.copyfile( image_list_name, red_image_list_name )

                # Make the flats list:
                if flat_dir!=None:
                    flat_list_name = str('%s/flats_%s.list' % (adir_i,object_name)).replace('//','/')
                    flat_list_openfile = open( flat_list_name, 'w' )
                    # Insert code for identifying flat files here.
                    flat_file_names = ['filler']
                    for flat_file in flat_files:
                        flat_list_openfile.write(* '%s\n' % flat_file )
                    print '\nSaving %s' % flat_list_name
                    flat_list_openfile.close()
                # Make the darks list:
                if dark_dir!=None:
                    dark_list_name = str('%s/darks_%s.list' % (adir_i,object_name)).replace('//','/')
                    dark_list_openfile = open( dark_list_name, 'w' )
                    # Insert code for identifying dark files here.
                    dark_files = ['filler']
                    for dark_file in dark_files:
                        dark_list_openfile.write(* '%s\n' % dark_file )
                    print '\nSaving %s' % dark_list_name
                    dark_list_openfile.close()
                # Make the biases list:
                if bias_dir!=None:
                    bias_list_name = str('%s/biass_%s.list' % (adir_i,object_name)).replace('//','/')
                    bias_list_openfile = open( bias_list_name, 'w' )
                    # Insert code for identifying bias files here.
                    bias_files = ['filler']
                    for bias_file in bias_files:
                        bias_list_openfile.write(* '%s\n' % bias_file )
                    print '\nSaving %s' % bias_list_name
                    bias_list_openfile.close()

            # Record the fact that we found some images in this folder:
            # Create a new file that will record where the various image, bias, flat etc directories are:
            data_locations =  '%s/data_locations.txt' % adir_i
            data_locations_openfile = open( data_locations, 'w' )
            data_locations_openfile.write( 'image_dir = %s \n' % ddir_i )
            data_locations_openfile.write( 'flat_dir  = %s \n' % flat_dir)
            data_locations_openfile.write( 'dark_dir  = %s \n' % dark_dir )
            data_locations_openfile.write( 'bias_dir  = %s \n' % bias_dir )            
            data_locations_openfile.close()
            print '\nSaving %s' % data_locations

        else:
            print '\nData directory exists but is empty'
    else:
        print '\nNo such directory:\n %s' % ddir_i

