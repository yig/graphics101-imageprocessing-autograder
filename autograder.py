#!/usr/bin/env python

from __future__ import print_function, division
from datetime import datetime, date
import webbrowser
import numpy as np
import os, sys, subprocess
import imgdiff

def usage():
    print( "Usage:", sys.argv[0], "path/to/raycasting", file = sys.stderr )
    sys.exit(-1)

if len( sys.argv ) != 2:
    usage()

path_to_binary = sys.arv[1]

## This script must be run next to the file itself. We assume the example are here, too.
assert os.path.abspath( os.cwd() ) == os.path.dir( os.path.abspath( __file__ ) )

output_dir = f'autograde {datetime.now().isoformat()}'
output_html = output_dir + '.html'
os.mkdirs( output_dir )

out = open( output_html, 'r' )
out.write( open( "header.html" ).read() )

###
### Camera tests
###

out.write( '<h3>Camera Tests</h3>' )

out.write( '''
<table>
<tr><th>Correct</th><th>Yours</th><th>Difference</th><th>Score</th></tr>
''' )

## Camera test 1
gt_path = "camera_test1-raycasting.png"
outpath = os.path.join( output_dir, "camera_test1.png" )
diffpath = os.path.join( output_dir, "camera_test1-diff.png" )
subprocess.call([ path_to_binary, "camera_test1.json", "500", outpath ])
diffimg = imgdiff.diff_in_neighborhood( gt_path, outpath, diffpath )
score = np.average( np.abs( diffimg ) )*100

out.write( f'''
<tr>
<td><img src="{gt_path}"></td>
<td><img src="{outpath}"></td>
<td><img src="{diffpath}"></td>
<td><img src="{score}"></td>
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
