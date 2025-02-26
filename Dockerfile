FROM ubuntu:24.04

# Install build dependencies
RUN apt-get update && apt-get install -y gcc python3 python3-venv python3-dev python3-pip

WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN python3 -mvenv /app/env
RUN /app/env/bin/pip install --upgrade pip && \ 
/app/env/bin/pip install -r requirements.txt

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy your Django project code
COPY . /app

# Copy the entrypoint script and ensure it's executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Collect static files (ensure your settings are configured for production)
RUN /app/env/bin/python manage.py collectstatic --noinput

# Expose the port Gunicorn will listen on
EXPOSE 8000

# Use the entrypoint script as the container's startup command
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]
