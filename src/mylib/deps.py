#!coding: utf-8
"""
Look for project dependencies
"""
import os
import ast
import uuid
import json
from typing import Optional, Sequence, Callable, Union, Tuple, Mapping
import sys

import stdlib_list


def is_package(path: str) -> bool:
    """
    Stat whether given path is a Python package.

    :param path: path to be investigated
    """
    return os.path.isdir(path) and "__init__.py" in os.listdir(path)


def is_directory(path: str) -> bool:
    """
    Stat whether given path is a directory.

    :param path: path to be investigated
    """
    return os.path.isdir(path)


def is_module(path: str) -> bool:
    """
    Stat whether given path is a Python module.

    :param path: path to be investigated
    """
    return os.path.isfile(path) and path.endswith(".py")


def is_shared_object(path: str) -> bool:
    """
    Stat whether given path is a shared object.

    :param path: path to be investigated
    """
    return os.path.isfile(path) and path.endswith(".so")


def is_file(path: str) -> bool:
    """
    Stat whether given path is a file.

    :param path: path to be investigated
    """
    return os.path.isfile(path)


def build_tree(path: str, ignore_dirs: Optional[Sequence[str]] = None) -> dict:
    """
    Build a tree from a given path

    :param path: path to be investigated
    :param ignore_dirs: list of directory names to be excluded
    :return: tree
    """
    if ignore_dirs is None:
        ignore_dirs = []
    if is_module(path):
        key = uuid.uuid4().hex
        name = os.path.splitext(os.path.basename(path))[0]
        item = {key: {
            "name": name,
            "path": os.path.abspath(path),
            "components": [name],
            "type": "module",
        }}
        return item
    if is_shared_object(path):
        key = uuid.uuid4().hex
        name = os.path.basename(path).partition(".")[0]
        return {key: {
            "name": name,
            "path": os.path.abspath(path),
            "components": [name],
            "type": "shared_object"
        }}
    if is_file(path):
        key = uuid.uuid4().hex
        return {key: {
            "name": None,
            "path": os.path.abspath(path),
            "components": [None],
            "type": "file"
        }}
    if is_directory(path):
        key = uuid.uuid4().hex
        name = os.path.basename(path)
        item = {key: {
            "name": name if is_package(path) else None,
            "path": os.path.abspath(path),
            "components": [name] if is_package(path) else [None],
            "type": "package" if is_package(path) else "directory",
            "children": {}
        }}
        for child in os.listdir(path):
            if child not in ignore_dirs:
                child_path = os.path.join(path, child)
                info = build_tree(child_path, ignore_dirs)
                if info:
                    if "children" in item[key]:
                        apply_tree(info, lambda x: x["components"].insert(0, item[key]["name"]))
                    item[key]["children"].update(info)
        return item
    return {}


def apply_tree(tree: dict, func: Callable, args: Optional[Tuple] = None, kwargs: Optional[Mapping] = None) -> None:
    """
    Apply a function to all items in the specified tree.

    The function should take a single argument (the current item in the tree). The return value of the function is
    ignored. A deep-first-search algorithm is used.

    :param tree: tree to be browsed
    :param args: positional arguments to be passed to the callable
    :param kwargs: keyword arguments to be passed to the callable
    :param func: function to be applied to each item in the tree
    """
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    frontier = []
    explored = set()
    for uid, item in tree.items():
        frontier.append((uid, item))
    while frontier:
        uid, item = frontier.pop()
        func(item, *args, **kwargs)
        explored.add(uid)
        if "children" in item:
            for child_uid, child_item in item["children"].items():
                if child_uid not in explored:
                    frontier.append((child_uid, child_item))


def find_tree(tree: dict,
              func: Callable,
              args: Optional[Tuple] = None,
              kwargs: Optional[Mapping] = None,
              how: Optional[str] = "one"
              ) -> Union[Sequence[dict], dict, None]:
    """
    Find item in the specified tree. The function applied to the item searched must return True when the item is
    passed to the function. By default the first match is returned, but the how argument can be set to "all" to return
    a list of match.

    :param tree: tree to be investigated
    :param func: function to be applied to item
    :param args: positional arguments to be passed to the callable
    :param kwargs: keyword arguments to be passed to the callable
    :param how: either 'one' or 'all' depending in we want to get the first match or all of them
    :return: in case how='one' a single item (dict) is returned otherwise a list of items is returned
    """
    if how not in ["one", "all"]:
        raise ValueError("'how' must be set to either 'all' or 'one'")
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    if how == "one":
        result = _find_one_tree(tree, func, args, kwargs)
    else:
        result = _find_all_tree(tree, func, args, kwargs)
    return result


