#!make

export PYTHON_VERSION := 3.8

#SHELL := /bin/bash

install-dev:
	@+pipenv install --python ${PYTHON_VERSION} --dev

install:
	@+pipenv install --python ${PYTHON_VERSION}

test:
	pipenv run pytest -q main/test/tests.py
