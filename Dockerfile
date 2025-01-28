FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY ig.py .
COPY s3.ini . 

# Create output directory
RUN mkdir -p /app/output

# Set output directory as volume
VOLUME /app/output

# Set entrypoint
ENTRYPOINT ["python", "ig.py"]
