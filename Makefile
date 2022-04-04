SHELL = /bin/bash

update-deps:
	pip-compile --allow-unsafe --build-isolation --generate-hashes --output-file requirements/main.txt requirements/main.in
	pip-compile --allow-unsafe --build-isolation --generate-hashes --output-file requirements/dev.txt requirements/dev.in

install:
	pip install --upgrade -r requirements/dev.txt
	pip install --upgrade -r requirements/main.txt

setup:
	pip install --upgrade pip-tools pip setuptools

develop: setup update-deps install

add: update-deps install

lint:
	isort functions/
	black functions/
	flake8 functions/

.PHONY: update-deps install develop lint
