
import json
import os
import io
import random

# Imports for the REST API
from flask import Flask, request, jsonify, make_response
from applicationinsights.flask.ext import AppInsights
from applicationinsights import TelemetryClient

# Imports for image procesing
from PIL import Image

# Imports for prediction
from predict import initialize, predict_image, predict_url

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['APPINSIGHTS_INSTRUMENTATIONKEY'] = os.environ.get('INSTRUMENTATION_KEY')

# log requests, traces and exceptions to Azure Application Insights
appinsights = AppInsights(app)

# 4MB Max image size limit
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

# Default route just shows simple text
@app.route('/')
def index():
    return 'CustomVision.ai model host harness'

# Like the CustomVision.ai Prediction service /image route handles either
#     - octet-stream image file 
#     - a multipart/form-data with files in the imageData parameter
@app.route('/image', methods=['POST'])
@app.route('/<project>/image', methods=['POST'])
@app.route('/<project>/image/nostore', methods=['POST'])
def predict_image_handler(project=None):
    operation_id = '%09x' % random.randrange(16**9)
    tc = app.wsgi_app.client
    tc._context.operation._values['ai.operation.id'] = operation_id
    try:
        imageData = None
        if ('imageData' in request.files):
            imageData = request.files['imageData']
        elif ('imageData' in request.form):
            imageData = request.form['imageData']
        else:
            imageData = io.BytesIO(request.get_data())

        print('\n\nOperation Id: {id}\n'.format(id=operation_id))

        img = Image.open(imageData)
        results = predict_image(img)

        predictions = {
            'tagName': results['predictions'][0]['tagName'],
            'confidence': results['predictions'][0]['probability']
        }

        tc.track_trace('Inference result for request {id}'
            .format(id=operation_id), predictions)

        resp = make_response(jsonify(results))
        resp.headers['X-Operation-Id'] = operation_id
        return resp
    except Exception as e:
        print('EXCEPTION:', str(e))
        return 'Error processing image', 500


# Like the CustomVision.ai Prediction service /url route handles url's
# in the body of hte request of the form:
#     { 'Url': '<http url>'}  
@app.route('/url', methods=['POST'])
@app.route('/<project>/url', methods=['POST'])
@app.route('/<project>/url/nostore', methods=['POST'])
def predict_url_handler(project=None):
    try:
        image_url = json.loads(request.get_data().decode('utf-8'))['url']
        results = predict_url(image_url)
        return jsonify(results)
    except Exception as e:
        print('EXCEPTION:', str(e))
        return 'Error processing image'

if __name__ == '__main__':
    # Load and intialize the model
    initialize()

    # Run the server
    listen_port = 8080 if os.environ.get('THIS_IS_DEV') else 80
    print('Listening on {p}/TCP.'.format(p=listen_port))
    app.run(host='0.0.0.0', port=listen_port)

