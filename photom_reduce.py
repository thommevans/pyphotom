import pdb
import os
from pyraf import iraf
import numpy as np
import pyfits

iraf.imred()
iraf.ccdred()
homestr = os.path.expanduser('~')

def Main(obj):
    """
    Takes raw data and calibration files (i.e. biases, darks and flats), and performs basic data reduction using the
    iraf.ccdproc routine. This is done by first constructing master calibration files and then pointing the iraf.ccdproc
    to them. Note that it is possible to use any subset of {bias, dark, flat} for the calibration (eg. if one is missing).
    Also, default values for the iraf.ccdproc settings are used unless different values are explicitly specified.
    """
    # First, make the master calibration files:
    print '\nGenerating master calibration images...'
    if (obj.bias_list!=None):
        make_master(obj, file_type='bias')
    else:
        obj.master_bias = None
    if (obj.dark_list!=None):
        make_master(obj, file_type='dark')
    else:
        obj.master_dark = None
    if (obj.flat_list!=None):
        make_master(obj, file_type='flat')
    else:
        obj.master_flat = None
    print '    Done.'
    # Second, use the master calibration files to reduce the images:
    reduce_data(obj)
    # Finally, return to the original analysis directory:
    os.chdir(obj.analysis_dir.replace('~',homestr))
    return None

def reduce_data(obj):
    """
    Once the master calibration files (i.e. bias, dark, flat) have been created, this routine sets the iraf.ccdproc
    parameters to the appropriate values and performs the calibration of the images, with the output saved as new images
    with the same name as the raw images plus a 'red_' prefix. Also created are:
      (1) a calibration_summary.txt file giving the full paths to the master calibration files used
      (2) a red_images.list file containing the names of all the calibrated images.
    """
    summary_filename = 'calibration_summary.txt'
    sfile = open(str(obj.analysis_dir+'/'+summary_filename).replace('//','/'),'w')
    print '\nReducing the raw images:'
    # Read in the names of the raw images to be reduced:
    raw_images = np.loadtxt(obj.image_list, dtype='str')
    # Specify the name of the file to contain the list of reduced images:
    obj.red_image_list = str(obj.analysis_dir+'/red_'+os.path.basename(obj.image_list)).replace('//','/')
    # Open the reduced image list file to write to it:
    outfile = open(obj.red_image_list,'w')
    # Set the iraf.ccdproc parameters:
    set_iraf_params(obj)
    if obj.master_bias==None:
        iraf.ccdproc.zerocor = 'no'
        print '  Bias correction = No'
        sfile.write('Master BIAS used = None applied\n')
    else:
        iraf.ccdproc.zerocor = 'yes'        
        iraf.ccdproc.zero = obj.master_bias
        print '  Bias correction = Yes'        
        sfile.write('Master BIAS used = %s\n' % obj.master_bias)
    if obj.master_dark==None:
        iraf.ccdproc.darkcor = 'no'
        print '  Dark correction = No'
        sfile.write('Master DARK used = None applied\n')
    else:
        iraf.ccdproc.darkcor = 'yes'            
        iraf.ccdproc.dark = obj.master_dark
        print '  Dark correction = Yes'                
        sfile.write('Master DARK used = %s\n' % obj.master_dark)
    if obj.master_flat==None:
        iraf.ccdproc.flatcor = 'no'
        print '  Flat correction = No'        
        sfile.write('Master FLAT used = None applied\n')
    else:
        iraf.ccdproc.flatcor = 'yes'            
        iraf.ccdproc.flat = obj.master_flat
        print '  Flat correction = Yes'                
        sfile.write('Master FLAT used = %s\n' % obj.master_flat)
    print ''
    counter=1
    obj.nimages_total = len(raw_images)
    for raw_image in raw_images:
        image_dir = os.path.dirname(raw_image)
        image_file = os.path.basename(raw_image)
        print 'Reducing image %i of %i' % (counter,len(raw_images))
        red_image = str(image_dir+'/red_'+image_file).replace('//','/')
        if os.path.exists(red_image): os.remove(red_image)
        iraf.ccdproc(raw_image, output=red_image)
        if os.path.exists(red_image)==False:
            print '   ... output not generated for some reason!'
        outfile.write(red_image+'\n')
        counter+=1
    outfile.close()
    print 'Successfully calibrated images!'
    print '\nList of calibrated images saved in data directory as:'
    print '  %s in data directory' % obj.red_image_list
    print 'Summary of calibration files used saved in:\n %s' % summary_filename
    sfile.close()
    # Lastly, generate a good-bad flag array for the images, setting them all to
    # 'good' (i.e. 1) to start with; this can be edited manually later on using
    # the set_attributes() routine:
    obj.goodbad_flags = np.ones(len(raw_images))
    return None

