# Use an official Python runtime as base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the application files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Start the Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]