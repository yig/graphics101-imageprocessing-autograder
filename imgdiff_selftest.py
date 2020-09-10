from __future__ import print_function, division

from imgdiff import *

def test_one( path1, path2, expected_diff, expected_diffneighbor ):
    d = diff( path1, path2 )
    dn = mindiff_in_neighborhood( path1, path2 )
    print( 'expected diff strict:', expected_diff, 'received:', d.sum(),
        'ERROR' if ( d.sum() != expected_diff ) else 'success' )
    print( 'expected diff neighbors:', expected_diffneighbor, 'received:', dn.sum(),
        'ERROR' if ( dn.sum() != expected_diffneighbor ) else 'success' )

def test_diffs():
    path1 = 'selftest/simplest-dot.png'
    path2 = 'selftest/simplest-dot-horizontal1.png'
    ## 2 pixels * 3 channels * difference
    test_one( path1, path2, 2*3*255, 0 )
    
    path1 = 'selftest/simplest-dot.png'
    path2 = 'selftest/simplest-dot-horizontal2.png'
    ## 2 pixels * 3 channels * difference
    test_one( path1, path2, 2*3*255, 2*3*255 )
    
    path1 = 'selftest/simple-single-dot.png'
    path2 = 'selftest/simple-single-dot.png'
    test_one( path1, path2, 0, 0 )
    
    path1 = 'selftest/simple-single-dot.png'
    path2 = 'selftest/simple-single-dot-vertical1.png'
    ## 2 pixels * 3 channels * difference
    test_one( path1, path2, 2*3*255, 0 )
    
    path1 = 'selftest/simple-single-dot.png'
    path2 = 'selftest/simple-single-dot-horizontal1.png'
    ## 2 pixels * 3 channels * difference
    test_one( path1, path2, 2*3*255, 0 )
    
    path1 = 'selftest/simple-single-dot.png'
    path2 = 'selftest/simple-single-dot-horizontal2.png'
    ## 2 pixels * 3 channels * difference
    test_one( path1, path2, 2*3*255, 2*3*255 )
    
    
    path1 = 'selftest/simple-single-dot.png'
    path2 = 'selftest/simple-single-dot-diagonal1.png'
    ## 2 pixels * 3 channels * difference
    test_one( path1, path2, 2*3*255, 0 )
    
    path1 = 'selftest/simple-stripes-one.png'
    path2 = 'selftest/simple-stripes-two1.png'
    ## 2 pixels * 3 channels * difference
    test_one( path1, path2, 23*3*255, 0 )
    
    path1 = 'selftest/simple-stripes-one.png'
    path2 = 'selftest/simple-stripes-two2.png'
    ## 2 pixels * 3 channels * difference
    test_one( path1, path2, 23*3*255, 23*3*255 )

test_diffs()
