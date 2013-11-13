import os#
import pdb
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker

################################################################################################################
#   Relative photometry:
#   
#   Often referred to as differential photometry when dealing with magnitudes instead of flux counts, but I find
#   it more natural to talk in terms of relative fluxes (it's all the same thing).
#   
#   Suppose you measure fluxes for 3 comparison stars:
#   
#     F1(t) = k(t) * f1
#     F2(t) = k(t) * f2
#     F3(t) = k(t) * f3
#   
#   where the uppercase F's indicate the measured values and the lower case f's indicate the true values, which
#   we assume are constant. Meanwhile, the k(t) term is the time-variable effects that affect all of the stars
#   on the chip proportionally (eg. cloud). Denote the sum of these fluxes as:
#   
#     S123(t) = F1(t) + F2(t) + F3(t) = k(t) * ( f1 + f2 + f3 ) = k(t) * C
#   
#   where C is a constant (i.e. the sum of the constant underlying fluxes).
#   
#   We also measure the target flux as:
#   
#     G(t) = k(t) * g(t)
#   
#   where we are trying to monitor the time-dependence of the target brightness. In order to do this, we need to
#   disentangle it from the time dependence of the k(t) term, which we can do in theory by dividing by the comparison
#   flux sum:
#   
#     H(t) = G(t) / S123(t) = k(t) * g(t) / k(t) / C = g(t) / C
#   
#   This is the signal we're after (i.e. g(t)) times a constant scaling factor (i.e. C). The latter is irrelevant,
#   if we express the result as differential fluxes about the mean or median:
#   
#     D(t) = H(t) - median[ H(t) ]
#   
#   and then normalise to the mean/median:
#   
#     D'(t) = D(t) / median[ H(t) ] = H(t) / median[ H(t) ] - 1
#   
#   leaving us with differential fluxes about the median/mean, expressed as fractions of the median/mean.
#   
################################################################################################################

def Main( obj, ix_target=None, ix_comparisons=None, make_plots=True ):
    """
    Calculates relative fluxes using absolute photometry already stored in the photom object.
    """

    if ( ix_target==None )+( ix_comparisons==None ):
        print '\nAssuming first star is target and rest are comparisons...\n'
        ix_target = np.array( 0 )
        ix_comparisons = np.arange( 1, obj.nstars )
    obj.ix_target = ix_target
    obj.ix_comparisons = ix_comparisons
    absphot_vals_target = obj.absphot_vals_all[ :, np.array( ix_target ) ]
    absphot_errs_target = obj.absphot_errs_all[ :, np.array( ix_target ) ]
    absphot_vals_comparisons = obj.absphot_vals_all[ :, np.array( ix_comparisons ) ]
    absphot_errs_comparisons = obj.absphot_errs_all[ :, np.array( ix_comparisons ) ]
    relphot_vals, relphot_errs = calc( absphot_vals_target, absphot_errs_target, absphot_vals_comparisons, \
                                       absphot_errs_comparisons )
    # Update the photom object:
    obj.relphot_vals = relphot_vals
    obj.relphot_errs = relphot_errs
    if make_plots==True:
        plot( obj )
        
    return None

def calc( absphot_vals_target, absphot_errs_target, absphot_vals_comparisons, absphot_errs_comparisons ):
    """
    Calculates relative fluxes given target and comparison flux time values. Also calculates the
    propagated formal uncertainty using the formal errors on each of the flux values.

    The required inputs are:
      ** absphot_vals_target - N-length np.array containing the absolute fluxes of the target star.
      ** absphot_errs_target - N-length np.array containing the error bars on the absolute fluxes of
         the target star.
      ** absphot_vals_comparisons - NxM np.array containing the absolute fluxes of M comparison stars.
      ** absphot_errs_comparisons - NxM np.array containing the error bars on the absolute fluxes of
         M comparison stars.

    All error calculation is done using standard uncertainty propagation assuming independence
    between points and quadrature sums.

    The function is defined in this way so that it's possible to have more flexibility in
    experimenting with different combinations of comparison stars elsewhere (eg. in other routines)
    if necessary.
    """
    
    # If there's only one comparison, just make sure everything is in the correct format:
    if ( np.rank( absphot_vals_comparisons )==1 ):
        absphot_vals_comparisons = np.reshape( absphot_vals_comparisons, [ len( absphot_vals_comparisons ), 1 ] )
    if ( np.rank( absphot_errs_comparisons )==1 ):
        absphot_errs_comparisons = np.reshape( absphot_errs_comparisons, [ len( absphot_errs_comparisons ), 1 ] )
    comparisons_sum_vals = np.sum( absphot_vals_comparisons, axis=1 )
    comparisons_sum_errs_sq = np.sum( absphot_errs_comparisons**2., axis=1 )
    comparisons_sum_errs = np.sqrt( comparisons_sum_errs_sq )
    relphot_vals = absphot_vals_target.flatten() / comparisons_sum_vals.flatten()
    relphot_errs = relphot_vals * np.sqrt( ( absphot_errs_target.flatten() / absphot_vals_target.flatten() )**2. \
                                        + ( comparisons_sum_errs.flatten() / comparisons_sum_vals.flatten() )**2. )
    return relphot_vals, relphot_errs

