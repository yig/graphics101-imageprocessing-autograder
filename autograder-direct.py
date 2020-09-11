#!/usr/bin/env python

from __future__ import print_function, division
from datetime import datetime, date
import webbrowser
import numpy as np
import os, sys, subprocess, multiprocessing
import imgdiff

import argparse
parser = argparse.ArgumentParser( description = 'Grade raycasting.' )
# parser.add_argument( 'command', choices = ['grade', 'truth'], help = 'The command to run.' )
parser.add_argument( 'exe', help = 'The path to the raycasting executable.' )
args = parser.parse_args()

## https://stackoverflow.com/questions/4060221/how-to-reliably-open-a-file-in-the-same-directory-as-a-python-script
## assert os.path.abspath( os.pwd() ) == os.path.dir( os.path.abspath( __file__ ) )
## __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
here_dir = sys.path[0]
assert len( here_dir ) > 0

## Make small images for time reasons
LONG_EDGE_SIZE = 300

tests_dir = os.path.join( here_dir, 'tests' )

## Average score of each category weighted by category weights
tests = [
    # file, category
    ( 'camera_test1.json', 'camera' ),
    ( 'camera_test2.json', 'camera' ),
    ( 'orthographic_test1.json', 'camera' ),
    ( 'orthographic_test2.json', 'camera' ),
    
    ( 'cone_cube.json', 'cube' ),
    ( 'refraction_inside.json', 'refraction' ),
    ( 'refraction.json', 'refraction' ),
    ( 'sphere.obj', 'sphere' ),
    ( 'spheres_cylinder.json', 'cylinder' ),
    ( 'stress_test.json', 'cone' )
    ]

# if args.command == 'exe':
#     raise NotImplementedError
# elif args.command == 'grade':

## Create the output location
output_dir = os.path.join( here_dir, f'autograder-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}' )
output_html = output_dir + '.html'
assert not os.path.exists( output_dir )
os.mkdir( output_dir )

## Run all raytracing tests in parallel
def run_one( json_name ):
    subprocess.call([
        args.exe,
        os.path.join( tests_dir, json_name ),
        os.path.join( output_dir, os.path.splitext( json_name )[0] + '.png' ),
        str(LONG_EDGE_SIZE)
        ])
multiprocessing.Pool().pmap( json_name for json_name, category in tests )

## Measure and save the output
out = open( output_html, 'w' )
out.write( open( "header.html" ).read() )

###
### Scene tests 
###

out.write( '<h3>Scene Tests</h3>' )
out.write( '''
<table style="width:100%">
<tr><th>Scene</th><th>Correct</th><th>Yours</th><th>Difference</th><th>Score</th></tr>
''' )
json_files = [f for f in listdir(json_directory) if '.json' in f]
for json in json_files:
	name = json.replace(".json","")
	param_file = f"{json_directory}/{json}"
	gt_path = f"{answer_result_path}/{name}.png"
	test_path = f"{test_result_path}/{name}.png"
	diff_path = f"{diff_dir}/{name}-diff.png"
	subprocess.call([answer_binary_path, param_file, gt_path, str(LONG_EDGE_SIZE) ])
	subprocess.call([test_binary_path, param_file, test_path, str(LONG_EDGE_SIZE) ])
	# comparison
	diffimg = imgdiff.diff( gt_path, test_path, diff_path )
	score = 100 - np.average( np.abs( diffimg ) )*100
	out.write( f'''
<tr>
<td style="width:15%">{name}</td>
<td style="width:25%"><img src="{gt_path}"></td> 
<td style="width:25%"><img src="{test_path}"></td>
<td style="width:25%"><img src="{diff_path}"></td>
<td style="width:10%"><label>{score}</label></td>
</tr>
''' ) 

###
### Footer
###

out.write( '</table>' )
out.write( '</body>' )
out.write( '</html>' )
out.close()

print( 'Saved:', output_html )

webbrowser.open( output_html )
