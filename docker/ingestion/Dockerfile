# 1. Start from an official image with Linux + Python 3.12 (small variant)
FROM python:3.12-slim

# 2. Create /app inside the image and make it the current folder
WORKDIR /app

# 3. Make Python print logs immediately instead of buffering them
ENV PYTHONUNBUFFERED=1

# 4. Install third-party libraries (slow, rarely changes → near the top)
RUN pip install --no-cache-dir requests==2.32.3 "psycopg[binary]==3.2.3" boto3==1.35.0

# 5. Copy project metadata and code (changes often → near the bottom)
COPY pyproject.toml ./
COPY src/ ./src/

# 6. Install OUR package only; its dependencies are already installed above
RUN pip install --no-cache-dir --no-deps .

# 7. Run the ingestion module
CMD ["python", "-m", "nyc_mobility.ingestion.main"]