def plot( obj ):
    """
    Plot the relative fluxes stored in a photom object. Also plot the sky brightness and airmass so
    that any obvious correlations can be identified.
    """
    orig_backend = plt.get_backend()
    plt.switch_backend( 'agg' )

    fig1 = plt.figure( figsize=[ 12, 13 ] )
    edge_buffer = 0.08
    markersize = 5
    linewidth = 2
    ax_width = 1. - 2.*edge_buffer
    ax_height = ( 1 - 2.*edge_buffer ) / 3.
    color = 'k'
    # Plot the differential photometry in the top panel:
    ax1 = fig1.add_axes( [ edge_buffer, edge_buffer + 2*ax_height, ax_width, ax_height ] )
    ix = np.argsort( obj.obstimes )
    y = obj.relphot_vals[ ix ] / np.median( obj.relphot_vals[ ix ] ) - 1
    ye = obj.relphot_errs[ ix ] / np.median( obj.relphot_vals[ ix ] )
    ax1.errorbar( obj.obstimes[ ix ], y, yerr=ye, fmt='-o', c=color, mfc=color, mec=color, \
                  ms=markersize, lw=linewidth )
    ax1.axhline( 0, ls='--', lw=linewidth, c='b' )
    xl = obj.obstimes.min() - 0.05*( obj.obstimes.max() - obj.obstimes.min() )
    xu = obj.obstimes.max() + 0.05*( obj.obstimes.max() - obj.obstimes.min() )
    x = np.r_[ xl : xu : 1j*len( obj.obstimes[ ix ] ) ]
    ax1.fill_between( x, -np.std( y ), +np.std( y ), color=[ 0.7, 0.7, 0.7 ] )
    ax1.set_ylabel( 'Normalised Median-subtracted Flux' )
    ax1.set_title( 'Relative Photometry (errorbars = formal calculated, shaded = measured scatter)' )
    ax1.xaxis.set_major_formatter( matplotlib.ticker.OldScalarFormatter() )
    ax1.yaxis.set_major_formatter( matplotlib.ticker.OldScalarFormatter() )
    plt.setp( ax1.xaxis.get_ticklabels(), visible=False )
    # Plot the sky values in the middle panel:
    ax2 = fig1.add_axes( [ edge_buffer, edge_buffer + 1*ax_height, ax_width, ax_height ], sharex=ax1 )
    skyvals_med = np.median( obj.skyvals, axis=1 )
    skystdvs_med = np.median( obj.skystdvs, axis=1 )
    ax2.errorbar( obj.obstimes[ ix ], skyvals_med[ ix ], yerr=skystdvs_med[ ix ], fmt='-o', ecolor=color, mfc=color,\
                 mec=color, c=color, ms=markersize, lw=linewidth )
    ax2.set_ylabel( 'Sky Flux' )
    ax2.xaxis.set_major_formatter( matplotlib.ticker.OldScalarFormatter() )
    ax2.yaxis.set_major_formatter( matplotlib.ticker.OldScalarFormatter() )
    plt.setp( ax2.xaxis.get_ticklabels(), visible=False )
    # Plot the airmass in the bottom panel:
    ax3 = fig1.add_axes( [ edge_buffer, edge_buffer, ax_width, ax_height ], sharex=ax1 )
    ax3.plot( obj.obstimes[ ix ], obj.airmasses[ ix ], '-o', lw=linewidth, mfc=color, mec=color, \
              c=color, ms=markersize )
    ax3.set_ylabel( 'Airmass' )
    ax3.set_xlabel( 'Time' )
    ax3.xaxis.set_major_formatter( matplotlib.ticker.OldScalarFormatter() )
    ax3.yaxis.set_major_formatter( matplotlib.ticker.OldScalarFormatter() )
    plt.setp( ax3.xaxis.get_ticklabels(), visible=True )
    fig1.suptitle( obj.analysis_dir )
    # Make sure the x-range is nice:
    ax1.set_xlim( [ xl, xu ] )
    plt.draw()
    # Save the figure:
    figname = str( obj.analysis_dir + '/relphot_output.png' ).replace( '//', '/' )
    obj.relphot_figure = figname
    fig1.savefig( figname )

    # Temporary (tidy up later):
    fig2 = plt.figure()
    fig2.suptitle( obj.analysis_dir )
    ax = fig2.add_subplot( 111 )
    ax.plot( obj.obstimes[ ix ], np.std( y ) / ye, '-o', c=color, mfc=color, mec=color, ms=markersize, lw=linewidth )
    ax.axhline( 1 )
    ax.set_ylim( [ 0.8, 1.5 ] )

    plt.switch_backend( orig_backend )
    return None

