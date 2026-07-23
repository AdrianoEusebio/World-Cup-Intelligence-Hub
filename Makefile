.PHONY: setup run test compose-up compose-down compose-build clean

setup:
	pip install -r requirements.txt
	playwright install chromium

run:
	python main.py

test:
	python -m unittest discover -s tests

compose-up:
	docker-compose up -d

compose-down:
	docker-compose down

compose-build:
	docker-compose build

clean:
	rm -rf __pycache__ .pytest_cache