def _find_one_tree(tree: dict,
                   func: Callable,
                   args: Tuple,
                   kwargs: Mapping,
                   ) -> Union[dict, None]:
    """
    Find one item in the specified tree. The function applied to the item searched must return True when the item is
    passed to the function. By default the first match is returned.

    :param tree: tree to be investigated
    :param func: function to be applied to item
    :param args: positional arguments to be passed to the callable
    :param kwargs: keyword arguments to be passed to the callable
    """
    frontier = []
    explored = set()
    for uid, item in tree.items():
        frontier.append((uid, item))
    while frontier:
        uid, item = frontier.pop()
        explored.add(uid)
        if func(item, *args, **kwargs):
            return item
        if "children" in item:
            for child_uid, child_item in item["children"].items():
                if child_uid not in explored:
                    frontier.append((child_uid, child_item))


def _find_all_tree(tree: dict,
                   func: Callable,
                   args: Tuple,
                   kwargs: Mapping
                   ) -> Union[Sequence[dict], None]:
    """
    Find items in the specified tree. The function applied to the item searched must return True when the item is
    passed to the function.

    :param tree: tree to be investigated
    :param func: function to be applied to item
    :param args: positional arguments to be passed to the callable
    :param kwargs: keyword arguments to be passed to the callable
    :param how: either 'one' or 'all' depending in we want to get the first match or all of them
    :return: in case how='one' a single item (dict) is returned otherwise a list of items is returned
    """
    frontier = []
    explored = set()
    found = []
    for uid, item in tree.items():
        frontier.append((uid, item))
    while frontier:
        uid, item = frontier.pop()
        explored.add(uid)
        if func(item, *args, **kwargs):
            found.append(item)
        if "children" in item:
            for child_uid, child_item in item["children"].items():
                if child_uid not in explored:
                    frontier.append((child_uid, child_item))
    return found


