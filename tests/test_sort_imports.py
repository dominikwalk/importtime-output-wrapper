import pytest
from typing import List, Tuple

from importtime_output_wrapper import Import
from importtime_output_wrapper import sort_imports

imp_a0 = Import(name="a0", t_self=4, t_cumu=5, depth=2, childs=[])
imp_a1 = Import(name="a1", t_self=3, t_cumu=4, depth=2, childs=[])
imp_b0 = Import(name="b0", t_self=4, t_cumu=5, depth=2, childs=[])
imp_b1 = Import(name="b1", t_self=3, t_cumu=4, depth=2, childs=[])
imp_b = Import(name="b", t_self=2, t_cumu=3, depth=1, childs=[imp_b0, imp_b1])
imp_a = Import(name="a", t_self=1, t_cumu=2, depth=1, childs=[imp_a0, imp_a1])
root = Import(name="root", t_self=0, t_cumu=0, depth=0, childs=[imp_a, imp_b])

test_tree = [root]


def _get_time_order(tree: List[Import], time_select="self") -> List[Tuple[str, int]]:
    time_list = []

    def collect_time_recursive(children: List[Import]) -> None:
        nonlocal time_list
        for imp in children:
            if imp == []:
                return
            else:
                time = None
                if time_select == "self":
                    time = imp.t_self_us
                elif time_select == "cumu":
                    time = imp.t_cumulative_us
                if time:
                    time_list.append((imp.name, time))
                collect_time_recursive(imp.nested_imports)

    collect_time_recursive(tree)
    return time_list


@pytest.mark.parametrize(
    ("test_input", "expected"),
    (
        ("self", [("b", 2), ("b0", 4), ("b1", 3), ("a", 1), ("a0", 4), ("a1", 3)]),
        ("cumu", [("b", 3), ("b0", 5), ("b1", 4), ("a", 2), ("a0", 5), ("a1", 4)]),
    ),
)
def test_sort_imports(test_input, expected):
    sorted_tree = sort_imports(test_tree, sort_by=test_input)

    assert _get_time_order(sorted_tree, time_select=test_input) == expected
