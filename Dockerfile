FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir gunicorn && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
ENV FLASK_ENV=production

EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 2 run:app