def get_imports(path: str) -> dict:
    """
    This function parse the module at specified path to look for import statements and return a dictionary
    representing the import statement.

    :param path: path to the Python module
    :return: information related to the import statements
    """
    imports = {}
    with open(path, mode="r") as file_object:
        tree = ast.parse(file_object.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for module in node.names:
                imports[uuid.uuid4().hex] = {"name": module.name, "type": "import", "alias": module.asname}
        elif isinstance(node, ast.ImportFrom):
            for name in node.names:
                imports[uuid.uuid4().hex] = {"module": node.module, "name": name.name, "alias": name.asname,
                                             "type": "from-import", "level": node.level}
    return imports


def _build_fullname(tree: dict) -> None:
    """
    Generate fullname variable for items in tree from components variable

    :param tree: tree to be updated
    """
    def _apply(item: dict) -> None:
        components = item.pop("components")
        try:
            idx = components[::-1].index(None)
        except ValueError:
            pass
        else:
            components = components[len(components) - idx:]
        if components:
            item["fullname"] = ".".join(components)
        else:
            item["fullname"] = None
    apply_tree(tree, _apply)


def _build_imports(tree: dict) -> None:
    """
    Add imports variable in tree.

    :param tree: tree to be updated
    """
    def _apply(item: dict) -> None:
        if item["type"] == "module":
            item["imports"] = get_imports(item["path"])
    apply_tree(tree, _apply)


def _look_in_package(tree: dict, module_path: str, name: str, level: Optional[int] = None) -> Union[str, None]:
    """
    Look for target of an import in the package

    :param tree: tree to be investigated
    :param module_path: path to the module from which the imports are looked for
    :param name: name of the import
    :param level: ancestor level in the case of a relative import
    """
    parent_path = os.path.dirname(module_path)
    if level is not None:
        for _ in range(level - 1):
            parent_path = os.path.dirname(parent_path)
    parent = find_tree(tree, lambda x, p: x["path"] in [p, os.path.join(p, "__init__.py")], args=(parent_path,))
    if parent:
        if parent["fullname"] in [name, "{}.__init__".format(name)]:
            return parent["path"]
        for child in parent["children"].values():
            if child["name"] == name:
                return child["path"]
        target = find_tree(tree, lambda x, f: x["fullname"] == f, args=("{}.{}".format(parent["fullname"], name),))
        if target:
            return target["path"]
    return None


def _build_python_stdlib(stdlib_lookup: bool) -> set:
    """
    Build a set of Python standard libraries.

    :param stdlib_lookup: if set to false, an empty set is returned
    """
    if stdlib_lookup:
        version = "{}.{}".format(sys.version_info.major, sys.version_info.minor)
        python_stdlib = set(stdlib_list.stdlib_list(version))
        python_stdlib.add("__builtin__")
    else:
        python_stdlib = set()
    return python_stdlib


def _get_name_level_relative_import_module(import_module: dict) -> Tuple:
    """
    Get information for an import module object

    :param import_module: import module object
    """
    level = None
    name = None
    relative = False
    if import_module["type"] == "import":
        # We start with import using only import keyword, it can be an import of the form:
        # import module
        # import package.module
        name = import_module["name"]
    elif import_module["type"] == "from-import":
        # Now we deal with from keyword like in:
        # from package import module
        # from module import func
        # from .. import module
        if import_module["module"] is None:
            # This is the case for the following types of imports
            # from . import module (level 1)
            # from .. import module (level 2)
            name = import_module["name"]
            relative = True
        else:
            # This is the case for the following types of imports
            # from .module import func (level 1)
            # from ..module import func (level 2)
            name = import_module["module"]
        level = import_module["level"]
    return name, level, relative


def _build_lookup(tree: dict, stdlib_lookup: bool = False) -> None:
    """
    Add lookup variable in tree.

    :param tree: tree to be updated
    :param stdlib_lookup: toggle lookup to Python standard library
    """
    def _apply(item: dict, python_stdlib: set) -> None:
        if item["type"] == "module" and item["imports"]:
            package = item["fullname"].partition(".")[0]
            for import_module in item["imports"].values():
                import_module["lookup"] = None
                name, level, relative = _get_name_level_relative_import_module(import_module)
                # So we first try to find a module with the expected name in the same directory
                # We look the parent item of the current module
                target = _look_in_package(tree, item["path"], name, level=level)
                if target:
                    import_module["lookup"] = target
                else:
                    # We now look if a package or module has the same name (within the same package)
                    target = find_tree(
                        tree,
                        lambda x, n, p: (x["fullname"] == n) and (x["fullname"].partition(".")[0] == p),
                        args=(name, package)
                    )
                    if target:
                        import_module["lookup"] = target["path"]
                    elif relative:
                        # We haven't found so it might be a symbol imported by a package in __init__.py
                        # We don't want to let an internal reference as not found
                        import_module["lookup"] = "@internal"
                    elif name.partition(".")[0] == item["fullname"].partition(".")[0]:
                        # This is in case a module from within the same package has not been found
                        # We don't want to let an internal reference as not found
                        import_module["lookup"] = "@internal"
                    else:
                        # In last resort, we look for the package in the standard library
                        if name in python_stdlib:
                            import_module["lookup"] = "@stdlib"
    apply_tree(tree, _apply, args=(_build_python_stdlib(stdlib_lookup),))


def lookup_imports_tree(tree: dict, stdlib_lookup: bool = False) -> None:
    """
    Lookup for imports in specified tree.

    :param tree: tree to be investigated
    :param stdlib_lookup: toggle lookup to Python standard library
    """
    _build_fullname(tree)
    _build_imports(tree)
    _build_lookup(tree, stdlib_lookup)


def get_external_imports(tree: dict,
                         only_top_level: bool = True) -> set:
    """
    Get external imports from given tree

    :param tree: tree to be investigated
    :param only_top_level: only return the top-level package of dependency
    """
    external_imports = set()
    modules = find_tree(tree, lambda x: x["type"] == "module", how="all")
    for module in modules:
        for import_item in module["imports"].values():
            if import_item["lookup"] is None:
                if import_item["type"] == "import":
                    external_imports.add(import_item["name"])
                elif import_item["type"] == "from-import":
                    if import_item["module"] is not None:
                        external_imports.add(import_item["module"])
    if only_top_level:
        external_imports = {i.partition(".")[0] for i in external_imports}
    return external_imports


def get_dependencies(path: str,
                     ignore_dirs: Optional[Sequence[str]] = None,
                     include_stdlib: bool = False,
                     only_top_level: bool = True,
                     ) -> set:
    """
    Get all module / package dependencies for source code at given path.

    :param path: path of the source code to be analysed
    :param ignore_dirs: list of directory names to be ignored
    :param include_stdlib: toggle to include Python standard library in the dependencies
    :param only_top_level: only return the top-level package of dependency
    :return: set of dependencies
    """
    tree = build_tree(path, ignore_dirs=ignore_dirs)
    lookup_imports_tree(tree, stdlib_lookup=not include_stdlib)
    return get_external_imports(tree, only_top_level)


def write_tree(tree: dict, path: str) -> None:
    """
    Write tree in a json file at specified location.

    :param tree: tree to be writen
    :param path: path of the output json file
    """
    with open(path, mode="w", encoding="utf-8") as file_object:
        file_object.write(json.dumps(tree, indent=4))
