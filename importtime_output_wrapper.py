import argparse
import json
import re
import shutil
import subprocess
import sys
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Sequence


PATTERN_IMPORT_TIME = re.compile(r"^import time:\s+(\d+) \|\s+(\d+) \|(\s+.*)")


class InvalidInput(Exception):
    pass


class Import(dict):
    def __init__(self, name: str, t_self: int, t_cumu: int, depth: int, childs: List):
        super().__init__()
        self.__dict__ = self
        self.name = name
        self.depth = depth
        self.t_self_us = t_self
        self.t_cumulative_us = t_cumu
        self.nested_imports = childs


def get_import_time(module: str) -> str:
    """
    Call the importtime function as subprocess, pass all selected modules
    and return the stderr output.
    """
    try:
        ret = subprocess.run(
            (sys.executable, "-Ximporttime", "-c", f"import {module}"),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            encoding="UTF-8",
        )
    except subprocess.CalledProcessError:
        raise InvalidInput(f'Invalid input: Could not import module "{module}"')

    return ret.stderr


def parse_import_time(s: str) -> List[Import]:
    """
    Recursively parse the importtime strderr output into a uniform tree structure.
    """
    root = Import("root", 0, 0, 0, [])
    import_stack = [root]

    for line in reversed(s.splitlines()):

        m = PATTERN_IMPORT_TIME.match(line)
        if m:
            t_self = int(m[1])
            t_cumu = int(m[2])
            name = str(m[3])
            depth = int((len(name) - len(name.lstrip()) - 1) / 2) + 1
            new_imp = Import(
                name=name.strip(),
                t_self=t_self,
                t_cumu=t_cumu,
                depth=depth,
                childs=[],
            )

            for _ in range(len(import_stack) - depth):
                import_stack.pop()
            import_stack[-1].nested_imports.insert(0, new_imp)
            import_stack.append(new_imp)
    if root.nested_imports == []:
        raise InvalidInput("Invalid input: could not parse any imports")
    return [root]


def prune_import_depth(
    imports: List[Import],
    depth: Optional[int] = None,
) -> List[Import]:
    """
    Prune the unified tree structure to the desired depth level.
    """

    def prune_children(childs: List[Import], depth: int):
        if childs == []:
            return
        if depth == 0:
            childs.clear()
        for imp in childs:
            prune_children(imp.nested_imports, depth - 1)

    if depth is not None:
        prune_children(imports, depth + 1)

    return imports


def sort_imports(imports: List[Import], sort_by="self") -> List[Import]:
    """
    Sort the unified tree structure according to the desired time key.
    """

    def sort_children(childs: List[Import]) -> None:
        if childs == []:
            return
        else:
            if sort_by == "self":
                childs.sort(key=lambda x: x.t_self_us, reverse=True)
            elif sort_by == "cumulative":
                childs.sort(key=lambda x: x.t_cumulative_us, reverse=True)

            for imp in childs:
                sort_children(imp.nested_imports)

    sort_children(imports)

    return imports


def import_tree_to_json_str(imports=List[Import]) -> str:
    """
    Print the imported modules tree in json format.
    """
    exclude_root = imports[0]["nested_imports"]
    return json.dumps(exclude_root, indent=2)


def import_tree_to_waterfall(imports=List[Import], time_key="self", width=79) -> str:
    """
    Print the imported modules tree as a waterfall diagram.
    """
    output_str = ""
    waterfall_output = []
    max_time = 0
    max_name_len = 0
    imp = NamedTuple("imp", [("name", str), ("space", int), ("time", int)])

    def create_name_str(childs: List[Import]) -> None:
        nonlocal max_time
        nonlocal max_name_len
        nonlocal waterfall_output
        nonlocal time_key
        if childs == []:
            return
        else:
            for child in childs:
                time = {"self": child.t_self_us, "cumulative": child.t_cumulative_us}[
                    time_key
                ]
                waterfall_output.append(
                    imp(name=child.name, space=child.depth - 1, time=time),
                )

                if time > max_time:
                    max_time = time
                if (len(child.name) + child.depth) > max_name_len:
                    max_name_len = len(child.name) + child.depth
                create_name_str(child.nested_imports)
        return

    create_name_str(imports[0]["nested_imports"])
    header = "module name" + " " * ((max_name_len + 1) - len("module name")) + " "
    header += " import time (us)" + "\n" + "-" * width + "\n"
    output_str += header

    for node in waterfall_output:
        name = node.space * "." + str(node.name)
        offset = ((max_name_len - len(name)) + 3) * " "
        time_str = str(node.time)
        water = "=" * int(
            (node.time / max_time)
            * (width - len(offset) - len(time_str) - len(name) - 2),
        )
        line_str = f"{name}{offset}{water}({time_str})\n"
        output_str += line_str

    min_width = round(1 / (node.time / max_time) + len(time_str) + len(name) + 2)
    if width < min_width:
        warning_msg = f"WARNING: The waterfall diagram may not be displayed correctly if the set width is too small!"
        output_str += warning_msg
    return output_str


def main(argv: Optional[Sequence[str]] = None) -> int:

    parser = argparse.ArgumentParser(
        description="""
        This script calls the python3 -X importtime implementation with a given module
        and parses the stderr output into a json format, which can then be used to
        search or display the given information. It can also display the data as a
        waterfall diagram in the terminal.
    """,
    )
    parser.add_argument("module", help="the module to import")

    parser.add_argument(
        "--format",
        nargs="?",
        default="json",
        choices=["json", "waterfall"],
        help="output format",
    )
    parser.add_argument(
        "--sort",
        nargs="?",
        choices=["self", "cumulative"],
        help="sort imported modules by import-time",
    )
    parser.add_argument(
        "--time",
        nargs="?",
        choices=["self", "cumulative"],
        help="time to use in waterfall format (default self)",
    )
    parser.add_argument(
        "--width",
        nargs="?",
        type=int,
        help="width of entries in waterfall format (default to "
        "environement variable COLUMNS or terminal's width)",
    )
    parser.add_argument(
        "--depth",
        nargs="?",
        type=int,
        help="limit depth of output format (default unlimited)",
    )

    args = parser.parse_args(argv)
    if args.time and args.format != "waterfall":
        parser.error(
            "--time requires format to be set to waterfall (--format waterfall)",
        )
    if args.width and args.format != "waterfall":
        parser.error(
            "--length requires format to be set to waterfall (--format waterfall)",
        )

    raw_output = get_import_time(module=str(args.module))
    all_imports = parse_import_time(raw_output)
    pruned_imports = prune_import_depth(all_imports, args.depth)

    if args.sort:
        output_imports = sort_imports(imports=pruned_imports, sort_by=args.sort)
    else:
        output_imports = pruned_imports

    if args.format == "json":
        print(import_tree_to_json_str(output_imports))
    elif args.format == "waterfall":
        width = args.width or shutil.get_terminal_size().columns
        time = args.time or "self"
        print(import_tree_to_waterfall(output_imports, time_key=time, width=width))

    return 0


if __name__ == "__main__":

    exit(main())
