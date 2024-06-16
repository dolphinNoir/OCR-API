from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import requests
from io import BytesIO
from langdetect import detect_langs

app = Flask(__name__)


@app.route('/api/extract_text', methods=['POST'])
def extract_text():
    try:
        # Check if the request content type is JSON
        if not request.is_json:
            return jsonify(error="Unsupported Media Type: Content-Type must be application/json"), 415

        # Parse the JSON data from the request
        data = request.get_json()
        if 'image_url' not in data:
            return jsonify(error="Missing 'image_url' in request"), 400

        image_url = data['image_url']

        # Fetch the image from the URL
        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify(error="Could not retrieve image"), 400

        # Convert the image to a PIL Image
        image = Image.open(BytesIO(response.content))

        # Use pytesseract to extract text
        text = pytesseract.image_to_string(image)

        # Detect languages in the extracted text
        languages = detect_langs(text)
        detected_languages = [
            {
                "language": str(lang.lang),
                "probability": f"{lang.prob * 100:.2f}%"  # Format as a percentage with 2 decimal places
            }
            for lang in languages
        ]

        # Return the extracted text and detected languages as a JSON response
        return jsonify(text=text, detected_languages=detected_languages)

    except Exception as e:
        return jsonify(error=str(e)), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

