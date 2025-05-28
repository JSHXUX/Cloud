from flask import Flask, render_template, jsonify, request, redirect
from google.cloud import firestore
from google.cloud import storage 
from datetime import timedelta
from google.oauth2 import service_account
import json
import base64 
import os
import openai
import env

app = Flask(__name__)
db = firestore.Client(project='rock-drake-456011-n4', database='images-metadata')
openai.api_key = env.openai_key

def get_credentials():
    b64_creds = env.google_key
    
    json_str = base64.b64decode(b64_creds).decode("utf-8")
    info = json.loads(json_str)
    credentials = service_account.Credentials.from_service_account_info(info)
    return credentials

credentials = get_credentials()
storage_client = storage.Client(credentials=credentials)
bucket_name = 'uploaded-images-data'


@app.route('/images')
def get_images():
    images_ref = db.collection('images')
    docs = images_ref.stream()
    data = [doc.to_dict() for doc in docs]
    return jsonify(data)

@app.route('/debug')
def debug_documents():
    docs = db.collection('images').stream()
    output = []
    for doc in docs:
        data = doc.to_dict()
        output.append(data)
    return jsonify(output)

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

    # Upload to GCS
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file)

    return jsonify({'success': True})


@app.route('/delete_image/<image_name>', methods=['DELETE'])
def delete_image(image_name):
    try:
        # Delete from Cloud Storage
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(image_name)
        blob.delete()

        # Delete from Firestore
        db.collection('images').document(image_name).delete()

        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def search_images_by_labels(labels):
    labels_lower = [label.lower() for label in labels]
    
    # 1. Căutare după PRIMA etichetă
    initial_query = db.collection('images').where('labels_lower', 'array_contains', labels_lower[0])
    docs = list(initial_query.stream())

    # 2. Filtrare locală pentru toate etichetele
    matching_docs = []
    for doc in docs:
        data = doc.to_dict()
        doc_labels = [label.lower() for label in data.get('labels_lower', [])]
        if all(label in doc_labels for label in labels_lower):
            matching_docs.append(doc)

    # 3. Dacă nu am găsit nimic, fac fallback pe OR logic
    if not matching_docs:
        fallback_query = db.collection('images').where('labels_lower', 'array_contains_any', labels_lower)
        matching_docs = list(fallback_query.stream())

    return matching_docs

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Traducerea în engleză
        translation_response = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates any text to fluent English."},
                {"role": "user", "content": f"Translate the following text to English: \"{user_message}\""}
            ],
            max_tokens=200,
            temperature=0,
        )
        user_message_en = translation_response['choices'][0]['message']['content'].strip()

        keywords = ['image', 'photo', 'picture', 'imagine', 'foto', 'photos', 'fotos', 'images', 'pictures', 'fotography', 'fotografie']
        if any(kw in user_message_en.lower() for kw in keywords):
            # Extrage etichete pentru căutarea imaginilor
        
            prompt_for_labels = (
            "You are an assistant that extracts main visual search labels from a sentence, ONLY if it refers to images, photos, or visual content.\n\n"
            "Your job is to:\n"
            "- Extract only the most important *key* nouns (no verbs, no general concepts).\n"
            "- Convert plural nouns to their singular form (e.g., 'cars' → 'car', 'dogs' → 'dog').\n"
            "- Return the result as a JSON list of lowercase singular strings, no extra text.\n"
            "- If there are no references to visual content, return an empty list.\n\n"
            "Examples:\n"
            "Text: \"Show me photos of cats and dogs\"\nOutput: [\"cat\", \"dog\"]\n\n"
            "Text: \"I want a picture of red cars and a tree\"\nOutput: [\"car\", \"tree\"]\n\n"
            "Text: \"I want images with an anime girl wearing a dress\"\nOutput: [\"anime girl\", \"dress\"]\n\n"
            "Text: \"I want a photography with a deer\"\nOutput: [\"deer\"]\n\n"
            "Text: \"Tell me a story about friendship\"\nOutput: []\n\n"
            "Text: \"I want to see all blue images.\"\nOutput: [\"blue\"]\n\n"
            f"Text: \"{user_message_en}\"\nOutput:"
            )

            label_response = openai.ChatCompletion.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You extract image search labels from text."},
                    {"role": "user", "content": prompt_for_labels}
                ],
                max_tokens=100,
                temperature=0,
            )
            import json
            try:
                labels = json.loads(label_response['choices'][0]['message']['content'].strip())
                if not isinstance(labels, list):
                    labels = []
            except json.JSONDecodeError:
                labels = []

            if not labels:
                # Dacă nu sunt etichete, nu găsim imagini
                return jsonify({'reply': "Sorry but I couldn't find an image for you.", 'images': []})

            # Căutare imagini în Firestore
            query = db.collection('images').where('labels_lower', 'array_contains_any', [label.lower() for label in labels])
            docs = query.stream()

            images_urls = []
            for doc in docs:
                data = doc.to_dict()
                image_name = data.get('imageName') or data.get('name')
                if not image_name:
                    continue
                # Generează URL semnat
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(image_name)
                signed_url = blob.generate_signed_url(
                    expiration=timedelta(hours=1),
                    method='GET',
                    credentials=credentials
                )
                images_urls.append(signed_url)

            if images_urls:
                return jsonify({
                    'reply': f"I found {len(images_urls)} image(s) matching your request.",
                    'images': images_urls
                })
            else:
                return jsonify({'reply': "Sorry but I couldn't find an image for you.", 'images': []})

        else:
            # Dacă nu cere imagini, răspuns normal GPT
            chat_response = openai.ChatCompletion.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You are a friendly assistant who always replies in English."},
                    {"role": "user", "content": user_message_en}
                ],
                max_tokens=200,
                temperature=0.7,
            )
            chat_reply = chat_response['choices'][0]['message']['content']
            return jsonify({'reply': chat_reply})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update-labels-lower')
def update_labels_lower_all():
    try:
        updated_docs = []
        docs = db.collection('images').stream()
        for doc in docs:
            data = doc.to_dict()
            labels = data.get('labels', [])
            labels_lower = [label.lower() for label in labels if isinstance(label, str)]
            doc.reference.update({'labels_lower': labels_lower})
            updated_docs.append(doc.id)
        return jsonify({"updated_docs": updated_docs})
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat_ui')
def chat_ui():
    return render_template('chat.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)