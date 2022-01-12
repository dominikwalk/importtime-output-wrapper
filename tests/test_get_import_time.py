import re

import pytest

from importtime_output_wrapper import get_import_time
from importtime_output_wrapper import InvalidInput

PATTERN_IMPORTTIME_HEADER = re.compile(
    r"import time: self [us] | cumulative | imported package",
)
PATTERN_IMPORT_TIME = re.compile(r"^import time:\s+(\d+) \|\s+(\d+) \|(\s+.*)")


@pytest.mark.parametrize(
    ("module_str", "module_only", "expected"),
    (("os", True, True), ("json", True, True), ("import os", False, True)),
)
def test_get_import_time_module(module_str, module_only, expected):
    std_out, std_err = get_import_time(module_str, module_only=module_only)
    std_err_lines = std_err.splitlines()
    valid_ret = False

    if PATTERN_IMPORTTIME_HEADER.match(std_err_lines[0]):
        valid_ret = True

    for line in std_err_lines[1:]:
        if PATTERN_IMPORT_TIME.match(line):
            valid_ret = True
        else:
            valid_ret = False
            break
    assert std_out == ""
    assert valid_ret == expected


@pytest.mark.parametrize(
    ("import_str", "expected"),
    (("import os; print('foobarbaz')", "foobarbaz\n"),),
)
def test_get_import_time_stdout(import_str, expected):
    std_out, _ = get_import_time(import_str, module_only=False)

    assert std_out == expected


def test_invalid_module_import():
    with pytest.raises(InvalidInput):
        get_import_time("foobarbaz", module_only=True)
