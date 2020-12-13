#!coding: utf-8
import os
import json
from typing import Optional


def get_version_file(path: Optional[str] = None) -> str:
    """
    Return the full path to version.json file.

    By default, the file is looked within the package.

    :param path: path to be looked for version file (by default the package folder is used)
    :return: full path of version file
    """
    parent_dir = os.path.dirname(__file__)
    if path:
        parent_dir = path
    return os.path.join(parent_dir, "version.json")


def get_version_data(path: Optional[str] = None) -> dict:
    """
    Get version data of package. The version data includes:

    - the version number
    - the build number
    - the commit number

    :param path: path to be looked for version file (by default the package folder is used)
    :return: version data
    """
    version_file = get_version_file(path)
    data = {"version": "N/A", "build": "N/A", "commit": "N/A"}
    if os.path.exists(version_file):
        with open(version_file, mode="r", encoding="utf-8") as file_object:
            data = json.loads(file_object.read())
    return data


def version(path: Optional[str] = None) -> str:
    """
    Return the version number of the package.

    :param path: path to be looked for version file (by default the package folder is used)
    :return: version number
    """
    return get_version_data(path)["version"]


def build(path: Optional[str] = None) -> str:
    """
    Return the build number of the package.

    :param path: path to be looked for version file (by default the package folder is used)
    :return: build number
    """
    return get_version_data(path)["build"]


def commit(path: Optional[str] = None) -> str:
    """
    Return the commit identifier of the package.

    :param path: path to be looked for version file (by default the package folder is used)
    :return: commit identifier
    """
    return get_version_data(path)["commit"]
