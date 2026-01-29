PORT ?= 8000

install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

ruff-check:
	uv run ruff check

build:
    ./build.sh

render-start:
    gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app