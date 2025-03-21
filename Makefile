install:
	#install command
	pip install --upgrade pip &&\
		pip install -r requirements.txt
dev:
	#install dev command
	pip install -r requirements-dev.txt
format:
	#format code
	# black storeapi/*.py
lint:
	# pylint --disable=R,C storeapi/*.py
test:
	#test
	pip install httpx
	python -m pytest -vv --cov=storeapi --cov=main storeapi/tests/routers/test_*.py storeapi/tests/test_*.py
build:
	#build container
	docker build -t deploy-fastapi .
run:
	#run container
	docker run -p 127.0.0.1:8081:8081 deploy-fastapi
deploy:
	#deploy
all: install format lint test deploy