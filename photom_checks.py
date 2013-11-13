from photom import photom_relative
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker
import os
import pdb
import pyfits
import itertools


def auxiliary_variables( obj, headerkws=None ):
    """
    Extracts various auxiliary variables for each of the images contained
    within the photom object. This can include variables stored in the
    image headers if the appropriate keywords are passed via the headerkws
    optional argument. Diagnostic output plots are generated and saved in
    the analysis directory, and a dictionary containing the auxiliary variables
    is also installed into the photom object.
    TO-DO is actually add the bit that plots stuff.
    """

    auxvars = {}

    # The sum of all stellar fluxes across the image:
    totflux = np.sum( obj.absphot_vals_all, axis=1 )
    auxvars['ALLSTARSUM'] = totflux

    # Now extract any requested information from the headers:
    if headerkws!=None:
        list_file = open( obj.red_image_list, 'r' )
        list_file.seek( 0 )
        image_names = []
        for image_name in list_file:
            image_names += [ image_name ]
        nimages = len( image_names )
        if np.rank( headerkws )==0:
            headerkws = [ headerkws ]
        headers = []
        for image in image_names:
            headers += [ pyfits.getheader( image ) ]
        for kw in headerkws:
            var_arr = np.zeros( nimages )
            for i in range( nimages ):
                var_arr[i] = headers[i][kw]
            auxvars[kw] = var_arr
                
                
    obj.auxvars = auxvars
    obj.pickle_obj()

    return None


def centering( obj, plot_every=1 ):
    """
    Prints a script to screen that can then be cut-and-pasted to a separate file
    so that plots are generated in batch mode; otherwise, matplotlib insists on
    opening an X window for every plot if it has already been imported with the
    X windows backend. Hopefully this can be avoided in future.
    """

    # Because I can't work out how to change the backend from matplotlib"
    # once I've already loaded the X windows backend, just cut-and-paste"
    # the following and run it as a separate script from the command line:"
    plt.ioff()
    list_file = open( obj.red_image_list, 'r' )
    list_file.seek( 0 )
    image_names = []
    for image_name in list_file:
        image_names += [ image_name ]
    nimages = len( image_names )
    nplot = int( np.floor( nimages/float(plot_every) ) )
    nby = 4
    if nimages<nby*nby:
        plot_every = 1
    nfigs = int( np.ceil( float( nplot ) / (nby*nby) ) )
    ndigits = len( str( nimages ) )
    png_images = []
    list_file.seek( 0 )
    ebuffer = 0.05
    axsize = ( 1-ebuffer )/float( nby )
    axcounter = 1
    figno = 1
    print '\n\nGoing through each of the figures to check centering:\n'
    for i in range( nimages ):
        #if i%plot_every!=0:
        #    print 'a'
        #    continue
        image = image_names[i]
        d = pyfits.getdata( image )
        print image
        n, m = np.shape( d )
        if np.median( d.flatten() )>0:
            zerolevel = np.median( d )
        else:
            zerolevel = d[ d>0 ].min()
        d[ d<zerolevel ] = zerolevel
        if ( i+1 )%float(nby*nby)==1:
            fig = plt.figure( figsize=[ 12, 12 ] )
            axcounter = 1
        else:
            axcounter += 1
        row = np.ceil( float( axcounter ) / nby )
        col = axcounter - nby*( row - 1 )
        xlow = 0.5*ebuffer+(col-1)*axsize
        ylow = 1-0.5*ebuffer-row*axsize
        cax = fig.add_axes( [ xlow, ylow, axsize, axsize ] )
        cax.imshow( d**0.1, aspect='equal', cmap='binary' )
        plt.setp( cax.xaxis.get_ticklabels(), visible=False )
        plt.setp( cax.yaxis.get_ticklabels(), visible=False )            

        # Get the parameters that IRAF used to do the photometry:
        raperture = obj.photpars['apertures']
        rannulus1 = raperture + obj.fitskypars['annulus']
        rannulus2 = rannulus1 + obj.fitskypars['dannulus']

        # Go through the target and each of the comparisons, drawing
        # small circles at the coordinates of each star, as well as larger
        # circles showing the the photometric aperture and outer annuli
        # showing where the sky was calculated from:
        ixt = obj.ix_target
        ixcs = obj.ix_comparisons
        xt, yt = obj.xycoords[i,ixt,:].flatten()
        if ( xt > 0 ) * ( xt < m ) * ( yt > 0 ) * ( yt < n ):
            cap = plt.Circle( ( xt, yt ), radius=raperture, fc='none', ec='r', lw=1 )
            cann1 = plt.Circle( ( xt, yt ), radius=rannulus1, fc='none', ec='r', lw=1 )
            cann2 = plt.Circle( ( xt, yt ), radius=rannulus2, fc='none', ec='r', lw=1 )       
            cax.add_patch( cap )
            cax.add_patch( cann1 )
            cax.add_patch( cann2 )
        for j in range( len( ixcs ) ):
            xc, yc = obj.xycoords[i,ixcs[j],:].flatten()
            if ( xc > 0 ) * ( xc < m ) * ( yc > 0 ) * ( yc < n ):
                cap = plt.Circle( ( xc, yc ), radius=raperture, fc='none', ec='g', lw=1 )
                cann1 = plt.Circle( ( xc, yc ), radius=rannulus1, fc='none', ec='g', lw=1 )
                cann2 = plt.Circle( ( xc, yc ), radius=rannulus2, fc='none', ec='g', lw=1 )       
                cax.add_patch( cap )
                cax.add_patch( cann1 )
                cax.add_patch( cann2 )
    
        if ( axcounter==nby*nby )+( i==len(image_names)-1 ):
            if plot_every==1:
                fig.suptitle( '{0} (figure {1} of {2})'.format( os.path.dirname(image), figno, nfigs ) )
            elif plot_every==2:
                fig.suptitle( '{0} (figure {1} of {2}, plotting only every 2nd image)'.format( os.path.dirname(image), figno, nfigs ) )
            elif plot_every==3:
                fig.suptitle( '{0} (figure {1} of {2}, plotting only every 3rd image)'.format( os.path.dirname(image), figno, nfigs ) )
            else:
                fig.suptitle( '{0} (figure {1} of {2}, plotting only every {3}th image)'.format( os.path.dirname(image), figno, nfigs, plot_every ) )          
            first_image = 1 + plot_every*( figno-1 )*nby*nby
            last_image = first_image + plot_every*nby*nby - 1
            id_key = '{0}-{1}'.format( str( first_image ).zfill( ndigits ), str( last_image ).zfill( ndigits ) )
            png_name = '{0}/images_{1}.png'.format( obj.analysis_dir, id_key ).replace( '//', '/' )
            plt.draw()
            fig.savefig( png_name )
            print 'Saved {0}'.format( png_name )
            png_images += [ png_name ]
            figno += 1
    obj.image_pngs = png_images
    obj.pickle_obj()

    return None


