# Use Apify's official Python base image (ships Python + the apify SDK).
FROM apify/actor-python:3.11

# Copy the full repository so .actor/ specs and requirements.txt are available.
COPY . ./app

# Install dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Run the Actor.
CMD python -m src.main
