# 1. Start from an official image with Linux + Python 3.12 (small variant)
FROM python:3.12-slim

# 2. Create /app inside the image and make it the current folder
WORKDIR /app

# 3. Make Python print logs immediately instead of buffering them
ENV PYTHONUNBUFFERED=1

# 4. Install libraries (slow, rarely changes → near the top)
#    We'll use `requests` later to download taxi data files.
RUN pip install --no-cache-dir requests==2.32.3 "psycopg[binary]==3.2.3" boto3==1.35.0
# 5. Copy our code from the Mac into the image (changes often → near the bottom)
COPY src/ ./src/

# 6. What to run when a container starts
CMD ["python", "src/nyc_mobility/ingestion/main.py"]