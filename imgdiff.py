from __future__ import print_function, division
from numpy import *
from PIL import Image
import sys

def print_diff_statistics( difference ):
    assert len( difference.shape ) == 3
    
    print( "=> Difference statistics. Units are RGB-space lengths." )
    
    ## Sum across channels, convert to [0,1]
    difference = linalg.norm( difference, axis = 2 )/255
    
    #print( "Min:", difference.min() )
    #print( "Max:", difference.max() )
    #print( "Mean:", average( difference ) )
    #print( "Median:", median( difference ) )
    
    q0,q25,q50,q75,q90,q99,q100 = percentile( difference, ( 0, 25, 50, 75, 90, 99, 100 ) )
    print( "Min:", q0 )
    print( "Max:", q100 )
    print( "Mean:", average( difference ) )
    print()
    print( "25-th percentile:", q25 )
    print( "Median:", q50 )
    print( "75-th percentile:", q75 )
    print( "90-th percentile:", q90 )
    print( "99-th percentile:", q99 )

def diff( inpath1, inpath2, outpath = None ):
    '''
    Given:
        inpath1: A path to an image
        inpath2: A path to an image
        outpath (optional): A path to an output
    Returns:
        The absolute difference as a numpy.array containing integer values between 0 and 255.
    
    Computes the RGB-space difference image between the images stored at `inpath1` and `inpath2`.
    Saves the difference image to `outpath` if not None.
    '''
    
    print( "=> diff()" )
    
    print( "Loading:", inpath1 )
    img1 = asarray( Image.open( inpath1 ).convert('RGB') ).astype( int )
    print( "Loading:", inpath2 )
    img2 = asarray( Image.open( inpath2 ).convert('RGB') ).astype( int )
    
    if img1.shape != img2.shape:
        print( "ERROR: Image dimensions don't match:", img1.shape, "!=", img2.shape, file = sys.stderr )
        return None
    
    difference = abs( img1 - img2 )
    
    print_diff_statistics( difference )
    
    if outpath is not None:
        Image.fromarray( difference.astype( uint8 ) ).save( outpath )
        print( "Saved:", outpath )
    
    return difference

def mindiff_in_neighborhood( inpath1, inpath2, outpath = None ):
    '''
    Just like diff(), except the difference at a pixel
    is the smallest absolute difference between any pixel
    in a 3x3 window centered at that pixel.
    That is not symmetric. An isolated pixel in image 2 will be erased by
    a 3x3 window. So we have to look once from image 1 to image 2
    and again from image 2 to image 1. We return the element-wise maximum.
    This is like the Hausdorff distance.
    '''
    
    print( "mindiff_in_neighborhood()" )
    
    print( "Loading:", inpath1 )
    img1 = asarray( Image.open( inpath1 ).convert('RGB') ).astype( int )
    print( "Loading:", inpath2 )
    img2 = asarray( Image.open( inpath2 ).convert('RGB') ).astype( int )
    
    ## Compute non-commutative differences in both directions
    diff_1to2 = mindiff_in_neighborhood_asymmetric( img1, img2 )
    diff_2to1 = mindiff_in_neighborhood_asymmetric( img2, img1 )
    ## Propagate errors
    if diff_1to2 is None or diff_2to1 is None: return None
    ## Combine both differences.
    ## Take error with the larger total error summed across all color channels.
    diff_1to2_mag = diff_1to2.sum( axis = 2 )
    diff_2to1_mag = diff_2to1.sum( axis = 2 )
    ## UPDATE: We can't use the maximum, since it's per channel, not per pixel.
    # difference = maximum( diff_1to2, diff_2to1 )
    difference = diff_1to2.copy()
    difference[ diff_2to1_mag > diff_1to2_mag ] = diff_2to1[ diff_2to1_mag > diff_1to2_mag ]
    
    print_diff_statistics( difference )
    
    if outpath is not None:
        Image.fromarray( difference.astype( uint8 ) ).save( outpath )
        print( "Saved:", outpath )
    
    return difference

