# Use a base image with Uvicorn and Gunicorn installed, suitable for FastAPI
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install necessary Python packages
RUN pip install fastapi uvicorn

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the current frontend directory contents to /app
COPY . /app

# Expose port 8001 for the application
EXPOSE 8001

# Command to run the application using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
