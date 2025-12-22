FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install dependencies (using CPU version of torch to save space/time)
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download a small multilingual model to bake it into image
# We use a script to download it during build to speed up startup
RUN python -c "from transformers import pipeline; pipeline('ner', model='Davlan/bert-base-multilingual-cased-ner-hrl', aggregation_strategy='simple')"

COPY app .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
