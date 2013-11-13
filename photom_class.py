import numpy as np
import matplotlib.pyplot as plt
import pdb
import os
import cPickle
import numpy as np
import shutil
from photom import photom_inspect, photom_reduce, photom_absolute, photom_relative, photom_checks, photom_optimise

homestr = os.path.expanduser( '~' )

class photom():
    """
    """
    def __init__(self):
        """
        Initalise a default photom object.
        """
        self.analysis_dir = ''
        self.nstars = None	       
        self.image_list = None     
        self.bias_list = None      
        self.dark_list = None      
        self.flat_list = None      
        self.ccdproc_params = 'default'
        self.master_bias = None
        self.master_dark = None
        self.master_flat = None
        self.red_image_list = None
        self.nimages_total = None
        self.nimages_good = None
        self.goodbad_flags = None  
        self.coords_input_files = None
        self.coords_input_type = None
        self.photpars = 'default'
        self.fitskypars = 'default'
        self.centerpars = 'default'
        self.datapars = 'default'
        self.dat_files = None
        self.absphot_file = None  
        self.relphot_file = None
        return None

    def set_attributes( self, analysis_dir=None, image_list=None, bias_list=None, dark_list=None, \
                        flat_list=None, ccdproc_params=None, ap_params=None, master_bias=None, \
                        master_dark=None, master_flat=None, red_image_list=None, nimages_total=None, \
                        nimages_good=None, goodbad_flags=None, nstars=None, coords_input_files=None, \
                        coords_input_type=None, photpars=None, fitskypars=None, centerpars=None, \
                        datapars=None, dat_files=None, absphot_file=None, relphot_file=None ):
        """
        Set photom object parameters.
        """
        if analysis_dir!=None: self.analysis_dir = analysis_dir.replace( '~', homestr )
        if self.analysis_dir=='': self.analysis_dir = os.getcwd()
        if image_list!=None:
            if (os.path.dirname(image_list)==''):
                self.image_list = str(self.analysis_dir+'/'+image_list).replace('//','/')
            else:
                self.image_list = image_list
        if red_image_list!=None:
            if (os.path.dirname(red_image_list)==''):
                self.red_image_list = str(self.analysis_dir+'/'+red_image_list).replace('//','/')
            else:
                self.red_image_list = red_image_list
        if bias_list!=None:
            if (os.path.dirname(bias_list)==''):
                self.bias_list = str(self.analysis_dir+'/'+bias_list).replace('//','/')
            else:
                self.bias_list = bias_list
        if dark_list!=None:
            if (os.path.dirname(dark_list)==''):
                self.dark_list = str(self.analysis_dir+'/'+dark_list).replace('//','/')
            else:
                self.dark_list = dark_list
        if flat_list!=None:
            if (os.path.dirname(flat_list)==''):
                self.flat_list = str(self.analysis_dir+'/'+flat_list).replace('//','/')
            else:
                self.flat_list = flat_list
        if coords_input_files!=None:
            if np.rank(coords_input_files)==0:
                self.coords_input_files = [str(self.analysis_dir+'/'+coords_input_files).replace('//','/')]
            else:
                self.coords_input_files = []
                for coords_input in coords_input_files:
                    if os.path.dirname(coords_input)=='':
                        coords_input_full = str(self.analysis_dir+'/'+coords_input).replace('//','/')
                    else:
                        coords_input_full = coords_input
                    self.coords_input_files = self.coords_input_files+[coords_input_full]
        if coords_input_type!=None: self.coords_input_type = coords_input_type
        if ccdproc_params!=None: self.ccdproc_params = ccdproc_params
        if ap_params!=None: self.ap_params = ap_params
        if master_bias!=None: self.master_bias = master_bias
        if master_dark!=None: self.master_dark = master_dark
        if master_flat!=None: self.master_flat = master_flat
        if red_image_list!=None: self.red_image_list = red_image_list
        if goodbad_flags!=None: self.goodbad_flags = goodbad_flags
        if nimages_total!=None: self.nimages_total = nimages_total
        if nimages_good!=None: self.nimages_good = nimages_good        
        if nstars!=None: self.nstars = nstars
        if photpars!=None: self.photpars = photpars
        if fitskypars!=None: self.fitskypars = fitskypars
        if centerpars!=None: self.centerpars = centerpars
        if datapars!=None: self.datapars = datapars
        if dat_files!=None: self.dat_files = dat_files
        if absphot_file!=None: self.absphot_file = absphot_file
        if relphot_file!=None: self.relphot_file = relphot_file
        self.pickle_obj()
        return None

    def inspect_images( self, obstime_kw=None, iraf_display_mode='display' ):
        """
        """
        photom_inspect.Main( self, obstime_kw=obstime_kw, iraf_display_mode=iraf_display_mode )
        self.pickle_obj()
        return None

    def reduce_images( self, use_previous=False, ccdproc_ccdtype='default', ccdproc_overscan='default', \
                       ccdproc_trim='default', ccdproc_fixpix='default', ccdproc_illumcor='default', \
                       ccdproc_fringecor='default', ccdproc_readcor='default', ccdproc_scancor='default', \
                       ccdproc_interactive='default', ccdproc_biassec='default', ccdproc_trimsec='default' ):
        """
        """
        if self.ccdproc_params=='custom':
            photom_reduce.custom_ccdproc_params( ccdproc_ccdtype=ccdproc_ccdtype, ccdproc_overscan=ccdproc_overscan, \
                                                 ccdproc_trim=ccdproc_trim, ccdproc_fixpix=ccdproc_fixpix, \
                                                 ccdproc_illumcor=ccdproc_illumcor, ccdproc_fringecor=ccdproc_fringecor, \
                                                 ccdproc_readcor=ccdproc_readcor, ccdproc_scancor=ccdproc_scancor, \
                                                 ccdproc_interactive=ccdproc_interactive, ccdproc_biassec=ccdproc_biassec, \
                                                 ccdproc_trimsec=ccdproc_trimsec )
        elif self.ccdproc_params=='default':
            photom_reduce.default_ccdproc_params(self)
        if use_previous==False:
            photom_reduce.Main(self)
        else:
            self.self_update()
        self.pickle_obj()
        return None

    def optimise_aperture( self, ap_size_trials, sky_annulus_trials, sky_dannulus, gain_kw=None, readnoise_kw=None, \
                           exptime_kw=None, obstime_kw=None, airmass_kw=None, ix_target=None, ix_comparisons=None ):
        """
        Searches a grid of aperture radii and sky annulus radii for the combination that
        minimises the scatter of the relative photometry.
        """
        scatter_array = photom_optimise.Main( self, ap_size_trials, sky_annulus_trials, sky_dannulus, datapars_gain=gain_kw, \
                                              datapars_readnoise=readnoise_kw, datapars_exposure=exptime_kw, \
                                              datapars_obstime=obstime_kw, datapars_airmass=airmass_kw, ix_target=ix_target, \
                                              ix_comparisons=ix_comparisons )
        return scatter_array

    def do_absphot( self, photpars_apertures='default', fitskypars_annulus='default', fitskypars_dannulus='default', \
                    fitskypars_salgorithm='default', centerpars_maxshift='default', centerpars_cbox='default', \
                    centerpars_minsnratio='default', datapars_gain='default', datapars_readnoise='default', \
                    datapars_exposure='default', datapars_obstime='default', datapars_airmass='default', make_plots=True ):
        """
        Does absolute photometry for one or more stars given a list of images.
        Output is generated in the form of two types of file:
          1. starX_absphot.dat for X=0,1,2,... files contain columns with the
             more detailed output for each of the stars, with each line
             corresponding to a different image.
          2. absolute.phot file containing the important numerical columns for
             each of the stars; it's supposed to be the most convenient output
             for use with numpy and for generating relative photometry.

       Summary plots are also generated by default:

        Figure 1:
          ** Top left = traces of xy drift for each of the stars
          ** Bottom left = airmass versus time
          ** Top right = absolute flux versus time for each star
          ** Bottom right = sky annulus value as a function of time for each star

        Figure 2:
          ?? Plots image number versus measured scatter divided by the calculated Poisson noise ??
        """

        if self.photpars=='custom':
            photom_absolute.custom_photpars( self, photpars_apertures=photpars_apertures )
        elif self.photpars=='default':
            photom_absolute.default_photpars( self )
        if self.fitskypars=='custom':
            photom_absolute.custom_fitskypars( self, fitskypars_annulus=fitskypars_annulus, fitskypars_dannulus=fitskypars_dannulus, \
                                               fitskypars_salgorithm=fitskypars_salgorithm )
        elif self.fitskypars=='default':
            photom_absolute.default_fitskypars( self )
        if self.centerpars=='custom':
            photom_absolute.custom_centerpars( self, centerpars_maxshift=centerpars_maxshift, centerpars_cbox=centerpars_cbox, \
                                               centerpars_minsnratio=centerpars_minsnratio )
        elif self.centerpars=='default':
            photom_absolute.default_centerpars( self )
        if self.datapars=='custom':
            photom_absolute.custom_datapars( self, datapars_gain=datapars_gain, datapars_readnoise=datapars_readnoise, \
                                             datapars_exposure=datapars_exposure, datapars_obstime=datapars_obstime, \
                                             datapars_airmass=datapars_airmass )
        elif self.datapars=='default':
            photom_absolute.default_datapars( self )
        photom_absolute.Main( self, make_plots=make_plots )
        self.pickle_obj()
        return None

    def do_relphot( self, ix_target=None, ix_comparisons=None, make_plots=True ):
        """
        Calculates relative fluxes using absolute photometry already stored in the photom object.
        Must specify indices for the target star and comparison stars to be used, using the format
        0,1,2,... etc where 0 is the first star.
        """
        photom_relative.Main( self, ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=make_plots )
        self.pickle_obj()
        return None

    def check_relphot( self ):
        """
        Does two basic checks of the relative photometry in an effort to identify
        variable comparison stars. Output is in the form of plots that must be
        visually inspected to identify variable stars.

        The two types of checks are:

          1. All possible pairs of stars that can be made up from the target
             and comparisons are checked.
          2. A leave-one-out approach is taken, where the relative photometry is
             repeated multiple times, with a different comparison star excluded
             each time. 
        """
        photom_checks.comparisons( self )
        return None

    def update_auxvars( self, headerkws=None ):
        """
        Will update the auxiliary variables within the photom object. This is done
        using the photometry already contained in the object to calculate the total
        sum of all stellar fluxes, as well as extracting header information from
        images stored in the red_images_list variable.
        """
        photom_checks.auxiliary_variables( self, headerkws=headerkws )
        return None
        
    def self_update( self ):
        """
        Routine used to generate default values for a few variables, eg. if
        a certain analysis step, such as reduce_images(), has already been
        performed and so does not need to be repeated.

        !!NOTE: This routine is currently pretty ad-hoc and could possibly do with a
        rethink plus the addition of various features that have been added to the
        overall pipeline since I first wrote this particular routine a while back.
        """
        # Count the total number of images:
        try:
            red_images = np.loadtxt(self.red_image_list, dtype='str')
            self.nimages_total = len(red_images)
        except:
            pass
        # Set the goodbad_flags to all be good:
        if self.goodbad_flags==None:
            try:
                self.goodbad_flags = np.ones(self.nimages_total)
            except:
                pass
        # Count the number of good images:
        self.nimages_good = int(np.sum(self.goodbad_flags))
        self.pickle_obj()
        return None

    def pickle_obj( self, quiet=False ):
        """
        Pickle the photom object in its current state. Saves the output as photom_object.pkl in the
        analysis directory.
        """
        outfile_name = str( self.analysis_dir + '/photom_object.pkl' ).replace( '//', '/' )
        outfile_open = open( outfile_name, 'w' )
        cPickle.dump( self, outfile_open )
        outfile_open.close()
        if quiet==False:
            print '\nSaved %s\n' % outfile_name
        self.pickled_output = outfile_name
        return None
    
    def backup_the_pickle( self ):
        """
        Makes a backup of the current photom_object.pkl, saving the backed up version as photom_object.pkl.BACKUP
        in the analysis directory.
        """
        pkl_name = str( self.analysis_dir + '/photom_object.pkl' ).replace( '//', '/' )
        shutil.copyfile( pkl_name, pkl_name + '.BACKUP' )
        print '\nBacked up pickled photom object'
        return None
