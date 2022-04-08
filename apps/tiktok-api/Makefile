SHELL = /bin/bash

lint:
	isort src tests
	black src tests
	flake8 src tests

install:
	poetry install --no-dev

install-dev:
	poetry install

.PHONY: lint install
