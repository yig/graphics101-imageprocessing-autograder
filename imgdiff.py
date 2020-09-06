from __future__ import print_function, division
from numpy import *
from PIL import Image

if __name__ == '__main__':
    
    import os, sys
    
    args = list(sys.argv[1:])
    def usage():
        print( "Usage:", sys.argv[0], "image1.png image2.png output.png", file = sys.stderr )
        sys.exit(-1)
    
    if len( args ) != 3: usage()
    
    inpath1 = args[0]
    inpath2 = args[1]
    outpath = args[2]
    
    if diff( inpath1, inpath2, outpath ) is None: usage()

def diff( inpath1, inpath2, outpath = None ):
    
    print( "Loading:", inpath1 )
    img1 = asarray( Image.open( inpath1 ).convert('RGB') ).astype( int )
    print( "Loading:", inpath2 )
    img2 = asarray( Image.open( inpath2 ).convert('RGB') ).astype( int )
    
    if img1.shape != img2.shape:
        print( "ERROR: Image dimensions don't match:", img1.shape, "!=", img2.shape, file = sys.stderr )
        return None
    
    difference = abs( img1 - img2 )
    
    if outpath is not None:
        Image.fromarray( difference.astype( uint8 ) ).save( outpath )
        print( "Saved:", outpath )
    
    return difference

def diff_in_neighborhood( inpath1, inpath2, outpath = None ):
    
    print( "Loading:", inpath1 )
    img1 = asarray( Image.open( inpath1 ).convert('RGB') ).astype( int )
    print( "Loading:", inpath2 )
    img2 = asarray( Image.open( inpath2 ).convert('RGB') ).astype( int )
    
    if img1.shape != img2.shape:
        print( "ERROR: Image dimensions don't match:", img1.shape, "!=", img2.shape, file = sys.stderr )
        return None
    
    difference = abs( img1 - img2 )
    raise NotImplementedError( "Use the minimum difference over the 3x3 neighborhood around each pixel" )
    
    if outpath is not None:
        Image.fromarray( difference.astype( uint8 ) ).save( outpath )
        print( "Saved:", outpath )
    
    return difference
