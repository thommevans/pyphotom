#!/usr/bin/python

import pyfits
from pyraf import iraf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mpl as mpl
import glob, sys, pdb, os, cPickle
from photom import photom_class, photom_inspect, photom_reduce, photom_absolute

###################################################################################################

# 1apr2012 TME:
# Edit this script each time you run a new analysis from the Python command line. I thought about
# having it run from the shell command line, but this makes interaction, examining plots etc a bit
# harder. Basically, you just need to run this script (the calls that do this are right at the bottom
# of the bottom of this file). The list of resulting photom objects will then be available within the
# environment for further analysis/interaction.

def Wrapper(ix_target=None, ix_comparisons=None):
    
    coords_input_files = ['star0_coords.init', 'star1_coords.init', 'star2_coords.init', 'star3_coords.init']

    objs = []
    make_plots = False

    if 1:
        analysis_dir = (os.getcwd()+'/20120307/HATP12/').replace('//','/')
        image_list = (analysis_dir+'/images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        obj = Main(analysis_dir, image_list, coords_input_type, coords_input_files, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
        objs = objs+[obj]

    if 0:
        analysis_dir = (os.getcwd()+'/20120308/HATP12/').replace('//','/')
        image_list = (analysis_dir+'/images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        obj = Main(analysis_dir, image_list, coords_input_type, coords_input_files, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
        objs = objs+[obj]

    if 0:
        analysis_dir = (os.getcwd()+'/20120310/HATP12/').replace('//','/')
        image_list = (analysis_dir+'/images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        obj = Main(analysis_dir, image_list, coords_input_type, coords_input_files, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
        objs = objs+[obj]

    if 0:
        analysis_dir = (os.getcwd()+'/20120312/HATP12/').replace('//','/')
        image_list = (analysis_dir+'/images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        obj = Main(analysis_dir, image_list, coords_input_type, coords_input_files, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
        objs = objs+[obj]

    if 0:
        analysis_dir = (os.getcwd()+'/20120314/HATP12/').replace('//','/')
        image_list = (analysis_dir+'/images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        obj = Main(analysis_dir, image_list, coords_input_type, coords_input_files, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
        objs = objs+[obj]

    if 1:
        analysis_dir = (os.getcwd()+'/20120317/HATP12/').replace('//','/')
        image_list = (analysis_dir+'/images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        obj = Main(analysis_dir, image_list, coords_input_type, coords_input_files, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
        objs = objs+[obj]

    if 1:
        analysis_dir = (os.getcwd()+'/20120318/HATP12/').replace('//','/')
        image_list = (analysis_dir+'/images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        obj = Main(analysis_dir, image_list, coords_input_type, coords_input_files, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
        objs = objs+[obj]

    if 1:
        analysis_dir = (os.getcwd()+'/20120320/HATP12/').replace('//','/')
        image_list = (analysis_dir+'/images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        obj = Main(analysis_dir, image_list, coords_input_type, coords_input_files, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
        objs = objs+[obj]

    if 0: # cloudy = unusable!
        analysis_dir = (os.getcwd()+'/20120322/HATP12/').replace('//','/')
        image_list = (analysis_dir+'/images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        obj = Main(analysis_dir, image_list, coords_input_type, coords_input_files, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
        objs = objs+[obj]

    if 1: 
        analysis_dir = (os.getcwd()+'/20120324/HATP12/').replace('//','/')
        image_list = (analysis_dir+'/images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        obj = Main(analysis_dir, image_list, coords_input_type, coords_input_files, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
        objs = objs+[obj]

    if 1:
        analysis_dir = (os.getcwd()+'/20120326/HATP12/').replace('//','/')
        image_list = (analysis_dir+'/images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        obj = Main(analysis_dir, image_list, coords_input_type, coords_input_files, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
        objs = objs+[obj]

    if 0: # something strange going on this night; but I haven't looked into it yet!
        analysis_dir = (os.getcwd()+'/20120328/HATP12/').replace('//','/')
        image_list = (analysis_dir+'/images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        obj = Main(analysis_dir, image_list, coords_input_type, coords_input_files, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
        objs = objs+[obj]

    if 1:
        analysis_dir = (os.getcwd()+'/20120330/HATP12/').replace('//','/')
        image_list = (analysis_dir+'/images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        obj = Main(analysis_dir, image_list, coords_input_type, coords_input_files, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
        objs = objs+[obj]


    return objs


def Main(analysis_dir, image_list, coords_input_type, coords_input_files, flat_list=None, dark_list=None, bias_list=None, ix_target=None, ix_comparisons=None, goodbad_flags=None, make_plots=True):

    # Specify whether various iraf routines will use default
    # or custom settings:
    ccdproc_params = 'default'
    photpars = 'custom'
    fitskypars = 'custom'
    centerpars = 'default'
    datapars = 'custom'

    # Header keywords to be used for iraf.phot output:
    obstime_kw = 'MJD'
    exptime_kw = 'EXPTIME'
    airmass_kw = 'AIRMASS'
    gain_kw = 'GAIN'
    readnoise_kw = 'READNOIS'

    # If starting from scratch, make the photom object:
    if 1:
        obj = initialise(analysis_dir, image_list, bias_list, dark_list, flat_list, ccdproc_params, photpars, fitskypars, centerpars, datapars, coords_input_files, coords_input_type)
    # Otherwise, read the photom object from a previous analysis:
    else:
        prev = open((analysis_dir+'/photom_object.pkl').replace('//','/'),'r')
        obj = cPickle.load(prev)
        prev.close()
    
    # Inspect the images:
    if 0:
        obj.inspect_images(obstime_kw=obstime_kw, iraf_display_mode='display')
        #obj.inspect_images(obstime_kw=obstime_kw, iraf_display_mode='imexam')

    # Perform the basic calibrations:
    if 0:
        # If flat fielding, dark-bias subtraction needs to be done:
        obj.reduce_images(use_previous=False)
    else:
        # If the images have already been reduced:
        obj.red_image_list = str(obj.analysis_dir+'/red_'+os.path.basename(obj.image_list)).replace('//','/')
        obj.reduce_images(use_previous=True)
    
    # If we have been provided with bad frame flags, update the photom object:
    if goodbad_flags!=None:
        obj.goodbad_flags = goodbad_flags
    # Add any other bad frame flags if necessary:
    if 0:
        #import random
        #ixs_random = np.array(random.sample(np.arange(10), 6))
        #obj.goodbad_flags[ixs_random] = 0
        #obj.goodbad_flags[ixs_random+22] = 0
        obj.goodbad_flags[2] = 0
        obj.goodbad_flags[6:] = 0
        #obj.goodbad_flags[25:] = 0
        

    # Assuming we have identified the optimal aperture size, do the absolute photometry:
    if 1:
        ap_size_opt = 8
        sky_annulus_opt = 20.0
        sky_dannulus_opt = 10
        obj.do_absphot(photpars_apertures=ap_size_opt, fitskypars_annulus=sky_annulus_opt, fitskypars_dannulus=sky_dannulus_opt, datapars_gain=gain_kw, datapars_readnoise=readnoise_kw, datapars_exposure=exptime_kw, datapars_obstime=obstime_kw, datapars_airmass=airmass_kw, make_plots=make_plots)

    # Assuming we have done the absolute photometry, do the relative photometry for the frames
    # taken on the current night:
    if 1:
        obj.do_relphot(ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots)
    # Check the effect of each comparison star on the photometry:
    if 0:
        obj.check_relphot()

    return obj


def initialise(analysis_dir, image_list, bias_list, dark_list, flat_list, ccdproc_params, photpars, fitskypars, centerpars, datapars, coords_input_files, coords_input_type):
    obj = photom_class.photom()
    obj.set_attributes(analysis_dir=analysis_dir, image_list=image_list, bias_list=bias_list, dark_list=dark_list, flat_list=flat_list, ccdproc_params=ccdproc_params, photpars=photpars, fitskypars=fitskypars, centerpars=centerpars, datapars=datapars, coords_input_files=coords_input_files, coords_input_type=coords_input_type)
    return obj

ix_target = np.array([0])
ix_comparisons = np.array([1,2,3])
objs = Wrapper(ix_target=ix_target, ix_comparisons=ix_comparisons)

