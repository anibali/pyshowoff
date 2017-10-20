DCR?=docker-compose run --rm pyshowoff

test:
	$(DCR) python3 setup.py test

release:
	$(DCR) python3 setup.py sdist upload

install:
	pip install --upgrade .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .eggs/
