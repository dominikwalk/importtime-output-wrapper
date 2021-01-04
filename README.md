# Python importtime output wrapper

Starting from the Python3.7 release, the ```-X importtime``` option is available.
It can be used to measure the import time for any python module, **including all nested imports**.

The official documentaion for this function can be found here:
https://docs.python.org/3.7/using/cmdline.html#id5

The implementaion prints out the output to the ```stderr```in string format. To actually use this output for benchmarking, I wrote this simple wrapper, that parses the output and puts it into a "usable" ```json``` format.

Alternatively, the program can format the output as a waterfall digram. However, this feature only serves to provide a quick overview.

The ```importtime_output_wrapper``` can also sort the imported modules (and their nested imports) by the time they needed.

It has a command-line interface that works as follows:

```console
usage: importtime_output_wrapper.py [-h] [--sort [{self,cumulative}]] module
```

As ```module``` any python module can be provided.
The optional argument ```--sort``` will sort the output either by the time every module needed to import (```--sort self```) or by the cumulative time (```--sort cumulative```).
## output as json
For example: calling ```$ python -X importtime -c "import os"``` would produce the following (reduced) output:
```console
import time: self [us] | cumulative | imported package
import time:      1504 |       1504 | _frozen_importlib_external
import time:      1073 |       1073 |   time
import time:      1749 |       2821 | zipimport
...
```

...and insted if you call ```$ python -m importtime_output_wrapper os```, it will produce the following (reduced) output:
```console
[
  {
    "name": "_frozen_importlib_external",
    "t_self_us": 550,
    "t_cumulative_us": 550,
    "nested_imports": []
  },
  {
    "name": "zipimport",
    "t_self_us": 368,
    "t_cumulative_us": 1049,
    "nested_imports": [
      {
        "name": "time",
        "t_self_us": 682,
        "t_cumulative_us": 682,
        "nested_imports": []
      }
    ]
  },
  ...
]
```
## output as waterfall diagram
As an additional feature, the program can also display the output as a waterfall digram in the terminal. For the above example, calling ```$ python -m importtime_output_wrapper os --format waterfall``` results in the following (reduced) output:
```console
module name                | import time (us)
-------------------------------------------------------------------------------
_frozen_importlib_external   ====(1425)
time                         ====(1578)
.zipimport                   ==(824)
_codecs                      (226)
codecs                       ========(2734)
.encodings.aliases           =========(3077)
..encodings                  ================(5461)
...encodings.utf_8           ===(1110)
....encodings.cp1252         ===(1265)
....._signal                 (128)
......encodings.latin_1      ===(1232)
[...]
_functools                   (98)
.functools                   ======(2051)
..contextlib                 =======(2606)
....importlib.util           ======(2298)
.....pywin32_bootstrap       ==============(4761)
......sitecustomize          ====(1615)
.......usercustomize         ===(1129)
........site                 ===========================================(14494)
```
The output is scaled to 79 characters. The number behind the bar indicates the import time in microseconds.

I personally used this program to sort the output of the ```-X importtime``` implementaion to index modules that were slowing down the startup of a larger project.
Maybe someone else will find this functionality useful someday.

**Note** that its output may be broken in multi-threaded application, as mentioned in the [official documentation](https://docs.python.org/3.7/using/cmdline.html#id5 "importtime documentation").
