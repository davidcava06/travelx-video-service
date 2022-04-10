SHELL = /bin/bash

update-deps:
	pip-compile --allow-unsafe --build-isolation --output-file requirements/main.txt requirements/main.in
	pip-compile --allow-unsafe --build-isolation --output-file requirements/dev.txt requirements/dev.in

install:
	pip install --upgrade -r requirements/main.txt
	pip install --upgrade -r requirements/dev.txt

add: update-deps install

lint:
	isort src
	black src
	flake8 src


api:
	FLASK_ENV=development flask run

.PHONY: lint install
