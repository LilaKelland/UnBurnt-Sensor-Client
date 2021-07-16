install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

# test:
	# python -m pytest -vv --cov=papaoutai test_papaoutai.py 

format:
	black *.py

lint:
	pylint --disable=R,C unburnt.py

all: install lint test