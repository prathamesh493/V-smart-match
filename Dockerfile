# --- Stage 1: Build Stage ---
# Use a full Python image to build dependencies, which may require build tools.
FROM python:3.12 AS builder

# Set the working directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# 5. Copy ONLY the requirements file first to leverage Docker layer caching
# COPY requirements.txt .
COPY requirements.txt .


# 6. Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final/Production Stage ---
# Use the slim Python image for a smaller final image size
FROM python:3.12-slim

WORKDIR /app

# Create a non-root user for better security
# The 'app' user and 'app' group are created
RUN addgroup --system app && adduser --system --group app

# Create the Hugging Face cache directory and set permissions for the 'app' user
ENV HF_HOME=/app/huggingface_cache
RUN mkdir -p ${HF_HOME} && chown -R app:app ${HF_HOME}

# Copy pre-installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy the executables (like uvicorn) from the builder stage
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code into the final image
COPY . .

# --- FIX: Change ownership AFTER copying files ---
# This is the key change. It ensures the 'app' user owns all the code.
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Expose the port the app runs on
EXPOSE 8000

# Define the default command to run your application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]