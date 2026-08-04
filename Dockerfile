# Apify's official Python base image. Its ONBUILD step copies the repo into
# /app and runs `pip install -r requirements.txt` automatically, so we don't
# need (and must not add) a manual COPY/install that would target the wrong dir.
FROM apify/actor-python:3.11

# The base image runs `python -m src` by convention, which executes
# src/__main__.py (renamed from main.py to match that convention).
