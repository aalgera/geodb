FROM python
WORKDIR /app
RUN pip install --upgrade pip \
 && pip install psycopg2 fastapi uvicorn python-multipart
COPY ./app /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
