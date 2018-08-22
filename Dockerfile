FROM python:3.5

COPY . /

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

EXPOSE 80

WORKDIR /app

CMD python app.py