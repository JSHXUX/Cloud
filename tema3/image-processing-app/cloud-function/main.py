import base64
import json
from google.cloud import vision
from google.cloud import firestore

def process_image(event, context):
    bucket = event['bucket']
    name = event['name']
    file_path = f"gs://{bucket}/{name}"

    vision_client = vision.ImageAnnotatorClient()

    firestore_client = firestore.Client(project='rock-drake-456011-n4', database='images-metadata')

    image = vision.Image(source=vision.ImageSource(image_uri=file_path))

    safe_search = vision_client.safe_search_detection(image=image).safe_search_annotation
    labels = vision_client.label_detection(image=image).label_annotations

    metadata = {
        'name': name,
        'safeSearch': {
            'adult': safe_search.adult,
            'violence': safe_search.violence,
            'racy': safe_search.racy,
        },
        'labels': [label.description for label in labels],
        'timestamp': firestore.SERVER_TIMESTAMP,
    }

    firestore_client.collection('images').document(name).set(metadata)
    print(f"Processed image: {name}")