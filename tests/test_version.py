#!coding: utf-8
import os

import pytest

import mylib


@pytest.fixture(scope="module")
def version_file_path():
    return os.path.join(os.path.dirname(__file__), "data")


def test_version(version_file_path):
    assert mylib.version.version(version_file_path) == "0.1.0"


def test_build(version_file_path):
    assert mylib.version.build(version_file_path) == "v0.1.0-3-g67b5a64"


def test_commit(version_file_path):
    assert mylib.version.commit(version_file_path) == "67b5a64f28768efddde516cc78b4ce92602c879b"
