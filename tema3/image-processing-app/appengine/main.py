from flask import Flask, render_template, jsonify, request, redirect
from google.cloud import firestore
from google.cloud import storage 
from datetime import timedelta
from google.oauth2 import service_account
import json
import base64 
import os

app = Flask(__name__)
db = firestore.Client(project='rock-drake-456011-n4', database='images-metadata')

# key_path = "image-processing-app/image-processing-app/appengine/service_account.json"

# credentials = service_account.Credentials.from_service_account_file(key_path)

def get_credentials():
    # b64_creds = 'ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAicm9jay1kcmFrZS00NTYwMTEtbjQiLAogICJwcml2YXRlX2tleV9pZCI6ICI1NDRjZjE1MzM5ZTlmZTliNjk2ZDczZmI0OGM3ZjYxZGMwMGY0NDA0IiwKICAicHJpdmF0ZV9rZXkiOiAiLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdkFJQkFEQU5CZ2txaGtpRzl3MEJBUUVGQUFTQ0JLWXdnZ1NpQWdFQUFvSUJBUUNtenNqaXN3ZGpVUTFXXG5TVW4yUGQwWkFPY3JmSzAzZXRmOS9XMmhmcUxKQ3NHUFFHWTIvV1Ftd3IxYll2cmxLTzhubStDd2lKQlpyVzFBXG56bm5ZeUhLVjNLR3pLK3FER3ZqakFYdWQ1eldMZ3BXclFXWE1zMlZZZUg4MFh0U0ZpU2QzZXhxdVFvQklid2pIXG5QbTNTc1N2d0dJL2cxeDRoV1FYbUtyenVRWXZ1Y05WTU4vN0xtM0svQUhkN2J0dlpKS2xrbnlJdzU2c3NGTDRWXG5WMVNoNHNxQngyQ09UMHlhSVlJWVhEWCtxMkc5YVBqSjJSanNyRTBHRHFPVmlvSUxqYk03Ymg1YnFyQ2l2QU8zXG4zSlZDaFBGYzF4K3AxT2c1cTFVL3ZPQ1lsUGM3RDBjYVFmUjRaV2t0QmFUN1NnaE9hNHpvVWI1YkdzOE8rdEplXG5yc0NscXF3ZkFnTUJBQUVDZ2dFQUNBeEV6SnJNVHl6aWJWaWFORFJFYzJ0dWtTa09YL1Y4dHhXUnRPaDRSVjdCXG4zdmJCbnRoYS9RbkNKZFUyRjhybFRNUEJzNFNBa0RJdlc2Q1hFcmNaaHRuTlRXakRTbi9zNjlQTGJzTHdlNVJnXG5lNjVBa1grMHVlRzZhc0MwditOOFVRbDlFNnBFQzk0cHh2dVkwazg3T0lRZTI2THh6UW5CV1g3TXRiK2cxeG42XG50Z0syS2Fpa1NaMjZTNzdmbW9pK1hlekxzM1R0TDFCTDFGdkJ3Q3dnSHYyQmh3NEJnZjRZRDZwK29FSzNMMCtZXG5HY3M4UUdoY2lYN3NHQmkxN3A1QlNVb0RjTEpIbWFDcWlCTzBjRUdvUCtPdkI1R09Kd25nZHBWdlJyYnRONmJDXG5MaWwrQnZxMXFZR1U0QkxlT2N5cnZtc1JVVmdSMEd2cUhkdjQ4dzBaZ1FLQmdRRE9EYTIwU0NqaWdmMmN1eG9PXG5iVno5NDlJcnFYZ2lNaFZYRE94eFEvd2tCcG1jVUlhRWUvT09ZRjVuUy9mYzFkUlRoSW5qM3FVa2haekw2ZmlTXG5WYnFkalNJY0lxTWVCb3RWckhzbUFCQWdaT2ZwcUdxeGxTU3ZzVWhQY0dpMVpBei9kZWpia21HUTROZFpRU2VOXG5QL1JYdE1IWDZxR2VZSXg0MDk5Znd6V0RnUUtCZ1FEUFBjYitvb0lTZVNFYkVjWnhCTGFRTkhyaEJIanpodFdGXG5CR0E2YTh2UFU1aDgxaEYxYzFFeXI4OUdiakFpWnZVa2Q4b2RPTjdpT0RUbTBuMFBJeitvdW5DRzMxVDU1UXgwXG5QN0RCSTM1bng4NnlpK0xPeE16L3IwNjZiVWtFbTQvSDBTeUo4N0FEc2JZRVlic0ZuRi80OUE2Nk1pQ3RETTA5XG5XRkZxYjdGL253S0JnRW1iSTBqNldmaUgvUU9tNXFqdXNrQlR5TGttSWE3OWV4Z01tczNmUGt2VU83MVdHcWRxXG42OWNaWDcvQXFIc3Z1MWhXU1Rlb1NnL2cxdUVVNUdISjFBOEI0b1J3YnhxRHRmUlYxK3Y4SzhhV3BTMlhwdjFtXG56S01pVGpWcWIwMFV2M3ZtTDlkMzAvaUFDUTF1TStYR1NjK20xM1A4OGR6MG1sbHpQaUVrUjVLQkFvR0FBMCtTXG5XVWtSV09nMGZqRTNnV0M0NWU3Z3M2MlZuUlpmWE9Pb0FlYnM5NS8zUks5SzBoeUloSTNJZXZDUnRrcjh5WnRjXG5VRUV6Vmx2ZGhINkNYdmFLTXREZnNWZnFESi83SmZSS2g1dGdqcG5qbEhpbG8vWUM3R2JKbERMZ3dzRVZkL1RBXG5pR2VyUFRQZW00MVFKcFBMK0xjMWNRWVIvWkhCeWFRYWtOKzk3ek1DZ1lCMmd0ditHbU5hNFB6dDFkVjJyc25QXG5ySFZHT1lxcXU0dTg1Q2VuOExFVVUyT3VkQUVLMC84YkhXNlJGam9kZUsyekk3bWtSZkZxWmRQNVZZcVRNZW93XG42SEgxeHpPZjVKUks4S2VUY3RvSWFYRGVoV0cxTjB0RUZkbisxN3E4YnNTRTB4MG91MEtvYzNVTHB5eGZzZ2ZHXG5GQmxjTldaU0xJZUt6TnYvWlJjUkx3PT1cbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsCiAgImNsaWVudF9lbWFpbCI6ICJyb2NrLWRyYWtlLTQ1NjAxMS1uNEBhcHBzcG90LmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllZW50X2lkIjogIjEwNzgxMjg5NDQ0MzEzODkyNDYyIiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YXRhdGEveDUwOS9yb2NrLWRyYWtlLTQ1NjAxMS1uNCU0MGFwcHNwb3QuZ3NlcnZpY2VhY2NvdW50LmNvbSIsCiAgInVuaXZlcnNlX2RvbWFpbiI6ICJnb29nbGVhcGlzLmNvbSIKfQo='
    b64_creds = os.environ.get("GOOGLE_CREDENTIALS_BASE64")
    
    json_str = base64.b64decode(b64_creds).decode("utf-8")
    info = json.loads(json_str)
    credentials = service_account.Credentials.from_service_account_info(info)
    return credentials

credentials = get_credentials()

storage_client = storage.Client(credentials=credentials)

bucket_name = 'uploaded-images-data'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/images')
def get_images():
    images_ref = db.collection('images')
    docs = images_ref.stream()
    data = [doc.to_dict() for doc in docs]
    return jsonify(data)

@app.route('/generate_signed_url/<image_name>')
def generate_signed_url(image_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(image_name)

    signed_url = blob.generate_signed_url(
        expiration=timedelta(hours=1),
        method='GET',
        credentials=credentials
    )

    return jsonify({'url': signed_url})

@app.route('/upload_images', methods=['POST'])
def upload_images():
    file = request.files['image']
    if not file:
        return 'No file uploaded.', 400

    bucket_name = 'uploaded-images-data'
    destination_blob_name = file.filename

    # Upload to GCS
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file)

    print(f"File {file.filename} uploaded to {bucket_name}.")

    return redirect('/')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)