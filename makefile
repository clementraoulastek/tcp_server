run:
	python -m src

lint:
	python -m isort . --profile black
	python -m black .
	python -m pylint src