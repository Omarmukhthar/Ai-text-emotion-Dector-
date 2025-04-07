from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
from deep_translator import GoogleTranslator  # ✅ Install using: pip install deep-translator

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

@app.route('/')
def home():
    return render_template("index.html")  # Ensure index.html is inside the "templates" folder

@app.route('/analyze', methods=['POST'])
def analyze_text():
    try:
        data = request.json
        text = data.get("text")
        language = data.get("language", "en")  # Default to English if not provided

        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        print(f"✅ Received text: {text} | Language: {language}")

        # ✅ Translate text if it's not English
        if language != "en":
            lang_map = {
                "eg": "ar",  # ✅ Egyptian Arabic mapped to Standard Arabic
                "hi": "hi",
                "ta": "ta",
                "bn": "bn",
                "ml": "ml",
                "te": "te",
            }
            source_lang = lang_map.get(language, language)  # Default to provided language if not in map

            try:
                translated_text = GoogleTranslator(source=source_lang, target="en").translate(text)
                print(f"✅ Translated Text: {translated_text}")
            except Exception as e:
                print(f"⚠️ Translation Error: {e}")
                return jsonify({"error": "Translation failed", "details": str(e)}), 500
        else:
            translated_text = text  # If already English, use as-is

        # ✅ Emotion analysis via Hugging Face API
        url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

        candidate_labels = ["happy", "sad", "angry", "fearful", "surprised", "disgusted", "neutral", "love", "excitement", "boredom"]

        response = requests.post(url, headers=headers, json={
            "inputs": translated_text,  # ✅ Sending translated text for better accuracy
            "parameters": {"candidate_labels": candidate_labels}
        })

        print(f"✅ API Response: {response.text}")  # Debugging

        if response.status_code != 200:
            return jsonify({"error": "API request failed", "details": response.text}), 500

        result = response.json()

        return jsonify({
            "labels": result.get("labels", []),
            "scores": result.get("scores", [])
        })

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
