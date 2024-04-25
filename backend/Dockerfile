FROM python:3.10-alpine

WORKDIR /app

RUN apk add --no-cache chromium chromium-chromedriver
RUN pip install --no-cache-dir fastapi uvicorn beautifulsoup4 selenium pydantic

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]