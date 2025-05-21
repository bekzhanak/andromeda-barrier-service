# Use slim Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependencies file and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app

# Run app using uvicorn
CMD ["uvicorn", "barrier_service:app", "--host", "0.0.0.0", "--port", "8000"]
