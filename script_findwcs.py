#!/usr/bin/python

from pyraf import iraf
import pyfits
import sys, os, glob, pdb, shutil
import numpy as np
iraf.images.imcoords()

# TME 7jun2012:
# Once you've identified the RA/Dec coordinates of the stars on the chip that you're
# interested in, if there is WCS information in the image headers, this routine script
# will then be able to convert the RA/Dec coordinates to xy-pixel coordinates for the
# first image for each object on each night. The first image is only needed because the
# photometry scripts deal with shifts in pointing between images. The script should in
# theory be able to handle cases where, say, the target wasn't on the chip for the first
# image of the night due to a pointing error, but X frames later this had been corrected,
# however, whether or not it works is something that needs to be tested still.
#
# To use the script, first edit the top bits then call it from either the shell command
# line using:
#
# >> python script_findwcs.py
#
# or from within an ipython session using:
#
# >> %run script_findwcs.py
#


# Setup up:
object_names = ['WASP12','HATP12']
star_radec_files = ['star_coords_wasp12.radec', 'star_coords_hatp12.radec']
ddir_base = '/Volumes/Data/evanst/data/liverpool/rise/hst_support'
adir_base = '~/analysis/liverpool/rise/hst_support'

# Specify the dates to be done:
if 0:
    dates = [20120406]
elif 1:
    dates = 'all'

        
