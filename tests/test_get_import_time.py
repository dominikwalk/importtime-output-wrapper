import pytest
import re

from importtime_output_wrapper import get_import_time
from importtime_output_wrapper import InvalidInput

PATTERN_IMPORTTIME_HEADER = re.compile(
    r"import time: self [us] | cumulative | imported package"
)
PATTERN_IMPORT_TIME = re.compile(r"^import time:\s+(\d+) \|\s+(\d+) \|(\s+.*)")


@pytest.mark.parametrize(("module_str", "expected"), (("os", True), ("json", True)))
def test_get_import_time(module_str, expected):
    ret = get_import_time(module_str).splitlines()
    valid_ret = False

    if PATTERN_IMPORTTIME_HEADER.match(ret[0]):
        valid_ret = True

    for line in ret[1:]:
        if PATTERN_IMPORT_TIME.match(line):
            valid_ret = True
        else:
            valid_ret = False
            break

    assert valid_ret == expected


def test_invalid_module_import():
    with pytest.raises(InvalidInput):
        get_import_time("foobarbaz")
