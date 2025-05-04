FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies including poppler-utils for PDF processing
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p data/resumes data/job_descriptions

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Expose the port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "app.main"]