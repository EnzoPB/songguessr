FROM python:3-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt && pip3 cache purge

COPY . .

CMD [ "gunicorn", "-w" , "4", "-b", "0.0.0.0", "main:app"]