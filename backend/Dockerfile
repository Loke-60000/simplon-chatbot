# Using a specific version of Python image based on Alpine
FROM python:3.10-alpine3.14

# Set a working directory
WORKDIR /app

# Install necessary packages for Chromium and chromedriver
# Adding the edge repositories to ensure you get the latest packages for chromium
RUN echo @edge http://nl.alpinelinux.org/alpine/edge/community >> /etc/apk/repositories \
    && echo @edge http://nl.alpinelinux.org/alpine/edge/main >> /etc/apk/repositories \
    && apk add --no-cache \
    chromium@edge \
    chromium-chromedriver@edge

# Upgrade pip and install Python dependencies
# No-cache-dir for pip to keep the container small
RUN pip install --upgrade pip \
    && pip install --no-cache-dir fastapi uvicorn beautifulsoup4 selenium pydantic openai

# Copy the local code to the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
