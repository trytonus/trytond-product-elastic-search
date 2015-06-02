test: test-sqlite test-postgres test-flake8

test-sqlite: install-dependencies start-docker
	coverage run setup.py test
	coverage report -m --fail-under 100

test-postgres: install-dependencies start-docker
	python setup.py test_on_postgres

test-flake8:
	pip install flake8
	flake8 .

install-dependencies:
	CFLAGS=-O0 pip install lxml
	pip install -r dev_requirements.txt

start-docker:
	docker run -d -p 9200:9200 -p 9300:9300 openlabs/docker-elasticsearch
	sleep 10
