# Raycasting Autograder

This autograder is designed for  for [graphics101-raytracing](http://github.com/yig/graphics101-raytracing).
Download this repository and run it via:

    python3 autograde.py path/to/build/raycasting

If you download `graphics101-raycasting-autograder` and place it
next to `graphics101-raycasting` in the filesystem, then the command would be:

    python3 autograde.py ../graphics101-raycasting/build/raycasting

The numbers in the score column measure the average absolute difference in pixel values between the ground truth and the tested executable magnified by 10.
(Because of aliasing artifacts near the boundaries of shapes, the difference actually uses the minimum to a pixel or its 8 neighbors.)
A perfect score is 100. A score of 0 means that the average absolute difference is 10%.
This does not translate to a grade for the assignment.

## Installing

The autograder depends on Python 3.x and the following modules: `numpy` and `pillow`. You can install the modules via:

    pip3 install numpy pillow

or install the [Poetry](https://python-poetry.org/) dependency manager and run:

    poetry install
    poetry shell

## Changing the examples

The autograder runs the `raycasting` executable on all tests in the
`scene_files` directory. If you are creating new examples for students, an easy way to generating the ground truth images for all tests is to run

    parallel path/to/solution/build/raycasting '{}' '{.}.png' 300 ::: scene_files/*.json

using the solution raycasting executable.
