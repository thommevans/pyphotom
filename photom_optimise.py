import cPickle
from photom import photom_absolute, photom_relative
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mpl as mpl
import pdb

def Main(obj, ap_size_trials, sky_annulus_trials, sky_dannulus, datapars_gain=None, datapars_readnoise=None, datapars_exposure=None, datapars_obstime=None, datapars_airmass=None, ix_target=None, ix_comparisons=None ):
    """
    Searches over the grid spanned by ap_size_trials and sky_annulus_trials (with sky_dannulus fixed) for the combination
    that minimises the scatter in the relative photometry. Returns the full grid of scatter values.
    """
    orig_backend = plt.get_backend()
    plt.switch_backend( 'agg' )

    n_apertures = len(ap_size_trials)
    n_sky_annuli = len(sky_annulus_trials)
    scatter_array = np.zeros([n_apertures, n_sky_annuli])
    # Parameters relevant to plotting:
    colormap = mpl.cm.spectral
    colormap = plt.cm.ScalarMappable(cmap=colormap)
    colormap.set_clim(vmin=0, vmax=1)
    color_points = np.r_[0.1:0.9:1j*n_sky_annuli]
    fig = plt.figure(figsize=[15,9])
    edge_buffer = 0.1
    ax_width = 1-2*edge_buffer
    ax_height = 1-2*edge_buffer
    ax = fig.add_axes([1.*edge_buffer, 1.*edge_buffer, ax_width, ax_height])
    # Calculate the scatter in the photometry for each of the trial parameter sets:
    for i in range(n_sky_annuli):
        print '\n%s' % (50*'=')
        print '\n  Starting Sky Annulus %i of %i' % (i+1,n_sky_annuli)
        for j in range(n_apertures):
            print '\n  Starting Aperture %i of %i with %i dannulus trials' % (j+1,n_apertures,n_sky_annuli)
            print '\n     doing analysis %i of %i...\n' % (1+j+i*n_apertures, n_apertures*n_sky_annuli)
            ap_size = ap_size_trials[j]
            sky_annulus = ap_size+sky_annulus_trials[i]
            # Make sure the object is ready to take on new values:
            obj.photpars = 'custom'
            obj.fitskypars = 'custom'
            # Do the absolute photometry:
            obj.do_absphot(photpars_apertures=ap_size, fitskypars_annulus=sky_annulus, fitskypars_dannulus=sky_dannulus, datapars_gain=datapars_gain, datapars_readnoise=datapars_readnoise, datapars_exposure=datapars_exposure, datapars_obstime=datapars_obstime, datapars_airmass=datapars_airmass, make_plots=False)
            # Do the relative photometry:
            obj.do_relphot( ix_target=ix_target, ix_comparisons=ix_comparisons, make_plots=False)
            # Calculate the scatter amongst points for the night:
            scatter_array[j,i] = np.std(obj.relphot_vals)
        # Plot the output for the current trial:
        color = colormap.to_rgba(color_points[i])
        this_scatter = scatter_array[:,i]
        ax.plot(ap_size_trials, this_scatter, '-o', c=color, mfc=color, mec=color, lw=2, label='+%s' % sky_annulus_trials[i])
        ix = np.argmin(scatter_array[:,i])
        ax.axvline(ap_size_trials[ix], ls='--', c=color, lw=2)
        ax.text(ap_size_trials[ix]+0.005*(ap_size_trials.max()-ap_size_trials.min()), (0.6-i*0.1)*np.max(scatter_array), '%.2f pix' % ap_size_trials[ix], fontdict={'size':18, 'color':color})
    ax.set_ylabel('Scatter')
    ax.set_xlabel('Aperture Radius (pixels)')
    ax.legend(numpoints=2, ncol=1, title='Sky Annulus', loc='upper left')
    ax.set_title(obj.analysis_dir)
    #plt.draw()
    outfig_name = (obj.analysis_dir+'/optimise_aperture_output.png').replace('//','/')
    fig.savefig( outfig_name )
    outfile_name = str(obj.analysis_dir+'/optimise_aperture_output.pkl').replace('//','/')
    outfile_open = open(outfile_name,'w')
    cPickle.dump(scatter_array, outfile_open)
    outfile_open.close()
    print '\n\nSaving output in:\n  %s\n  %s' % ( outfile_name, outfig_name )

    plt.switch_backend( orig_backend )
    return scatter_array
    
