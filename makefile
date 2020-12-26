.PHONY: test dist install uninstall reqs pypi testpypi miniconda jenkins delete_miniconda

PACKAGE_NAME = mylib_template
LIB_NAME = mylib
MINICONDA = Miniconda3-latest-Linux-x86.sh
MINICONDA_URL = https://repo.anaconda.com/miniconda

install:
	pip install --upgrade .

uninstall:
	pip uninstall -y $(PACKAGE_NAME)

reqs:
	pipreqs --force

test:
	PYTHONPATH=src:${PYTHONPATH} pytest --cov=$(LIB_NAME) ./tests

tox:
	tox

pep8:
	-flake8
	-pylint src/

dist:
	rm -rf dist
	python setup.py sdist bdist_wheel

pypi:
	twine upload dist/*

testpypi:
	twine upload --repository testpypi dist/*

jenkins_miniconda:
	wget -q ${MINICONDA_URL}/${MINICONDA}
	sh ${MINICONDA} -u -b -p .miniconda
	rm -f ${MINICONDA}

jenkins_install_envs: jenkins_miniconda
	./.miniconda/bin/conda create -y -n py36 python=3.6
	./.miniconda/envs/py36/bin/pip install tox
	./.miniconda/bin/conda create -y -n py37 python=3.7
	./.miniconda/envs/py37/bin/pip install tox

jenkins_test: jenkins_install_envs jenkins_miniconda
	PATH=.miniconda/envs/py36/bin:.miniconda/envs/py37/bin:${PATH} tox

jenkins: jenkins_test
