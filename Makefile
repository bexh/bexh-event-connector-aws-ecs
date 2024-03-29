#!make

export PYTHON_VERSION := 3.8

#SHELL := /bin/bash

install-dev:
	@+pipenv install --python ${PYTHON_VERSION} --dev

install:
	@+pipenv install --python ${PYTHON_VERSION}

.PHONY: test
test:
	pipenv run pytest

docker-up:
	{ \
   	cd redis-docker ;\
   	docker-compose up -d ;\
	}

docker-down:
	{ \
	cd redis-docker ;\
	docker-compose down ;\
  	}

local-setup:
	python scripts/local_setup.py