def comparisons( obj ):
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

    Also plotted is a simple flux versus time for the target and all comparisons
    to show how the flux magnitudes compare, if there's obvious variability etc.
    """
    
    # Step 1. Check all possible combinations of pairs.
    check_pairs( obj )
    
    # Step 2. Check the derived differential flux obtained for all cases of leaving one
    # comparison out at a time.
    check_indivs( obj )

    # Step 3. Make a simple plot of flux versus time for all of the stars on the same axes.
    plot_each_fluxseries( obj )

    print '\n\nSaved png versions of the figures plotted to screen as:\n'
    for i in obj.check_pairs_relphot_figures:
        print '  {0}'.format( i )
    for i in obj.check_indivs_relphot_figures:
        print '  {0}'.format( i )
    print '  {0}'.format( obj.check_indiv_fluxseries )
    
    return None

def check_pairs( obj ):
    """
    Calculate the relative fluxes between all possible combinations of pairs. Note that all
    comparisons are included, even if they weren't used in the most recent relative photometry
    routine (i.e. even if use_comparisons!='all' in the obj.do_relphot() routine).

    Also calls plot_check_pairs_results() to generate a series of plots of starX/starY
    normalised flux as a function of time, for each pair.     
    """
    
    # Work out all possible pair combinations:
    ixs = range( obj.nstars )
    pairs = list( itertools.combinations( ixs, 2 ) )
    npairs = len( pairs )
    # Prepare variables to store the output:
    obj.check_pairs_relphot_vals = np.zeros( [ obj.nimages_good, npairs ] )
    obj.check_pairs_relphot_errs = np.zeros( [ obj.nimages_good, npairs ] )
    obj.check_pairs_ixs = []
    # Calculate the relative fluxes and variances for each pair:
    for i in range( npairs ):
        obj.check_pairs_ixs = obj.check_pairs_ixs + [ np.array( pairs[ i ] ) ]
        fluxes1 = obj.absphot_vals_all[ :, pairs[ i ][ 0 ] ]
        errs1 = obj.absphot_errs_all[ :, pairs[ i ][ 0 ] ]
        fluxes2 = obj.absphot_vals_all[ :, pairs[ i ][ 1 ] ] 
        errs2 = obj.absphot_errs_all[ :, pairs[ i ][ 1 ] ]               
        obj.check_pairs_relphot_vals[ :, i ], obj.check_pairs_relphot_errs[ :, i ] \
            = photom_relative.calc( fluxes1, errs1, fluxes2, errs2 )
    plot_check_pairs_results( obj )
    print '\n\nPairs in order:\n'
    for i in range( npairs ):
        print pairs[i]

    return None

def check_indivs( obj ):
    """
    Calculate the relative fluxes, but repeat M times where M is the number of comparison stars,
    leaving one comparison out each time to identify if any obviously degrade the results.

    Also calls plot_check_pairs_results() to generate a series of plots of starX/starY
    normalised flux as a function of time, for each pair.
    """
    
    # Prepare the variables to store the output:
    obj.check_indivs_relphot_vals = np.zeros( [ obj.nimages_good, obj.ncomparisons ] )    
    obj.check_indivs_relphot_errs = np.zeros( [ obj.nimages_good, obj.ncomparisons ] )
    # Calculate the differential fluxes for each case:
    for i in range( obj.ncomparisons ):
        # Exclude one of the comparison stars:
        ix_comparisons_i = obj.ix_comparisons[ obj.ix_comparisons!=obj.ix_comparisons[i] ]
        # Get the target flux and errors:
        fluxes1 = obj.absphot_vals_all[ :, obj.ix_target ]
        errs1 = obj.absphot_errs_all[ :, obj.ix_target ]
        fluxes2 = obj.absphot_vals_all[ :, ix_comparisons_i ]
        errs2 = obj.absphot_errs_all[ :, ix_comparisons_i ]
        #
        obj.check_indivs_relphot_vals[ :, i ], obj.check_indivs_relphot_errs[ :, i ] = \
            photom_relative.calc( fluxes1, errs1, fluxes2, errs2 )
    plot_check_indivs_results( obj )
    
    return None

def plot_check_pairs_results( obj ):
    """
    Makes two kinds of plots:

      ** Figure 1
      A plot of std( fluxA / fluxB ) where fluxA and fluxB are the absolute flux time
      series for starA and starB, as a function of the different pair combinations.
      TO-DO: Add labels that show which pair each point on the plot corresponds to.
                  
      ** Figure 2 and onwards
      Plots ( fluxA / fluxB ) versus time for each of the different star pairs, with a
      different pair in each panel. There are five panels per figure, with more
      figures being generated as needed. 
    """
    
    edge_buffer = 0.08
    markersize = 5
    linewidth = 2

    npairs = np.shape( obj.check_pairs_relphot_vals )[ 1 ]
    variances = np.std( obj.check_pairs_relphot_vals, axis=0 )
    
    # Plot the variances for each of the pairs; note that this is the variance of the
    # relative flux values over the whole night, compared between the different pairs:
    fig1 = plt.figure()
    figname1 = str( obj.analysis_dir + '/check_pairs_variances.png' ).replace( '//', '/' )
    obj.check_pairs_variances_figure = figname1
    x_lowcorner = 1.5*edge_buffer
    ax_width = 1. - 2*edge_buffer
    ax_height = 0.5*ax_width
    y_lowcorner = 0.5 - 0.5*ax_height
    ax1 = plt.axes( [ x_lowcorner, y_lowcorner, ax_width, ax_height ] )
    ax1.set_xlabel( 'Different Star Pairs' )
    ax1.set_ylabel( 'Variances' )
    ax1.plot( range( npairs ), variances, '-ok', ms=markersize, lw=linewidth )
    ylow = variances.min() - 0.1*( variances.max() - variances.min() )
    yupp = variances.max() + 0.1*( variances.max() - variances.min() )
    ax1.set_xlim( [ -0.5, len( variances ) + 0.5 ] )
    ax1.set_ylim( [ ylow, yupp ] )
    plt.savefig( figname1 )

    # Now plot the time series for each of the pairs:
    npanels = npairs
    nrows_perfig = 5
    nfigs = np.ceil( npanels / float( nrows_perfig ) )
    ncols = 1
    ax_height = ( 1. - 2.*edge_buffer ) / nrows_perfig
    fig_counter = 0
    fignames = []
    for i in range( npanels ):
        j = (i+1) % nrows_perfig
        if ( i%nrows_perfig==0 ):
            fig_counter += 1
            if fig_counter>1:
                # Save the current figure:
                plt.savefig( figname )
            # Specify the name for the next figure:
            figname = str( obj.analysis_dir + '/check_pairs_relphot_fig%iof%i.png' % \
                           ( fig_counter, nfigs ) ).replace( '//', '/' )
            fignames = fignames + [ figname ]
            # Open the new figure for plotting:
            figi = plt.figure()
            figi.suptitle( 'Relative Fluxes: pair checks (fig %i of %i)' % (fig_counter, nfigs ) )
        panel_number = i + 1 - ( fig_counter - 1 )*nrows_perfig
        x_lowercorner = 1.5*edge_buffer
        y_lowercorner = edge_buffer + nrows_perfig*ax_height - panel_number*ax_height
        if i==0:
            ax_first = figi.add_axes( [ x_lowercorner, y_lowercorner, ax_width, ax_height ] )
        else:
            ax_lower = figi.add_axes( [ x_lowercorner, y_lowercorner, ax_width, ax_height], \
                                      sharex=ax_first, sharey=ax_first )
        cax = plt.gca()
        plt.setp( cax.yaxis.get_ticklabels(), visible=True )
        cax.xaxis.set_major_formatter( matplotlib.ticker.OldScalarFormatter() )
        cax.yaxis.set_major_formatter( matplotlib.ticker.OldScalarFormatter() )
        cax.errorbar( obj.obstimes, obj.check_pairs_relphot_vals[ :, i ], \
                      yerr=obj.check_pairs_relphot_errs[ :, i ], fmt='-ok', lw=3 )
        cax.set_ylabel( 'Stars %i-%i' % ( obj.check_pairs_ixs[ i ][ 0 ], obj.check_pairs_ixs[ i ][ 1 ] ) )
        if ( ( panel_number==nrows_perfig ) + ( i==npanels-1 ) ):
            cax.set_xlabel( 'Time' )
            plt.setp( cax.xaxis.get_ticklabels(), visible=True )
        else:
            plt.setp( cax.xaxis.get_ticklabels(), visible=False )
    # Store the names of the saved figures in the photom object:
    obj.check_pairs_relphot_figures = fignames
    
    return None

def plot_check_indivs_results( obj ):
    """
    Makes two kinds of plots:

      ** Figure 1
      A plot of std( fluxA / [ fluxB + fluxC + ... ] ) where fluxA, fluxB, ... are
      the absolute flux time series for starA, starB, ... etc as a function of the
      different pair combinations.
      TO-DO: Add labels that show which pair each point on the plot corresponds to.
                  
      ** Figure 2 and onwards
      Plots std( fluxA / [ fluxB + fluxC + ... ] ) versus time for each of the
      different star pairs, with a different pair in each panel. There are five
      panels per figure, with more figures being generated as needed. 
    """
    
    edge_buffer = 0.08
    linewidth = 2
    markersize = 5
    #npairs = np.shape( obj.check_pairs_relphot_vals )[ 1 ]
    variances = np.std( obj.check_pairs_relphot_vals, axis=0 )
    
    # Plot the variances for each of the cases:
    plt.figure()
    figname = str( obj.analysis_dir + '/check_indivs_variances.png' ).replace( '//', '/' )
    obj.check_indivs_variances_figure = figname
    x_lowcorner = 1.5*edge_buffer
    ax_width = 1. - 2*edge_buffer
    ax_height = 0.5*ax_width
    y_lowcorner = 0.5 - 0.5*ax_height
    ax = plt.axes( [ x_lowcorner, y_lowcorner, ax_width, ax_height ] )
    plt.xlabel( 'Different Comparisons Excluded' )
    plt.ylabel( 'Variances' )
    #plt.plot( range( npairs ), variances, '-ok', lw=linewidth, ms=markersize )
    plt.plot( range( obj.ncomparisons ), variances, '-ok', lw=linewidth, ms=markersize ) 
    ylow = variances.min() - 0.1*(variances.max() - variances.min() )
    yupp = variances.max() + 0.1*(variances.max() - variances.min() )
    plt.xlim( [ -0.5, obj.ncomparisons + 0.5 ] )
    plt.ylim( [ ylow, yupp ] )

    # Now plot the time series for each of the cases:
    npanels = obj.ncomparisons
    nrows_perfig = 5
    nfigs = np.ceil( npanels / float( nrows_perfig ) )
    ncols = 1
    ax_height = ( 1. - 2.*edge_buffer ) / nrows_perfig
    fig_counter = 0
    fignames = []
    for i in range( npanels ):
        j = (i+1) % nrows_perfig
        if ( i%nrows_perfig==0 ):
            top_panel = True
            fig_counter += 1
            if fig_counter>1:
                # Save the current figure:
                plt.savefig( figname )
            # Specify the name for the next figure:
            figname = str( obj.analysis_dir + '/check_indivs_relphot_fig%iof%i.png' \
                           % ( fig_counter, nfigs ) ).replace( '//', '/' )
            fignames = fignames + [ figname ]
            # Open the new figure for plotting:
            figi = plt.figure()
            figi.suptitle( 'Relative fluxes: excluding one comparison at a time (fig %i of %i)' \
                           % ( fig_counter, nfigs ) )
        else:
            top_panel = False
        panel_number = i + 1 - ( fig_counter - 1 )*nrows_perfig
        x_lowercorner = 1.5*edge_buffer
        y_lowercorner = edge_buffer + nrows_perfig*ax_height - panel_number*ax_height
        if top_panel==True:
            ax_top = plt.axes( [ x_lowercorner, y_lowercorner, ax_width, ax_height ] )
        else:
            ax_lower = plt.axes( [ x_lowercorner, y_lowercorner, ax_width, ax_height], \
                                 sharex=ax_top, sharey=ax_top )
        cax = plt.gca()
        plt.setp( cax.yaxis.get_ticklabels(), visible = True)
        cax.xaxis.set_major_formatter( matplotlib.ticker.OldScalarFormatter() )
        cax.yaxis.set_major_formatter( matplotlib.ticker.OldScalarFormatter() )
        cax.errorbar( obj.obstimes, obj.check_indivs_relphot_vals[ :, i ], \
                      yerr=obj.check_indivs_relphot_errs[ :, i ], fmt='-ok', lw=linewidth+1 )
        cax.set_ylabel( 'Excl. %i' % (i+1) )
        if ( ( panel_number==nrows_perfig ) + ( i==npanels-1 ) ):
            cax.set_xlabel( 'Time' )
            plt.setp( cax.xaxis.get_ticklabels(), visible=True )
        else:
            plt.setp( cax.xaxis.get_ticklabels(), visible=False )
    # Store the names of the saved figures in the photom object:
    obj.check_indivs_relphot_figures = fignames
    
    return None


def plot_each_fluxseries( obj ):
    """
    Simply plots the flux as a function of time for each of the stars.
    This can be useful for identifying how the brightnesses compare,
    whether or not there's any obviously variable stars etc.
    """
    
    edge_buffer = 0.08
    markersize = 5
    linewidth = 2
    fig = plt.figure()
    figname = str( obj.analysis_dir + '/fluxseries_eachstar.png' ).replace( '//', '/' )
    obj.fluxseries_eachstar_figure = figname
    x_lowcorner = 1.5*edge_buffer
    ax_width = 1. - 2*edge_buffer
    ax_height = 0.5*ax_width
    y_lowcorner = 0.5 - 0.5*ax_height
    ax = plt.axes( [ x_lowcorner, y_lowcorner, ax_width, ax_height ] )
    ax.set_xlabel( 'Time' )
    ax.set_ylabel( 'Flux' )
    for i in range( obj.nstars ):
        ax.plot( obj.obstimes, obj.absphot_vals_all[:,i], '-', lw=linewidth, label='star{0}'.format( str( i ) ) )
    ax.legend()
    plt.savefig( figname )
    obj.check_indiv_fluxseries = figname

    return None