def make_master(obj, file_type=None):
    """
    This routine takes the name of a file containing the raw calibration images in the **current** directory that are to
    be combined to form a master calibration image. The type of calibration images (i.e. bias, dark or flat) is specified
    by the file_type keyword; this is necessary because the type of calibration image determines how the multiple raw
    calibration images are to be combined (eg. pixel averages vs medians).
    """
    # Get the name of the master calibration file:
    if file_type=='bias':
        list_file = obj.bias_list
    elif file_type=='dark':
        list_file = obj.dark_list
    elif file_type=='flat':
        list_file = obj.flat_list
    dirpath = os.path.dirname(list_file)+'/'
    filename = 'master_'+file_type+'.fits'
    master_filename = dirpath+filename
    if os.path.exists(master_filename): os.remove(master_filename)
    # Now make the master calibration file:
    if file_type=='bias':
        iraf.zerocombine(input='@'+list_file, output=master_filename, combine='average', ccdtype='', process='no', delete='no')
        obj.master_bias = master_filename
    elif file_type=='dark':
        iraf.darkcombine(input='@'+list_file, output=master_filename, combine='average', ccdtype='', process='no', delete='no')
        obj.master_dark = master_filename
    elif file_type=='flat':
        iraf.flatcombine(input='@'+list_file, output=master_filename, combine='median', ccdtype='', process='no', delete='no')
        obj.master_flat = master_filename
    return None

def set_iraf_params(obj):
    """
    Set various iraf routine parameters using values stored in the photom object.
    """
    iraf.unlearn('ccdproc')
    iraf.ccdproc.ccdtype = obj.ccdproc_params['ccdtype']
    iraf.ccdproc.overscan = obj.ccdproc_params['overscan']
    iraf.ccdproc.trim = obj.ccdproc_params['trim']
    iraf.ccdproc.fixpix = obj.ccdproc_params['fixpix']
    iraf.ccdproc.illumcor = obj.ccdproc_params['illumcor']
    iraf.ccdproc.fringecor = obj.ccdproc_params['fringecor']
    iraf.ccdproc.readcor = obj.ccdproc_params['readcor']
    iraf.ccdproc.scancor = obj.ccdproc_params['scancor']
    iraf.ccdproc.interactive = obj.ccdproc_params['interactive']    
    iraf.ccdproc.biassec = obj.ccdproc_params['biassec']    
    iraf.ccdproc.trimsec = obj.ccdproc_params['trimsec']    
    return None

def default_ccdproc_params(obj):
    """
    Returns a dictionary containing the default parameter settings for the iraf.ccdproc routine.
    """
    obj.ccdproc_params = {}
    obj.ccdproc_params['ccdtype'] = ''
    obj.ccdproc_params['overscan'] = 'no'
    obj.ccdproc_params['trim'] = 'no'
    obj.ccdproc_params['fixpix'] = 'no'
    obj.ccdproc_params['illumcor'] = 'no'
    obj.ccdproc_params['fringecor'] = 'no'
    obj.ccdproc_params['readcor'] = 'no'
    obj.ccdproc_params['scancor'] = 'no'
    obj.ccdproc_params['interactive'] = 'no'   
    obj.ccdproc_params['biassec'] = ''
    obj.ccdproc_params['trimsec'] = ''
    return None

def custom_ccdproc_params(obj, ccdproc_ccdtype='default', ccdproc_overscan='default', ccdproc_trim='default', ccdproc_fixpix='default', ccdproc_illumcor='default', ccdproc_fringecor='default', ccdproc_readcor='default', ccdproc_scancor='default', ccdproc_interactive='default', ccdproc_biassec='default', ccdproc_trimsec='default'):
    """
    Allows custom values for one or more of the parameters used by the iraf.ccdproc routine to be specified.
    """
    obj.ccdproc_params = default_ccdproc_params(obj)
    if ccdproc_ccdtype!='default': obj.ccdproc_params['ccdtype'] = ccdproc_ccdtype
    if ccdproc_overscan!='default': obj.ccdproc_params['overscan'] = ccdproc_overscan
    if ccdproc_trim!='default': obj.ccdproc_params['trim'] = ccdproc_trim
    if ccdproc_fixpix!='default': obj.ccdproc_params['fixpix'] = ccdproc_fixpix
    if ccdproc_illumcor!='default': obj.ccdproc_params['illumcor'] = ccdproc_illumcor
    if ccdproc_fringecor!='default': obj.ccdproc_params['fringecor'] = ccdproc_fringecor
    if ccdproc_readcor!='default': obj.ccdproc_params['readcor'] = ccdproc_readcor
    if ccdproc_scancor!='default': obj.ccdproc_params['scancor'] = ccdproc_scancor
    if ccdproc_interactive!='default': obj.ccdproc_params['interactive'] = ccdproc_interactive
    if ccdproc_biassec!='default': obj.ccdproc_params['biassec'] = ccdproc_biassec
    if ccdproc_trimsec!='default': obj.ccdproc_params['trimsec'] = ccdproc_trimsec
    return None
