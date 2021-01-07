import pytest

from importtime_output_wrapper import Import
from importtime_output_wrapper import parse_import_time
from importtime_output_wrapper import InvalidInput


imp_a0 = Import(name="a0", t_self=4, t_cumu=5, childs=[])
imp_a1 = Import(name="a1", t_self=3, t_cumu=4, childs=[])
imp_b0 = Import(name="b0", t_self=4, t_cumu=5, childs=[])
imp_b1 = Import(name="b1", t_self=3, t_cumu=4, childs=[])
imp_b = Import(name="b", t_self=2, t_cumu=3, childs=[imp_b0, imp_b1])
imp_a = Import(name="a", t_self=1, t_cumu=2, childs=[imp_a0, imp_a1])
root = Import(name="root", t_self=0, t_cumu=0, childs=[imp_a, imp_b])

test_tree = [root]

with open("tests/sample_importtime_output") as f:
    test_output_string = f.read()


@pytest.mark.parametrize(
    ("test_input", "expected"),
    ((test_output_string, test_tree),),
)
def test_parse_std_err(test_input, expected):

    assert parse_import_time(test_input) == expected


def test_parse_empty_std_err():
    with pytest.raises(InvalidInput):
        parse_import_time("")