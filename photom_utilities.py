import numpy as np
import itertools
import matplotlib.pyplot as plt
import matplotlib.ticker
import pdb

# This has been cut and pasted from another script, but I think it makes sense to
# include it here; it's basically a collection of routines that do useful things
# with photom objects. 

def stitch(objs, ix_target=None, ix_comparisons=None, make_plot=True, coadd_within=True, plot_errorbars='conservative'):
    """
    Takes the list of objects and stitches together the time series.
    """
    ix_target = np.array(ix_target).flatten()
    ix_comparisons = np.array(ix_comparisons).flatten()
    nobjs = len(objs)
    ncomparisons = len(ix_comparisons)
    times = np.zeros(1)
    relphot_vals = np.zeros(1)
    relphot_scatters = np.zeros(1)
    relphot_errs = np.zeros(1)
    for i in range(nobjs):
        obj = objs[i]
        targ_vals = obj.absphot_vals_all[:,ix_target].flatten()
        targ_errs = obj.absphot_errs_all[:,ix_target].flatten()
        if len(ix_comparisons)>1:
            comp_vals = np.sum(obj.absphot_vals_all[:,ix_comparisons],axis=1).flatten()
            comp_errs = np.sqrt(np.sum(obj.absphot_errs_all[:,ix_comparisons]**2.,axis=1)).flatten()
        else:
            comp_vals = obj.absphot_vals_all[:,ix_comparisons].flatten()
            comp_errs = obj.absphot_errs_all[:,ix_comparisons].flatten()
        if coadd_within==True:
            targ_val_i = np.sum(targ_vals, axis=0)
            targ_err_i = np.sqrt(np.sum(targ_errs**2., axis=0))
            comp_val_i = np.sum(comp_vals, axis=0)
            comp_err_i = np.sqrt(np.sum(comp_errs**2., axis=0))
            times_i = np.median(obj.obstimes)
            relphot_scatters = np.concatenate([relphot_scatters, np.array(np.std(targ_vals/comp_vals)/np.sqrt(len(targ_vals))).flatten()])
        else:
            targ_val_i = targ_vals
            targ_err_i = targ_errs
            comp_val_i = comp_vals
            comp_err_i = comp_errs
            times_i = obj.obstimes
            relphot_scatters = np.concatenate([relphot_scatters, np.zeros(len(targ_vals))+np.std(targ_vals/comp_vals)])
        relphot_val_i = targ_val_i/comp_val_i
        relphot_err_i = relphot_val_i*np.sqrt((targ_err_i/targ_val_i)**2.+(comp_err_i/comp_val_i)**2.)
        relphot_vals = np.concatenate([relphot_vals, np.array(relphot_val_i).flatten()])
        relphot_errs = np.concatenate([relphot_errs, np.array(relphot_err_i).flatten()])
        times = np.concatenate([times, np.array(times_i).flatten()])
    times = times[1:]
    relphot_vals = relphot_vals[1:]
    relphot_scatters = relphot_scatters[1:]
    relphot_errs = relphot_errs[1:]
    if make_plot==True:
        if plot_errorbars=='conservative':
            errs = np.zeros(len(times))
            for i in range(len(times)):
                errs[i] = max([relphot_scatters[i], relphot_errs[i]])
        elif plot_errorbars=='scatter':
            errs = relphot_scatters
        elif plot_errorbars=='formal':
            errs = relphot_errs
        plot_single(times, relphot_vals, errs, ix_target=ix_target, ix_comparisons=ix_comparisons)
    return times, relphot_vals, relphot_scatters, relphot_errs

def check_comparisons(objs, make_plot=True, coadd_within=True):
    """
    Cycle through all the possible pairs to identify obvious variable comparisons.
    Note that this routine assumes that the same stars have been used for each of
    the objects, with the same indices.
    """
    
    nobjs = len(objs)
    ncomparisons = (objs[0]).ncomparisons
    nframes = (objs[0]).nimages_good

    ixs = range((objs[0]).nstars)
    pairs = list(itertools.combinations(ixs,2))
    npairs = len(pairs)

    output = np.zeros([nobjs,npairs,2])
    for i in range(npairs):
        ix_target = pairs[i][0]
        ix_comparison = pairs[i][1]
        times, relphot_vals, relphot_scatters, relphot_errs = stitch(objs, ix_target=ix_target, ix_comparisons=ix_comparison, make_plot=False, coadd_within=coadd_within)
        output[:,i,0] = relphot_vals
        output[:,i,1] = relphot_errs

    if make_plot==True:
        plot_pairs(times,output,pairs)

    return times, output, pairs

