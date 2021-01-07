from importtime_output_wrapper import import_tree_to_json_str
from importtime_output_wrapper import import_tree_to_waterfall
from importtime_output_wrapper import Import

import json
import re

imp_a0 = Import(name="a0", t_self=4, t_cumu=5, childs=[])
imp_a1 = Import(name="a1", t_self=3, t_cumu=4, childs=[])
imp_b0 = Import(name="b0", t_self=4, t_cumu=5, childs=[])
imp_b1 = Import(name="b1", t_self=3, t_cumu=4, childs=[])
imp_b = Import(name="b", t_self=2, t_cumu=3, childs=[imp_b0, imp_b1])
imp_a = Import(name="a", t_self=1, t_cumu=2, childs=[imp_a0, imp_a1])
root = Import(name="root", t_self=0, t_cumu=0, childs=[imp_a, imp_b])

test_tree = [root]


def test_import_tree_to_json():
    test_json_output = import_tree_to_json_str(test_tree)
    json.loads(test_json_output)


def test_import_tree_to_waterfall():
    test_waterfall_output = import_tree_to_waterfall(test_tree).splitlines()

    PATTERN_HEADER_LINE0 = re.compile(r"module name\s*\| import time \(us\)")
    PATTERN_HEADER_LINE1 = re.compile("-" * 79)

    PATTERN_WATERFALL_LINE = re.compile(r".+\s+[=]+\(\d+\)\s*")

    valid_output = False

    if (PATTERN_HEADER_LINE0.match(test_waterfall_output[0])) and (
        PATTERN_HEADER_LINE1.match(test_waterfall_output[1])
    ):
        print(test_waterfall_output[0])
        valid_output = True

    for line in test_waterfall_output[2:]:
        if not PATTERN_WATERFALL_LINE.match(line):
            valid_output = False

    assert valid_output == True