def Main( object_names, star_radec_files, ddir_base, adir_base, dates ):
    """
    Using the star coordinates stored in the star_radec_file, searches the input
    image for the corresponding pixel coordinates. In particular, the input image
    is typically going to be the first image in a block, to give the IRAF routine
    an initial starting point, from which it can take over.

    For this function to work, the WCS information must be stored in the headers
    of the image being analysed.
    """
    # Make sure the RA-Dec files are where we're expecting them to be:
    adir_base = adir_base.replace( '~', os.path.expanduser('~') )

    # Find paths for the analysis directories divided between dates: 
    if dates=='all':
        ddirs_dates = glob.glob( '%s/2*_1' % ddir_base )
        adirs_dates = []
        dates = []
        for i in range(len(ddirs_dates)):
            dates += [os.path.basename( ddirs_dates[i] )[:8]]
            adir_date = '%s/%s' % (adir_base, dates[i] )
            adir_date = adir_date.replace( '//', '/' )
            if os.path.isdir( adir_date )==False:
                os.makedirs( adir_date )
            adirs_dates += [adir_date]
    else:
        ddirs_dates = []
        adirs_dates = []
        for date in dates:
            ddir_date = '%s/%s_1/' % ( ddir_base, date )
            ddir_date = ddir_date.replace( '//', '/' )
            ddirs_dates += [ ddir_date ]
            adir_date = '%s/%s' % (adir_base, date)
            adir_date = adir_date.replace('//','/')
            if os.path.isdir( adir_date )==False:
                os.makedirs( adir_date )
            adirs_dates += [adir_date]
    # Now go through each of the nights, work out which targets were observed, and
    # create the xy-coordinate files:
    nnights = len( adirs_dates )
    for i in range(nnights):

        ddir_i = ddirs_dates[i]
        adir_i = adirs_dates[i]
        print '\n%s' % ('='*50)
        print '\nDATA DIRECTORY:\n  '+ddir_i

        # Cycle through the different objects, and if one was found to be observed on
        # the current night, proceed with the analysis; note that the subfolders on a
        # given night should have been given names taken directly from the 'OBJECT' field
        # in the fits headers in the script_prepare.py step:
        nobjects = len(object_names)
        for j in range(nobjects):
            print '\n%s' % ('='*50)
            print '\nTARGET = %s (%s)\n' % (object_names[j],dates[i])
            radec_file_path = str( '%s/%s' % ( adir_base, star_radec_files[j] ) ).replace('//','/')
            if os.path.exists( radec_file_path )==False:
                pdb.set_trace()
            print ' - using RA/Dec coordinates in %s ...' % star_radec_files[j]
            adir_full = str('%s/%s' % (adir_i, object_names[j])).replace('//','/')
            coords_block = np.loadtxt(radec_file_path, dtype=str)
            star_names = coords_block[:,0]
            star_ras = coords_block[:,1]
            star_decs = coords_block[:,2]
            nstars = len(star_names)
            if nstars==0:
                pdb.set_trace() # this shouldn't happen if script_prep.py has already been run
            if os.path.isdir(adir_full)==True:
                image_list = str('%s/images_%s.list' % (adir_full,object_names[j])).replace('//','/')
                red_image_list = str('%s/red_images_%s.list' % (adir_full,object_names[j])).replace('//','/')
                try:
                    images = np.loadtxt( image_list, dtype=str )
                    red_images = np.loadtxt( red_image_list, dtype=str )
                except:
                    print '\nCreate the image lists first!'
                    pdb.set_trace()
                nimages = len(red_images)
                if nimages==0:
                    continue
                
                # Generate a list of output file names to store the pixel coordinates for each star on
                # the chip for the current target:
                star_files = []
                for star_name in star_names:
                    star_file = str('%s/%s_coords.init' % (adir_full, star_name)).replace('//','/')
                    star_files = star_files+[star_file]
                # Now that we've found the radec file, we'll go through each of the images
                # of the current object until we find one that has the target on the chip
                # (this should be the first image unless there was a pointing error):
                for k in range(nstars):
                    for l in range(nimages):
                        # Write a temporary file containing the RA/Dec coordinates of the
                        # current star, because this is how IRAF likes it:
                        radec_tempfile = str('%s/temp_coords.radec' % adir_full).replace('//','/')
                        if os.path.isdir( adir_full )==False:
                            print '\n\nGenerating directory for output:\n%s \n\n' % adir_full
                            os.makedirs( adir_full )
                        tempfile = open(radec_tempfile,'w')
                        tempfile.write('%s  %s' % (star_ras[k],star_decs[k]))
                        tempfile.close()
                        # Now use the IRAF param to locate the pixel coordinates:
                        setparams(radec_tempfile, red_images[l], star_files[k])
                        check_exists = os.path.exists( star_files[k] )
                        if check_exists==True:
                            os.remove( star_files[k] )
                        iraf.wcsctran( mode='h', verbose=0 )
                        # Always remove the temporary file before the next loop:
                        os.remove(radec_tempfile)
                        # Check to see if the star was actually found in the image, and if it
                        # was, break the loop to repeat the process for the next star:
                        h = pyfits.getheader(red_images[l])
                        naxis1 = h['NAXIS1']
                        naxis2 = h['NAXIS2']
                        xy = np.loadtxt( star_files[k] )
                        star_located = False
                        if (xy[0]>0)*(xy[0]<naxis1)*(xy[1]>0)*(xy[1]<naxis2):
                            if check_exists:
                                print '\n*Overwriting previous...'
                            print ' -->Saved: %s' % (star_files[k])
                            star_located = True
                            # In the case that the target star (i.e. k==0) was not located on the first image,
                            # create a new image list and red_image list to reflects this:
                            if (k==0)*(l>0)*(star_located==True):
                                # Have not properly tested this block yet:
                                print '\nDid not find target on first image, so updating image lists accordingly...'
                                image_list_unfiltered = str('%s/images_%s_unfiltered.list' % (adir_full,object_names[j])).replace('//','/')
                                shutil.move( image_list, image_list_unfiltered )
                                red_image_list_unfiltered = str('%s/red_images_%s_unfiltered.list' % (adir_full,object_names[j])).replace('//','/')
                                shutil.move( red_image_list, red_image_list_unfiltered )
                                np.savetxt( image_list, images[l:] )
                                np.savetxt( red_image_list, red_images[l:] )                            
                                print '  UPDATED: %s' % image_list
                                print '  UPDATED: %s\n' % red_image_list
                            break
                        # Otherwise, remove the output file that was just created by wcsctran,
                        # because it will contain nonsense, and try the next image:
                        else:
                            os.remove(star_files[k])
                            if l==nimages-1:
                                print '\n  (%s not found in any images)' % (star_names[k])
    print '\nFinished.\n'
    return None

def setparams(star_radec_file,image,outfile):
    """
    Sets the parameters of the wcsctran routine. I think the
    order in which these are set might be important (because
    I seemed to get different results depending on which order
    I used), so it's done separately here.
    """
    iraf.wcsctran.setParam('input',star_radec_file)
    iraf.wcsctran.setParam('output',outfile)
    iraf.wcsctran.setParam('image',image)
    iraf.wcsctran.setParam('inwcs','world')
    iraf.wcsctran.setParam('outwcs','logical')
    iraf.wcsctran.setParam('units','h n')
    iraf.wcsctran.setParam('columns','1 2')
    return None


Main( object_names, star_radec_files, ddir_base, adir_base, dates ) # runs the main function
