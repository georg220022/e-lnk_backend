FROM python:3.9

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD gunicorn  elink.wsgi:application --bind 0:8000