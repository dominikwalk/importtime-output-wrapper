# Python importtime implementaion wrapper

Starting from the Python3.7 release, the ```-X importtime``` option is available.
It can be used to measure the import time for any python module, including all nested
imports.

The official documentaion for this function can be found here:
https://docs.python.org/3.7/using/cmdline.html#id5

The implementaion prints out the output to the ```stderr```in string format. To actually
use this output for benchmarking, I wrote this simple wrapper, that parses the output
and puts it into a "usable" ```json```format.

The ```importtime_wrapper``` can also sort the imported modules
(and their nested imports) by the time they needed.
