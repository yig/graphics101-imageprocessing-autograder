#!/usr/bin/env python3

from datetime import datetime, date
import webbrowser
import numpy as np
import os, sys, subprocess, multiprocessing
from pathlib import Path
from collections import namedtuple
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
TESTS_DIR = HERE_DIR / 'scene_files'

## Where is the output stored?
OUTPUT_DIR = HERE_DIR / f'autograder-{datetime.now().strftime("%Y-%m-%d at %H:%M:%S")}'
OUTPUT_HTML = Path( str(OUTPUT_DIR) + '.html' )

## How large are the output images?
## Make small images for time reasons.
## This must match ground truth.
LONG_EDGE_SIZE = 300


######
###### Let's start processing
######

## A helper function to run one test. This needs to be out here
## so that multiprocessing finds it.
def run_one( exepath, jsonpath ):
    print( f"Starting {jsonpath.name}..." )
    subprocess.run([
        exepath,
        jsonpath,
        jsonpath2outputpath( jsonpath ),
        str(LONG_EDGE_SIZE)
        ])
    print( f"Finished {jsonpath.name}." )
def jsonpath2outputpath( jsonpath ): return OUTPUT_DIR / ( jsonpath.stem + '.png' )

## Since we use multiprocessing to run tests in parallel, we need to make
## sure this file can be imported without actually running the code.
if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser( description = 'Grade raycasting.' )
    # parser.add_argument( 'command', choices = ['grade', 'truth'], help = 'The command to run.' )
    parser.add_argument( 'exe', help = 'The path to the raycasting executable.' )
    args = parser.parse_args()
    
    ## Collect all tests
    all_tests = sorted(TESTS_DIR.glob('*.json'))
    
    ## Create the output directory
    assert not OUTPUT_DIR.exists()
    os.makedirs( OUTPUT_DIR )
    
    ## Run all tests in parallel:
    ## We must wrap the output in a list(), because otherwise nothing happens.
    with multiprocessing.Pool() as pool: list(pool.starmap( run_one, ( (args.exe,t) for t in all_tests ), 1 ))
    ## Run all tests serially:
    # map( run_one, all_tests )
    
    ## Organize them into categories
    category2test = {}
    Test = namedtuple('Test', ['jsonpath', 'outputpath'])
    for jsonpath in all_tests:
        category = jsonpath.name.split('_')[0]
        category2test.setdefault( category, [] ).append( Test( jsonpath, jsonpath2outputpath( jsonpath ) ) )
    
    ## Measure and save the output
    out = open( OUTPUT_HTML, 'w' )
    out.write( open( HERE_DIR / "header.html" ).read() )
    
    ## Iterate over categories
    for category in sorted( category2test.keys() ):
        tests = category2test[ category ]
        
        out.write( f'<h3>{category} tests</h3>' )
        out.write( '''
    <table style="width:100%">
    <tr><th>Scene</th><th>Correct</th><th>Yours</th><th>Difference</th><th>Score</th></tr>
    ''' )
    
        for test in tests:
            ## Ground truth images are next to the json files.
            gt_path = test.jsonpath.with_suffix( '.png' )
            ## Create a difference image.
            if test.outputpath.exists():
                diff_path = test.outputpath.parent / (test.outputpath.stem + '-diff.png')
                diffimg = imgdiff.mindiff_in_neighborhood( gt_path, test.outputpath, diff_path )
                ## The score is the average absolute pixel difference.
                ## These values range from 0 to 255.
                ## Convert them to [0,1] and then scale to [100,0].
                ## Boost by an extra 10x, since pixels may be subtly different.
                score = max( 0, 100 - np.clip( np.average( np.abs( diffimg ) )/255, 0, 1 )*100*10 )
            else:
                diff_path = ""
                score = 0
            
            out.write( f'''
    <tr>
    <td style="width:15%">{test.jsonpath.name}</td>
    <td style="width:25%"><img src="{gt_path}"></td> 
    <td style="width:25%"><img src="{test.outputpath}"></td>
    <td style="width:25%"><img src="{diff_path}"></td>
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
