import pdb
import os
import numpy as np
from photom import photom_class

# TME 1apr2012: The idea of this script is to copy it into the analysis directory for a specific
# dataset and tweak it there accordingly. For instance, in the Main() function, you can edit the
# grid of aperture and sky annulus radii over which the search is performed, and you can also alter
# the header keywords for the gain, exposure time etc. With the Main() function set up, you can
# then completely alter the content of the Wrapper() function so that you target the optimisation
# for the desired nights. In practice, a Wrapper() command at the end of this script then allows
# it to be run from the Python command line with "run script_optap.py" if desired.

def Wrapper():
    """
    This wrapper passes into the Main() function, which searches over a grid of
    aperture and sky annulus radii for the combination that optimises the scatter
    of the photometry between frames.
    """
    
    if 1:
        analysis_dir = (os.getcwd()+'/20120317/HATP12/').replace('//','/')
        red_image_list = (analysis_dir+'/red_images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        coords_input_files = ['star0_coords.init', 'star1_coords.init', 'star2_coords.init', 'star3_coords.init']
        Main(analysis_dir, red_image_list, coords_input_type, coords_input_files)

    if 1:
        analysis_dir = (os.getcwd()+'/20120318/HATP12/').replace('//','/')
        red_image_list = (analysis_dir+'/red_images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        coords_input_files = ['star0_coords.init', 'star1_coords.init', 'star2_coords.init', 'star3_coords.init']
        Main(analysis_dir, red_image_list, coords_input_type, coords_input_files)

    if 0:
        analysis_dir = (os.getcwd()+'/20120320/HATP12/').replace('//','/')
        red_image_list = (analysis_dir+'/red_images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        coords_input_files = ['star0_coords.init', 'star1_coords.init', 'star2_coords.init', 'star3_coords.init']
        Main(analysis_dir, red_image_list, coords_input_type, coords_input_files)

    if 0: 
        analysis_dir = (os.getcwd()+'/20120322/HATP12/').replace('//','/')
        red_image_list = (analysis_dir+'/red_images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        coords_input_files = ['star0_coords.init', 'star1_coords.init', 'star2_coords.init', 'star3_coords.init']
        Main(analysis_dir, red_image_list, coords_input_type, coords_input_files)

    if 0:
        analysis_dir = (os.getcwd()+'/20120324/HATP12/').replace('//','/')
        red_image_list = (analysis_dir+'/red_images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        coords_input_files = ['star0_coords.init', 'star1_coords.init', 'star2_coords.init', 'star3_coords.init']
        Main(analysis_dir, red_image_list, coords_input_type, coords_input_files)

    if 1:
        analysis_dir = (os.getcwd()+'/20120326/HATP12/').replace('//','/')
        red_image_list = (analysis_dir+'/red_images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        coords_input_files = ['star0_coords.init', 'star1_coords.init', 'star2_coords.init', 'star3_coords.init']
        Main(analysis_dir, red_image_list, coords_input_type, coords_input_files)

    if 0:
        analysis_dir = (os.getcwd()+'/20120328/HATP12/').replace('//','/')
        red_image_list = (analysis_dir+'/red_images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        coords_input_files = ['star0_coords.init', 'star1_coords.init', 'star2_coords.init', 'star3_coords.init']
        Main(analysis_dir, red_image_list, coords_input_type, coords_input_files)

    if 0:
        analysis_dir = (os.getcwd()+'/20120330/HATP12/').replace('//','/')
        red_image_list = (analysis_dir+'/red_images_hatp12.list').replace('//','/')
        coords_input_type = 'init'
        coords_input_files = ['star0_coords.init', 'star1_coords.init', 'star2_coords.init', 'star3_coords.init']
        Main(analysis_dir, red_image_list, coords_input_type, coords_input_files)



def Main(analysis_dir, red_image_list, coords_input_type, coords_input_files, flat_list=None, dark_list=None, bias_list=None):
    """
    This is where the optimisation actually gets done. Any parameters defined in here should be
    common to all of the nights and all of the targets (i.e. common to the overall data set).
    """

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

    # Generate photom object:
    obj = photom_class.photom()
    obj.set_attributes(analysis_dir=analysis_dir, red_image_list=red_image_list, bias_list=bias_list, dark_list=dark_list, flat_list=flat_list, ccdproc_params=ccdproc_params, photpars=photpars, fitskypars=fitskypars, centerpars=centerpars, datapars=datapars, coords_input_files=coords_input_files, coords_input_type=coords_input_type)

    # Explore a grid of aperture and sky annulus sizes:
    ap_sizes_trials = np.r_[3:20:1j*30]
    sky_annuli_trials = np.array([5,10,20]) # NOTE: this is defined as the number of pixels BEYOND the outer edge of the aperture!!
    sky_dannulus = 10
    scatter_array = obj.optimise_aperture(ap_sizes_trials, sky_annuli_trials, sky_dannulus, gain_kw=gain_kw, readnoise_kw=readnoise_kw, exptime_kw=exptime_kw, obstime_kw=obstime_kw, airmass_kw=airmass_kw)
    
    return None

# Comment this out unless you want the Wrapper() call made automatically:
Wrapper()
