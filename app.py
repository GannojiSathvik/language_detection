from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import os
import requests
import io
from pydub import AudioSegment

app = Flask(__name__, static_folder='.')
CORS(app) # Enable CORS for all routes

def translate_audio(audio_file, language_code, SARVAM_API_KEY):
    if not SARVAM_API_KEY or SARVAM_API_KEY.strip() == "":
        raise ValueError("❌ Invalid API key. Please check your Sarvam AI key.")
    
    api_url = "https://api.sarvam.ai/speech-to-text-translate"
    headers = {"api-subscription-key": SARVAM_API_KEY}
    model_data = {"model": "saaras:v2", "with_diarization": False, "language_code": language_code}

    # Read audio data from the file-like object
    audio_segment = AudioSegment.from_file(audio_file)
    
    chunk_buffer = io.BytesIO()
    audio_segment.export(chunk_buffer, format="wav")
    chunk_buffer.seek(0)
    files = {'file': ('audiofile.wav', chunk_buffer, 'audio/wav')}

    try:
        response = requests.post(api_url, headers=headers, files=files, data=model_data)
        if response.status_code == 200 or response.status_code == 201:
            response_data = response.json()
            transcript = response_data.get("transcript", "")
            detected_language = response_data.get("language_code", "")
        elif response.status_code == 401 or response.status_code == 403:
            raise ValueError("❌ Invalid API key. Please check your Sarvam AI key.")
        else:
            raise RuntimeError(f"❌ Request failed with status code: {response.status_code}. Details: {response.text}")
    except Exception as e:
        raise e
    finally:
        chunk_buffer.close()

    return transcript, detected_language

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/transcribe', methods=['POST'])
def transcribe_audio_api():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['file']
    language_code = request.form.get('language_code', 'unknown')
    sarvam_api_key = request.headers.get('X-API-Key')

    if not sarvam_api_key:
        return jsonify({"error": "Sarvam AI Key is missing"}), 400

    try:
        transcript, detected_language = translate_audio(audio_file, language_code, sarvam_api_key)
        return jsonify({
            "transcript": transcript,
            "detected_language": detected_language
        })
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except RuntimeError as re:
        return jsonify({"error": str(re)}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
