#!/usr/bin/env python3

from datetime import datetime, date
import webbrowser
import numpy as np
import os, sys, subprocess, multiprocessing
from pathlib import Path
from collections import namedtuple
import itertools
import imgdiff


######
###### Some global definitions
######

## Where are the tests stored?
## https://stackoverflow.com/questions/4060221/how-to-reliably-open-a-file-in-the-same-directory-as-a-python-script
## assert os.path.abspath( os.pwd() ) == os.path.dir( os.path.abspath( __file__ ) )
## __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
assert len( sys.path[0] ) > 0
HERE_DIR = Path( sys.path[0] )
TESTS_DIR = HERE_DIR / 'test_cases'

## Where is the output stored?
OUTPUT_DIR = HERE_DIR / f'autograde-{datetime.now().strftime("%Y-%m-%d at %H-%M-%S")}'
OUTPUT_HTML = Path( str(OUTPUT_DIR) + '.html' )

######
###### Let's start processing
######

## A helper function to run one test. This needs to be out here
## so that multiprocessing finds it.
def run_one( arguments ):
    print( "Running:", arguments )
    ## All this str(.as_posix()) business is to solve a problem on some Windows machines
    ## the complained that a WindowsPath is not iterable.
    subprocess.run( arguments )
    print( "Finished:", arguments )

## Since we use multiprocessing to run tests in parallel, we need to make
## sure this file can be imported without actually running the code.
if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser( description = 'Grade Image Processing.' )
    # parser.add_argument( 'command', choices = ['grade', 'truth'], help = 'The command to run.' )
    parser.add_argument( 'executable', help = 'The path to the imageprocessing executable.' )
    args = parser.parse_args()
    
    ## Collect all tests
    IMAGE_NAMES = TESTS_DIR.glob('*.png')
    FILTERS = ( TESTS_DIR / 'filters' ).glob('*.png')
    all_tests = [
        [ 'grey' ],
        [ 'box', '0' ],
        [ 'box', '3' ],
        [ 'box', '25' ],
        [ 'edges' ],
        [ 'sharpen', '1', '5' ],
        [ 'sharpen', '2', '5' ],
        [ 'sharpen', '2', '10' ],
        [ 'scale', '100', '100' ],
        [ 'scale', '50', '100' ],
        [ 'scale', '10', '100' ],
        [ 'scale', '100', '50' ],
        [ 'scale', '100', '10' ],
        [ 'scale', '50', '50' ],
        [ 'scale', '10', '10' ],
        [ 'scale', '200', '200' ],
        [ 'scale', '50', '200' ],
        [ 'scale', '200', '50' ]
        ]
    all_tests.extend([ [ 'convolve', filter ] for filter in FILTERS ])
    
    ## Create the output directory
    print( OUTPUT_DIR )
    assert not OUTPUT_DIR.exists()
    os.makedirs( OUTPUT_DIR )
    assert OUTPUT_DIR.exists()
    
    ## Organize them
    name2test = {}
    Test = namedtuple('Test', ['webname', 'arguments', 'outname'])
    for image_path in IMAGE_NAMES:
        for test in all_tests:
            if test[0] == 'convolve':
                filter = test[1]
                outname = f"{image_path.stem}-convolve-{filter.stem}.png"
                webname = 'convolve ' + filter.name
            else:
                outname = f"{image_path.stem}-{'-'.join(test)}.png"
                webname = ' '.join(test)
            arguments = [args.executable] + list(test) + [ image_path, OUTPUT_DIR/outname ]
            name2test.setdefault( image_path.name, [] ).append( Test( webname, arguments, outname ) )
    
    ## Run all tests in parallel:
    ## We must wrap the output in a list(), because otherwise nothing happens.
    ## We must pass the output directory as a parameter,
    ## since it is derived from the current time and that may be different in
    ## other instantiations.
    # print( list( itertools.chain( *name2test.values() ) ) )
    with multiprocessing.Pool() as pool: list(pool.imap( run_one, ( test.arguments for test in itertools.chain( *name2test.values() ) ), 1 ))
    ## Run all tests serially:
    # for test in itertools.chain( *name2test.values() ): run_one( test.arguments )
    
    ## Measure and save the output
    out = open( OUTPUT_HTML, 'w' )
    out.write( open( HERE_DIR / "header.html" ).read() )
    
    ## Iterate over categories
    for name in sorted( name2test.keys() ):
        tests = name2test[ name ]
        
        out.write( f'<h3>{name}</h3>' )
        out.write( '''
    <table style="width:100%">
    <tr><th>Command</th><th>Correct</th><th>Yours</th><th>Difference</th><th>Score</th></tr>
    ''' )
    
        for test in tests:
            ## Ground truth images are next to the json files.
            gt_path = TESTS_DIR / (Path(name).stem + '-reference') / test.outname
            ## Create a difference image.
            outpath = OUTPUT_DIR/test.outname
            if outpath.exists():
                diff_path = outpath.parent / (outpath.stem + '-diff.png')
                diffimg = imgdiff.diff( gt_path, outpath, diff_path )
                ## The score is the average absolute pixel difference.
                ## These values range from 0 to 255.
                ## Convert them to [0,1] and then scale to [100,0].
                ## Boost differences by an extra 10x, since pixels may be subtly different.
                score = int(round( max( 0, 100 - np.clip( np.average( np.abs( diffimg ) )/255, 0, 1 )*100*10 ) ))
                diff_path_URI = diff_path.relative_to(HERE_DIR).as_posix()
            else:
                diff_path_URI = ""
                score = 0
            
            out.write( f'''
    <tr>
    <td style="width:15%">{test.webname}</td>
    <td style="width:25%"><img src="{gt_path.relative_to(HERE_DIR).as_posix()}"></td>
    <td style="width:25%"><img src="{outpath.relative_to(HERE_DIR).as_posix()}"></td>
    <td style="width:25%"><img src="{diff_path_URI}"></td>
    <td style="width:10%"><label>{score}</label></td>
    </tr>
    ''' )
        
        out.write( '</table>' )
        out.write( '' )
    
    ###
    ### Footer
    ###
    
    out.write( '</body>' )
    out.write( '</html>' )
    out.close()
    
    print( 'Saved:', OUTPUT_HTML )
    
    webbrowser.open( OUTPUT_HTML.as_uri() )
