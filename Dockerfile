# This should not be UTF-8 BOM but ASCII
# because of a tiny ACR parser bug

FROM python:3.6

ADD app /app

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

EXPOSE 80

WORKDIR /app

CMD python app.py