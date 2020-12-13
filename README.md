<a id="Top"></a>
[![PyPI](https://img.shields.io/pypi/v/mylib-template?logo=pypi&logoColor=yellow)](https://pypi.org/project/mylib-template/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mylib-template?logo=python&logoColor=yellow)](https://pypi.org/project/mylib-template/)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/mylib-template)](https://pypi.org/project/mylib-template/)
[![PyPI - Format](https://img.shields.io/pypi/format/mylib-template)](https://pypi.org/project/mylib-template/)
[![GitHub](https://img.shields.io/github/license/ccampguilhem/python-project-template)](https://github.com/ccampguilhem/python-project-template/blob/master/LICENSE)

[![Build Status](https://travis-ci.org/ccampguilhem/python-project-template.svg?branch=master)](https://travis-ci.org/ccampguilhem/python-project-template)
[![Coveralls github](https://img.shields.io/coveralls/github/ccampguilhem/python-project-template?logo=coveralls)](https://coveralls.io/github/ccampguilhem/python-project-template)
[![Codecov](https://img.shields.io/codecov/c/github/ccampguilhem/python-project-template?logo=codecov)](https://codecov.io/gh/ccampguilhem/python-project-template)

[![GitHub issues](https://img.shields.io/github/issues-raw/ccampguilhem/python-project-template)](https://github.com/ccampguilhem/python-project-template/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/ccampguilhem/python-project-template)](https://github.com/ccampguilhem/python-project-template/commits/master)
[![Lines of code](https://img.shields.io/tokei/lines/github/ccampguilhem/python-project-template)](https://github.com/ccampguilhem/python-project-template)

# A template for Python projects

As I spent a lot of time to set up my projects in Python, I wanted to have a reference guiding me through the process.

The purpose of this project is just to suggest a layout for Python projects including:

- source code organization
- tests and test coverage
- dependencies 
- deployment (installation, upload to PyPi or Conda)
- documentation and deployment
- code analysis (linting)

## Source code organization

I tend to prefer having a `src` directory in the source tree. If the package is a pure Python package, then the package 
lays directly in the `src` folder. Otherwise, I add another level using `python` folder. C or Fortran extensions are 
then stored respectively in `c` and `fortran` folders.

The layout looks like this:

```text
- src
    - mylib
        - __init__.py
        - ...
- tests
- README.md
- LICENSE
- setup.py
- setup.cfg
- .gitignore
- .travis.yml
- requirements.txt
```

Or with a non-Python extension:

```text
- src
    - python 
        - mylib
            - __init__.py
            - ...
    - c
        - include
        - src
- tests
- README.md
- LICENSE
- setup.py
- setup.cfg
- .gitignore
- .travis.yml
- requirements.txt
```

## Dependencies

To generate the `requirements.txt` file, simply use `pipreqs`:

```bash
# pip
pip install pipreqs
# conda
conda install -c conda-forge pipreqs
```

Then, from within the source tree:

```bash
pipreqs
```

## Distribution

I have followed the tutorial provided [here](https://packaging.python.org/tutorials/packaging-projects/) to 
configure the package deployment and installation. This is using the 
[setuptools](https://setuptools.readthedocs.io/en/latest/) library.

Make sure to have the latest version of setuptools:

```bash
# pip
pip install --upgrade setuptools wheel
# conda
conda install setuptools wheel
```

The version, build and commit identifier are automatically collected when running the `setup.py` module. It is 
assumed that the project is using git as revision control system.

To install the package from the source tree, you can simply use pip:

```bash
pip install .
```

Or you can install the package such as Python looks into your source tree for the latest version:

```bash
pip install --editable .
```

To uninstall the package:

```bash
pip uninstall mylib_template
```

The full list of classifiers can be found [here](https://pypi.org/pypi?%3Aaction=list_classifiers).

## Upload

### To Python Package Index (PyPi)

This package is uploaded into Test PyPi, the procedure is the following one:

Make sure to create an account by going [here](https://test.pypi.org/account/register/) for Test PyPi or 
[here](https://pypi.org/account/register) for PyPi. 
Then generate an API token from the account settings.
Store the Token API into the `$HOME/.pypirc` configuration file:

```ini
[testpypi]
username = __token__
password = pypi-...
[pypi]
username = __token__
password = pypi-...
```

Then make sure you have `twine` installed:

```bash
# pip
pip install --upgrade twine
# conda
conda install twine
```

Build the distribution packages you want to upload:

```bash
python setup.py sdist bdist_wheel
```

Finally, upload with twine either on Test PyPi or PyPi:

```bash
twine upload --repository testpypi dist/*
twine upload dist/*
```

Now it's uploaded, you can install with the following command line depending on where the package is hosted:

```bash
pip install -i https://test.pypi.org/simple/ mylib-template
pip install mylib-template
```

### To conda-forge

To come...

## Shields

You can use service from [Shield IO](https://shields.io/) to add badges to your project. Example of badges are included 
on [top](#Top) of this README.md file

## Tests

I use [pytest](https://docs.pytest.org/en/stable/) for testing, the test cases are collected into the `tests` folder. 
To run the tests from the source tree

```bash
PYTHONPATH=./src:${PYTHONPATH} pytests ./tests
```

If instead you want to run tests for the installed version:

```bash
pytests ./tests
```

## Continuous integration

To set up test-on-build with Travis CI:

- Go the Travis CI [home page](https://travis-ci.org/signin) and authenticate with your GitHub account
- In your profile settings, make sure the repository of your package is activated
- Your project requires a `.travis.yml` file so that Travis CI builds and run tests for your project. You can 
follow the documentation from [here](https://docs.travis-ci.com/user/languages/python/) to set up a configuration file.
  
An example of .travis.yml file is provided below:

```yaml
language: python
python:
  - "3.6"      # current default Python on Travis CI
  - "3.7"
  - "3.8"
install:
  - pip install -r requirements.txt
script:
  - pytest ./tests
```

You can check that the web hook for GitHub has been created. Go to the settings of the project in GitHub and check that 
you have a web hook registered for Travis CI. Travis CI gets notified whenever a new commit is submitted to GitHub.

## Test coverage

### Using Travis CI

#### Travis CI configuration

Whatever the solution used to display the coverage, the Travis CI configuration shall be updated in the following way:

```yaml
install:
  - pip install pytest-cov
script:
  - PYTHONPATH=src:{PYTHONPATH} pytest --cov=mylib ./tests
```

**Note**: to be able to make the connection between the coverage report and the source code, the tests have to be 
run in the source tree (without any installation of the package).

This enables to run pytest with generation of a coverage report. The coverage report can then be sent to one of the two 
following websites for display.

#### Coveralls

To get status of test coverage with [Coveralls.io](https://coveralls.io/), several steps are required, as described 
[here](https://code-maven.com/coverall-with-python-minimal-setup):

- Go to Coveralls website: https://coveralls.io/ and authenticate using your GitHub account.
- Add the repository you want to have covered by Coveralls.
- Then update the `.travis.yml` file like this:

```yaml
install:
  - pip install coveralls
after_success:
  - coveralls -v
```

- Finally, add a badge to the README.md file.

**Note**: there is no need to use an API token when working with Travis CI.

#### Codecov

To get status of test coverage with [Codecov](https://about.codecov.io/), several steps are required:

- Go to Codecov website: https://about.codecov.io/ and authenticate using your GitHub account.
- Add the repository you want to have covered by Codecov.
- Then update the `.travis.yml` file like this:

```yaml
after_success:
  - bash <(curl -s https://codecov.io/bash)
```

- Finally, add a badge to the README.md file.

**Note**: there is no need to use an API token when working with Travis CI.

### Using Jenkins

To come...

## Documentation

To come...

## Code analysis

To come...

