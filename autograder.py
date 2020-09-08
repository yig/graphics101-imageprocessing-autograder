#!/usr/bin/env python

from __future__ import print_function, division
from datetime import datetime, date
import webbrowser
import numpy as np
import os, sys, subprocess
import imgdiff
from os import listdir
import shutil

def usage():
    print( "Usage:", sys.argv[0], "path/to/json_dir", "path/to/your_executable", "path/to/answer_executable", file = sys.stderr )
    sys.exit(-1)

if len( sys.argv ) != 4:
    usage()

json_directory = sys.argv[1]
test_binary_path = sys.argv[2]
answer_binary_path = sys.argv[3]

# create dirs
answer_result_path = "./grader_ground_truth"
test_result_path = "./grader_test_results"
diff_dir = "./grader_diff_dir"
all_dirs = [answer_result_path, test_result_path, diff_dir]
for dir_name in all_dirs:
	if os.path.exists(dir_name):
		shutil.rmtree(dir_name)
	os.mkdir(dir_name)
## This script must be run next to the file itself. We assume the example are here, too.
# assert os.path.abspath( os.pwd() ) == os.path.dir( os.path.abspath( __file__ ) )

output_dir = f'autograder_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}'
output_html = output_dir + '.html'
# os.mkdir( output_dir )

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
	subprocess.call([answer_binary_path, param_file, gt_path, "500" ])
	subprocess.call([test_binary_path, param_file, test_path, "500" ])
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
