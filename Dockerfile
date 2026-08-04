FROM apify/actor-python:3.11

# Install dependencies first (better layer caching).
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code into /app (the image WORKDIR).
COPY . .

# Run the Actor. src/__main__.py is executed via `python -m src`.
CMD ["python", "-m", "src"]
