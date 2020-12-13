#!coding: utf-8
import os
import subprocess as sp
import json
import sys

import setuptools


# Generate a version file and get version number
def generate_version_file(dest="src/mylib/version.json") -> dict:
    """
    Automatically generate a version file for the package if run from source tree, otherwise re-use an existing version
    file.

    :return: version data
    """
    # We check if we are in the source tree
    in_source_tree = False
    try:
        commit = sp.check_output(args=["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
    except sp.CalledProcessError:
        commit = "N/A"
    else:
        in_source_tree = True

    # If we are not in source tree, we return the content of the already existing version file (if any)
    if not in_source_tree:
        source_dir = os.getcwd()
        version_file = os.path.join(source_dir, dest)
        if os.path.exists(version_file):
            with open(version_file, mode="r", encoding="utf-8") as file_object:
                version_data = json.loads(file_object.read())
        else:
            version_data = {"version": "N/A", "build": "N/A", "commit": "N/A"}
    # We are in the source tree so we re-generate a newer version file
    else:
        # Get package directory. Because pip will move to a temporary directory, the better way is to rely on the PWD
        # environment variable on Unix systems. For Windows, the cd variable is used instead
        if sys.platform == "win32":
            source_dir = os.environ["cd"]
        else:
            source_dir = os.environ["PWD"]

        # Get the path to the version file within the package
        version_file = os.path.join(source_dir, dest)

        # Get information from git command line
        try:
            build = sp.check_output(args=["git", "describe", "--tags", "--long"]).decode("utf-8").strip()
        except sp.CalledProcessError:
            build = "N/A"
            version = "N/A"
        else:
            version = build.split("-")[0].strip("vV")

        # Save version data to file
        version_data = {"version": version, "build": build, "commit": commit}
        with open(version_file, mode="w", encoding="utf-8") as file_object:
            data = json.dumps(version_data, indent=4)
            file_object.write(f"{data}\n")

    # Return version data
    return version_data


# Setup of package
setuptools.setup(
    version=generate_version_file()["version"],
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"mylib": ["version.json"]},
    python_requires=">=3.6",
)
