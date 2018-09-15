# Monkey Business customvision.ai Classifier

## How to build:

    docker build -t <your image name> .

## How to run locally:

    docker run -p 127.0.0.1:80:80 -e INSTRUMENTATION_KEY=<app insights key> -d <your image name>

Then use your favorite tool to connect to the end points.

### POST as multipart/form-data using the imageData key &mdash;

    curl -X POST http://127.0.0.1/image -F imageData=@image.jpg

### POST as application/octet-stream &mdash;

    curl -X POST http://127.0.0.1/image -H "Content-Type: application/octet-stream" --data-binary @some_file_name.jpg

### POST http://127.0.0.1/url with image URL as body &mdash;

    curl -X POST http://127.0.0.1/url -d '{ "url": "<image url>" }'
