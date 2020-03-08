import uuid
import time
import json
from base64 import b64decode
from google.cloud import vision
from google.cloud import storage
from google.cloud.vision_v1 import enums
from google.cloud.vision_v1 import ImageAnnotatorClient
from google.cloud.vision_v1 import types
from flask import Flask, request, jsonify
from flask import render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Get GCS bucket
storage_client = storage.Client()
bucket = storage_client.bucket('ocr_input_bucket')
result_bucket = storage_client.bucket('ocr_results_bucket')

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/uploadajax', methods=['POST'])
def user_update_avatar():
    # Make sure we have an image in the request
    #print(request.form)
    data_uri = request.form['data_uri']
    
    header, encoded = data_uri.split(",", 1)
    data = b64decode(encoded)

    with open("images/temp.png", "wb") as uploadedImage:
        uploadedImage.write(data)
    
    #print(uploadedImage)
    
    if not uploadedImage:
        return jsonify(
        {'error': 'Missing image, can not change avatar'}
        )
    try:
        #filename =  str(time.time()*1000) + '_' + uploadedImage.filename 
        #filename = uploadedImage.filename
        blob = bucket.blob('temp.png')
        blob.upload_from_filename('images/temp.png')
        return jsonify({
        'filename': 'temp.png'
        }), 200

    except Exception as e:
        return jsonify({
        'error': 'Could not create image data'
        }), 500

@app.route('/fetchdetails', methods=['POST'])
def fetchdetails():
    # Make sure we have an image in the request
    if request.method == "POST":
        filename=request.form['filename']
        for blob in storage_client.list_blobs(result_bucket, prefix=filename):
            json_data = blob.download_as_string()
            return jsonify({'text':json_data.decode('utf-8')}), 200, {'ContentType':'application/json'} 

if __name__ == '__main__':
    app.run()