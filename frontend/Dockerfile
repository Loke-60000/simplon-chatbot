FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./frontend /app/frontend
COPY ./static /app/static

RUN pip install fastapi uvicorn

WORKDIR /app/frontend

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]