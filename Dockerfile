# ----- Stage 1: Build -----
FROM ubuntu:24.04 as builder

# Install build dependencies
RUN apt-get update && apt-get install -y gcc

WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# ----- Stage 2: Production Image -----
FROM ubuntu:24.04 

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Update PATH so installed packages are available
ENV PATH="/install/bin:$PATH"

WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /install /install

# Copy your Django project code
COPY . /app

# Copy the entrypoint script and ensure it's executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Collect static files (ensure your settings are configured for production)
RUN python manage.py collectstatic --noinput

# Expose the port Gunicorn will listen on
EXPOSE 8000

# Use the entrypoint script as the container's startup command
CMD ["/app/entrypoint.sh"]
