#!coding: utf-8
import os
from pprint import pprint
import json
import importlib
import sys

import pytest

from mylib.deps import build_tree, apply_tree, lookup_imports_tree, get_external_imports, write_tree


@pytest.fixture(scope="module")
def package01():
    return os.path.join(os.path.dirname(__file__), "data", "package1")


def test_build_tree_without_stdlib(package01):
    tree = build_tree(package01, ignore_dirs=["__pycache__"])
    lookup_imports_tree(tree, stdlib_lookup=False)
    assert get_external_imports(tree) == {"math", "os", "sample", "pandas"}


def test_build_tree_with_stdlib(tmpdir, package01):
    tree = build_tree(package01, ignore_dirs=["__pycache__"])
    lookup_imports_tree(tree, stdlib_lookup=True)
    assert get_external_imports(tree) == {"sample", "pandas"}
    write_tree(tree, str(tmpdir.join("tree.json")))


def test_numpy_dependencies(tmpdir):
    # print(importlib.machinery.PathFinder().find_spec("numpy", sys.path))
    path = os.path.dirname(importlib.util.find_spec("numpy").origin)
    tree = build_tree(path, ignore_dirs=["__pycache__", "tests", "_examples"])
    lookup_imports_tree(tree, stdlib_lookup=True)
    write_tree(tree, str(tmpdir.join("tree.json")))
    deps = get_external_imports(tree, only_top_level=True)
    assert "Numeric" in deps
    assert "code_generators" in deps
    assert "setuptools" in deps
    assert "mkl" in deps
    assert "nose" in deps
    assert "numarray" in deps
    assert "numpy_api" in deps
    assert "numpy_distutils" in deps
    assert "pickle5" in deps
    assert "pytest" in deps
    assert "psutil" in deps
    assert "scipy" in deps
    assert "numpy" not in deps


def test_mylib_dependencies(tmpdir):
    path = "./src"
    tree = build_tree(path, ignore_dirs=["__pycache__"])
    lookup_imports_tree(tree, stdlib_lookup=True)
    write_tree(tree, str(tmpdir.join("tree.json")))
    assert get_external_imports(tree, only_top_level=False) == {"stdlib_list"}


def test_pandas_dependencies(tmpdir):
    path = os.path.dirname(importlib.util.find_spec("pandas").origin)
    tree = build_tree(path, ignore_dirs=["__pycache__"])
    lookup_imports_tree(tree, stdlib_lookup=True)
    write_tree(tree, str(tmpdir.join("tree.json")))
    deps = get_external_imports(tree, only_top_level=True)
    pprint(deps)
    assert "IPython" in deps
    assert "PyQt4" in deps
    assert "PyQt5" in deps
    assert "bs4" in deps
    assert "dask" in deps
    assert "dateutil" in deps
    assert "lxml" in deps
    assert "matplotlib" in deps
    assert "numpy" in deps
    assert "openpyxl" in deps
    assert "pytest" in deps
    assert "pytz" in deps
    assert "scipy" in deps
    assert "sklearn" in deps
    assert "sqlalchemy" in deps
    assert "tables" in deps
    assert "xarray" in deps
    assert "xlrd" in deps
    assert "xlwt" in deps
    assert "xlsxwriter" in deps
    assert "pandas" not in deps
