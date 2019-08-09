FROM python:3

RUN apt-get update && apt-get -y install ghostscript && apt-get clean

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT} app:app -k eventlet --timeout 6000"]


