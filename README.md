# Python importtime output wrapper

Starting from the Python3.7 release, the ```-X importtime``` option is available.
It can be used to measure the import time for any python module, **including all nested imports**.

The official documentaion for this function can be found here:
https://docs.python.org/3.7/using/cmdline.html#id5

The implementaion prints out the output to the ```stderr```in string format. To actually use this output for benchmarking, I wrote this simple wrapper, that parses the output and puts it into a "usable" ```json``` format.

The ```importtime_output_wrapper``` can also sort the imported modules (and their nested imports) by the time they needed.

It has a comamnd-line-interface that works as follows:

```console
usage: importtime_output_wrapper.py [-h] [--sorted [{self,cumulative}]] module
```

As ```module``` any python module can be provided.
The optional argument ```--sorted``` will sort the output either by the time every module needed to import (```--sorted self```) or by the cumulative time (```--sorted cumulative```).

For example: calling ```python -X importtime -c "import os"``` would produce the following (reduced) output:
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

I personally used this program to sort the output of the ```-X importtime``` implementaion to index modules that were slowing down the startup of a larger project.
Maybe someone else will find this functionality useful someday.

**Note** that its output may be broken in multi-threaded application, as mentioned in the [official documentation](https://docs.python.org/3.7/using/cmdline.html#id5 "importtime documentation").
