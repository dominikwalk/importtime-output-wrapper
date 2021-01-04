import re
import subprocess
import sys
import json
import argparse
from typing import List, Optional, Sequence


PATTERN_IMPORT_TIME = re.compile(r"^import time:\s+(\d+) \|\s+(\d+) \|(\s+.*)")


class InvalidInput(Exception):
    pass


class Import(dict):
    def __init__(self, name: str, t_self: int, t_cumu: int, childs: List):
        super().__init__()
        self.__dict__ = self
        self.name = name
        self.t_self_us = t_self
        self.t_cumulative_us = t_cumu
        self.nested_imports = childs


def get_import_time(module: str) -> List[Import]:
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

    root = Import("root", 0, 0, [])
    import_stack = [root]

    for line in reversed(ret.stderr.splitlines()):

        m = PATTERN_IMPORT_TIME.match(line)
        if m:
            t_self = int(m[1])
            t_cumu = int(m[2])
            name = str(m[3])
            new_imp = Import(name=name.strip(), t_self=t_self, t_cumu=t_cumu, childs=[])
            depth = int((len(name) - len(name.lstrip()) - 1) / 2) + 1

            for _ in range(len(import_stack) - depth):
                import_stack.pop()
            import_stack[-1].nested_imports.insert(0, new_imp)
            import_stack.append(new_imp)

    return [root]


def sort_imports(imports: List[Import], sort_by="self") -> List[Import]:
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

    exclude_root = imports[0]["nested_imports"]
    return json.dumps(exclude_root, indent=2)


def main(argv: Optional[Sequence[str]] = None) -> int:

    parser = argparse.ArgumentParser(
        description="""
        This script calls the python3 -X importtime implementation with a given module
        and parses the stderr output into a json format, which can then be used to
        search or display the given information.
    """
    )
    parser.add_argument("module", help="the module to import")
    parser.add_argument(
        "--sorted",
        nargs="?",
        choices=["self", "cumulative"],
        help="sort imported modules by import-time",
    )
    args = parser.parse_args(argv)

    all_imports = get_import_time(module=str(args.module))
    print(args)
    if args.sorted:
        output_imports = sort_imports(imports=all_imports, sort_by=args.sorted)
    else:
        output_imports = all_imports

    print(import_tree_to_json_str(output_imports))

    return 0


if __name__ == "__main__":
    exit(main())
