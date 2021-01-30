# Image Processing Autograder

This autograder is designed for [graphics101-imageprocessing](http://github.com/yig/graphics101-imageprocessing).
Download this repository and run it via:

    python3 autograde.py path/to/build/imageprocessing --all

If you download `graphics101-imageprocessing-autograder` and place it
next to `graphics101-imageprocessing` in the filesystem, then the command would be:

    python3 autograde.py ../graphics101-imageprocessing/build/imageprocessing --all

The numbers in the score column measure the average absolute difference in pixel values between the ground truth and the tested executable magnified by 10.
(Because of aliasing artifacts near the boundaries of shapes, the difference actually uses the minimum to a pixel or its 8 neighbors.)
A perfect score is 100. A score of 0 means that the average absolute difference is 10%.
This does not translate to a grade for the assignment.

You can run only a subset of tests by changing the `--all` flag. Possibilities are:

```
  --all               Whether to execute all tests.
  --all-but-convolve  Whether to execute all tests except convolve.
  --grey              Whether to execute grey tests.
  --box               Whether to execute box tests.
  --edges             Whether to execute edge tests.
  --sharpen           Whether to execute sharpen tests.
  --scale             Whether to execute scale tests.
  --convolve          Whether to execute convolve tests.
```

You can pass more than one flag.

## Installing

The autograder depends on Python 3.x and the following modules: `numpy` and `pillow`. You can install the modules via:

    pip3 install numpy pillow

or install the [Poetry](https://python-poetry.org/) dependency manager and run:

    poetry install
    poetry shell

## Changing the examples

The autograder runs the `imageprocessing` executable on all images in the
`test_cases` directory and all filters in the `test_cases/filters` subdirectory. If you are creating new examples for students, an easy way to generating the ground truth images for all tests is to run

    python3 autograde.py ../graphics101-imageprocessing/build/imageprocessing --all

using the solution `imageprocessing` executable and then move the output files into `test_cases/{name}-reference` subdirectories.
