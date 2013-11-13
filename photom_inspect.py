import pyfits
from pyraf import iraf
import pdb
import os
import numpy as np
homestr = os.path.expanduser('~')

def Main(obj, obstime_kw=None, iraf_display_mode='display'):
    """
    Given a list of images in a specified folder, will display
    them using iraf.display (if iraf_display_mode=='display') or iraf.imexamine
    (if iraf_display_mode=='imexamine') in blocks of 10. For first pass inspection,
    the point is to see whether there are any significant pointing
    drifts between frames that will cause the source tracking
    algorithm to fail. For second pass inspection, the point is
    to make a quick comparison between the absolute photometry
    output from the pipeline and manual imexam photometry values.
    """
    images = np.loadtxt(obj.image_list, dtype='str')
    if obstime_kw!=None:
        obstimes = np.zeros(len(images))
        for i in range(len(obstimes)):
            h = pyfits.getheader(images[i])
            obstimes[i] = h[obstime_kw]
        ixs = np.argsort(obstimes)
        images = images[ixs]
    blockids = np.zeros(len(images))
    nperblock = 10
    nimages = len(images)
    nblocks = int(np.ceil(float(nimages)/nperblock))
    record_outcome = np.ones(nblocks)
    block_counter = 0
    for i in range(nblocks):
        n = min([nperblock, nimages-i*nperblock])
        print '\nBlock %i of %i' % (i+1,nblocks)
        for j in range(n):
            ix = i*nperblock+j
            blockids[ix] = i
            try:
                print 'Loading %s...' % images[ix]
                if iraf_display_mode=='display':
                    iraf.display(images[ix],j+1)
                elif iraf_display_mode=='imexamine':
                    iraf.imexamine(images[ix],j+1)
                else:
                    pdb.set_trace()
            except:
                pass
        print '\nEnter 1 for OK, 0 if not:\n'
        outcome = ''
        while outcome=='':
            outcome = raw_input('')
        record_outcome[i] = outcome
    ixs = np.arange(nblocks)[record_outcome==0]
    ncloser = len(ixs)
    print '\nYou identified %i blocks to look at again closely.' % ncloser
    print 'Enter y to go through them again now, or n to exit:'
    outcome = ''
    while outcome=='':
        outcome = raw_input('')
    if outcome=='y':
        for i in range(ncloser):
            closer_images = images[blockids==ixs[i]]
            print '\n Block %i:' % (ixs[i]+1)
            for j in range(len(closer_images)):
                print closer_images[j]
                iraf.display(closer_images[j],j+1)
            print '   (enter c to continue)'
            outcome = ''
            while outcome=='':
                outcome = raw_input('')
    else:
        print '\nFor future reference, the identified blocks were:'
        for i in range(ncloser):
            print '\n  Block %i, containing:' % ixs[i]
            closer_images = images[blockids==ixs[i]]
            for j in range(len(closer_images)):
                print '   - %s' % closer_images[j]
    return None