def plot_pairs(times, array, pair_ixs):
    """
    Creates a set of plots to illustrate the different relative fluxes
    between each pair of stars.

    NOTE: This probably supercedes stuff in the photom_checks.py module. However,
    I should perhaps allow for there being more than 1 figure if there are too
    many comparison stars. Otherwise, as of 4apr2012 this particular routine
    works well.
    """
    # Get the data in a clearer format for plotting:
    nax = len(pair_ixs)
    relphot_vals = array[:,:,0]
    relphot_meds = np.median(relphot_vals,axis=0)
    relphot_errs = array[:,:,1]
    yvals = np.zeros([len(times),nax])
    yerrs = np.zeros([len(times),nax])
    for i in range(nax):
        yvals[:,i] = relphot_vals[:,i]/relphot_meds[i]-1
        yerrs[:,i]= relphot_errs[:,i]/relphot_meds[i]
    yvals[np.isfinite(yvals)!=True] = 0
    yerrs[np.isfinite(yerrs)!=True] = 0    
    # Set plotting parameters:
    xmin = times.min()-0.02*(times.max()-times.min())
    xmax = times.max()+0.02*(times.max()-times.min())
    ymin = np.min(yvals-yerrs)-0.02*(np.max(yvals+yerrs)-np.min(yvals-yerrs))
    ymax = np.max(yvals+yerrs)+0.02*(np.max(yvals+yerrs)-np.min(yvals-yerrs))
    linewidth = 3
    markersize = 5
    color = 'k'
    edge_buffer = 0.1
    ncols = 2
    nrows = 5
    ax_width = (1-2*edge_buffer)/float(ncols)
    ax_height = (1-2*edge_buffer)/float(nrows)
    nfigs = int(float(nax)/float(nrows))
    ax_counter = 1
    for k in range(nfigs):
        for i in range(ncols):
            xlow = 1.5*edge_buffer+i*ax_width
            for j in range(nrows):
                if ax_counter>nax:
                    continue
                else:
                    if ax_counter%(nrows*ncols)==1:
                        fig = plt.figure(figsize=[12,13])
                        fig.suptitle('Comparison of Relative Flux Pairs')
                    ylow = 1-0.5*edge_buffer-(j+1)*ax_height
                    if (i==0)*(j==0):
                        ax0 = fig.add_axes([xlow,ylow,ax_width,ax_height])
                    else:
                        ax = fig.add_axes([xlow,ylow,ax_width,ax_height], sharex=ax0, sharey=ax0)
                    cax = fig.gca()
                    cax.errorbar(times, yvals[:,ax_counter-1], yerr=yerrs[:,ax_counter-1], fmt='-o', c=color, ecolor=color, capsize=0, mfc=color, mec=color, lw=linewidth, ms=markersize)
                    cax.axhline(0,ls='--', c=color, lw=linewidth)
                    xtext = xmin+0.03*(xmax-xmin)
                    ytext = ymax-0.1*(ymax-ymin)
                    text_str = 'star%i/star%i' % (pair_ixs[ax_counter-1][0], pair_ixs[ax_counter-1][1])
                    cax.text(xtext,ytext,text_str)
                    if (j+1)%nrows!=0:
                        plt.setp(cax.get_xticklabels(), visible=False)
                    else:
                        cax.set_xlabel('Time')
                    if (i+1)%ncols!=1:
                        plt.setp(cax.get_yticklabels(), visible=False)
                    else:
                        cax.set_ylabel('Relative Flux')
                    ax_counter += 1
        ax0.set_xlim([xmin,xmax])
        ax0.set_ylim([ymin,ymax])
    return None

def plot_single(t, yval, yerr, ix_target=None, ix_comparisons=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    linewidth = 2
    elinewidth = 4
    color = 'k'
    markersize = 5
    yval_n = yval/np.median(yval)-1
    yerr_n = yerr/np.median(yval)
    ax.axhline(0,ls='--',lw=linewidth,c='r')
    ax.errorbar(t, yval_n, yerr=yerr_n, fmt='-o', c=color, ecolor=color, elinewidth=elinewidth, mew=elinewidth, mfc=color, mec=color, ms=markersize, lw=linewidth, barsabove=True)
    ax.set_xlim([t.min()-0.1*(t.max()-t.min()), t.max()+0.1*(t.max()-t.min())])
    ax.xaxis.set_major_formatter(matplotlib.ticker.OldScalarFormatter())
    ax.yaxis.set_major_formatter(matplotlib.ticker.OldScalarFormatter())
    ax.set_ylabel('Normalised Relative Flux')
    ax.set_xlabel('Time')
    title_str = ''
    if (ix_target!=None):
        title_str += 'target_ix=[%i] ' % ix_target
    if ix_comparisons!=None:
        if title_str!='':
            title_str += ', '
        title_str += 'comparison_ixs=['
        ixs = np.array(ix_comparisons).flatten()
        for i in range(len(ixs)):
            title_str += '%i' % ixs[i]
            if i<len(ixs)-1:
                title_str += ', '
            else:
                title_str += ']'
    if title_str!='':
        ax.set_title(title_str)
    plt.draw()
    return None