def mindiff_in_neighborhood_asymmetric( img1, img2 ):
    '''
    Given:
        img1: A row-by-column-by-channels image.
        img2: A row-by-column-by-channels image.
    Returns:
        A numpy.array containing the minimum absolute difference between
        each pixel in `img1` and the corresponding pixel in `img2` as well
        as its 8 neighbors in a 3x3 windiow.
        To find the minimum, the magnitude of the difference is computed as
        the sum of absolute differences across all channels.
    
    Helper function used by `mindiff_in_neighborhood()`.
    '''
    
    if img1.shape != img2.shape:
        print( "ERROR: Image dimensions don't match:", img1.shape, "!=", img2.shape, file = sys.stderr )
        return None
    
    difference = abs( img1 - img2 )
    
    ## For each offset, compute the current per-pixel difference magnitude across all channels.
    ## We have to recompute this for each offset, since we update `difference`.
    ## If the neighbor's magnitude is greater, replace the difference at the center pixel.
    
    ## +1,+1
    diffmag = difference.sum( axis = 2 )
    differenceoff = abs( img1[1:,1:] - img2[:-1,:-1] )
    mask = diffmag[1:,1:] > differenceoff.sum( axis = 2 )
    difference[1:,1:][ mask ] = differenceoff[ mask ]
    
    ## +1,0
    diffmag = difference.sum( axis = 2 )
    differenceoff = abs( img1[1:,:] - img2[:-1,:] )
    mask = diffmag[1:,:] > differenceoff.sum( axis = 2 )
    difference[1:,:][ mask ] = differenceoff[ mask ]
    
    ## +1,-1
    diffmag = difference.sum( axis = 2 )
    differenceoff = abs( img1[1:,:-1] - img2[:-1,1:] )
    mask = diffmag[1:,:-1] > differenceoff.sum( axis = 2 )
    difference[1:,:-1][ mask ] = differenceoff[ mask ]
    
    ## 0,-1
    diffmag = difference.sum( axis = 2 )
    differenceoff = abs( img1[:,:-1] - img2[:,1:] )
    mask = diffmag[:,:-1] > differenceoff.sum( axis = 2 )
    difference[:,:-1][ mask ] = differenceoff[ mask ]
    
    ## -1,-1
    diffmag = difference.sum( axis = 2 )
    differenceoff = abs( img1[:-1,:-1] - img2[1:,1:] )
    mask = diffmag[:-1,:-1] > differenceoff.sum( axis = 2 )
    difference[:-1,:-1][ mask ] = differenceoff[ mask ]
    
    ## -1,0
    diffmag = difference.sum( axis = 2 )
    differenceoff = abs( img1[:-1,:] - img2[1:,:] )
    mask = diffmag[:-1,:] > differenceoff.sum( axis = 2 )
    difference[:-1,:][ mask ] = differenceoff[ mask ]
    
    ## -1,+1
    diffmag = difference.sum( axis = 2 )
    differenceoff = abs( img1[:-1,1:] - img2[1:,:-1] )
    mask = diffmag[:-1,1:] > differenceoff.sum( axis = 2 )
    difference[:-1,1:][ mask ] = differenceoff[ mask ]
    
    ## 0,+1
    diffmag = difference.sum( axis = 2 )
    differenceoff = abs( img1[:,1:] - img2[:,:-1] )
    mask = diffmag[:,1:] > differenceoff.sum( axis = 2 )
    difference[:,1:][ mask ] = differenceoff[ mask ]
    
    return difference

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser( description = 'Compare two RGB images.' )
    parser.add_argument( 'image1', help = 'An image to compare.' )
    parser.add_argument( 'image2', help = 'Another image to compare.' )
    parser.add_argument( 'outpath', help = 'A path to store the difference image.' )
    parser.add_argument( '--neighborhood', '-n', action='store_true', help = 'If specified, images will be the same if the same pixel is in a 3x3 neghborhood in the other image.' )
    args = parser.parse_args()
    
    if args.neighborhood:
        result = mindiff_in_neighborhood( args.image1, args.image2, args.outpath )
    else:
        result = diff( args.image1, args.image2, args.outpath )
    
    if result is None: parser.print_usage( sys.stderr )
