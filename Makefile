install:
	#install command
	pip install --upgrade pip &&\
		pip install -r requirements.txt
format:
	#format code
	black *.py storeapi/*.py
lint:
	pylint --disable=R,C *.py storeapi/*.py
test:
	#test
	pip install httpx
	python -m pytest -vv --cov=storeapi --cov=main test_*.py
build:
	#build container
run:
	#run container
	docker run -p 127.0.0.1:8081:8081 deploy-fastapi
deploy:
	#deploy
all: install post_install lint test deploy