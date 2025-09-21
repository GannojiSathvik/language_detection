import gradio as gr
import time  
import numpy as np
import os
import requests
import io
from pydub import AudioSegment
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import websockets
import asyncio

SARVAM_API_KEY = "sk_22wujz2a_Bq5uscoXUbA4rnubZXmax0v6"

def translate_audio(audio, language_code):
    api_url = "https://api.sarvam.ai/speech-to-text-translate"
    headers = {"api-subscription-key": SARVAM_API_KEY}
    model_data = {"model": "saaras:v2", "with_diarization": False, "language_code": language_code}

    chunk_buffer = io.BytesIO()
    audio.export(chunk_buffer, format="wav")
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

def stream_transcribe(history, audio_data, language_code):
    if history is None:
        history = ""
        
    try:
        if audio_data is None:
            return history, "No audio data provided."
        
        if isinstance(audio_data, tuple):  # Streaming audio from microphone
            sr, y = audio_data
            if y.ndim > 1:
                y = y.mean(axis=1)
            y_int16 = y.astype(np.int16)
            audio_segment = AudioSegment(data=y_int16.tobytes(), sample_width=2, frame_rate=sr, channels=1)
        else:  # File upload
            if hasattr(audio_data, 'name') and audio_data.name:
                audio_segment = AudioSegment.from_file(audio_data.name)
            else:
                return history, "Invalid audio file."

        transcription, detected_language = translate_audio(audio_segment, language_code)
        history = history + '\n' + f'({detected_language})==> ' + transcription
        return history, history
    except ValueError as ve:
        return history, str(ve)
    except Exception as e:
        print(f"Error during Transcription: {e}")
        return history, str(e)

def clear():
    return ""

def clear_state():
    return None

def clear_api_key():
    return ""

def toggle_audio():
    return gr.update(visible=True)

# Custom CSS for an attractive, gradient-based design
custom_css = """
body {
    background: linear-gradient(135deg, #0a0e2a 0%, #2a2a6f 100%);
    font-family: 'Orbitron', sans-serif;
    margin: 0;
    padding: 0;
    color: #e0e0e0;
    animation: bgShift 15s infinite alternate;
}

@keyframes bgShift {
    0% { background-position: 0% 0%; }
    100% { background-position: 100% 100%; }
}

.gradio-container {
    width: 100vw !important;
    max-width: none !important;
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
}

.main-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
    padding: 2rem !important;
    background: rgba(10, 14, 42, 0.9);
    border-radius: 15px;
    box-shadow: 0 0 30px rgba(0, 255, 234, 0.3), 0 0 60px rgba(0, 255, 234, 0.1);
    min-height: 100vh;
    position: relative;
    overflow: hidden;
}

h1 {
    color: #00ffea;
    text-align: center;
    font-size: 3.5em;
    margin-bottom: 0.5rem;
    font-weight: 900;
    text-transform: uppercase;
    text-shadow: 0 0 10px #00ffea, 0 0 20px #00d4ff, 0 0 30px #00aaff;
}

.subheader {
    color: #00d4ff;
    text-align: center;
    font-size: 2.2em;
    margin-bottom: 2rem;
    font-weight: 700;
    text-shadow: 0 0 5px #00d4ff, 0 0 10px #00aaff;
    letter-spacing: 2px;
}

.header-section {
    background: linear-gradient(135deg, #00d4ff 0%, #00aaff 100%);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 212, 255, 0.5);
    position: relative;
    overflow: hidden;
}

.header-section::before {
    content: '';
    position: absolute;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(0, 255, 234, 0.3) 0%, transparent 70%);
    animation: pulse 6s infinite;
    top: -100px;
    left: -100px;
}

@keyframes pulse {
    0% { transform: scale(0.5); opacity: 0.5; }
    50% { transform: scale(1.5); opacity: 0.2; }
    100% { transform: scale(0.5); opacity: 0.5; }
}

.file-drop-zone {
    border: 2px dashed #00ffea;
    border-radius: 15px;
    padding: 2rem;
    text-align: center;
    background: rgba(0, 0, 0, 0.5);
    margin-bottom: 1rem;
    transition: all 0.3s ease;
    color: #00ffcc;
    box-shadow: 0 0 15px rgba(0, 255, 234, 0.3);
}

.file-drop-zone:hover {
    border-color: #00ffcc;
    background: rgba(0, 0, 0, 0.7);
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(0, 255, 204, 0.5);
}

.audio-button {
    background: linear-gradient(135deg, #ff4d4d 0%, #ff8c00 100%);
    color: white;
    border-radius: 15px;
    width: 300px; /* Increased width */
    height: 80px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8em;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 6px 20px rgba(255, 77, 77, 0.5), 0 0 15px rgba(255, 140, 0, 0.3);
    text-transform: uppercase;
    letter-spacing: 2px;
    padding: 0 1rem;
}

.audio-button:hover {
    transform: scale(1.05);
    background: linear-gradient(135deg, #ff3333 0%, #ff6600 100%);
    box-shadow: 0 8px 25px rgba(255, 77, 77, 0.7), 0 0 20px rgba(255, 140, 0, 0.5);
}

.input-section {
    background: rgba(0, 0, 0, 0.6);
    border-radius: 15px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

.textbox {
    border-radius: 10px !important;
    border: 1px solid #00ffea !important;
    background: rgba(0, 0, 0, 0.7) !important;
    padding: 1rem !important;
    font-size: 1.1em !important;
    color: #e0e0e0 !important;
    caret-color: #00ffcc !important;
    box-shadow: 0 0 10px rgba(0, 255, 234, 0.2);
}

.dropdown {
    border-radius: 10px !important;
    border: 1px solid #00ffea !important;
    background: rgba(0, 0, 0, 0.7) !important;
    padding: 0.5rem !important;
    color: #00ffcc !important;
    box-shadow: 0 0 10px rgba(0, 255, 234, 0.2);
}

.button {
    border-radius: 10px !important;
    background: linear-gradient(135deg, #00d4ff 0%, #00aaff 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.9rem 1.8rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    margin: 0 0.5rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
}

.button:hover {
    background: linear-gradient(135deg, #00ffcc 0%, #00d4ff 100%) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 6px 20px rgba(0, 255, 204, 0.6) !important;
}

.output-section {
    background: rgba(0, 0, 0, 0.8);
    border-radius: 15px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
    border-left: 5px solid #00ffcc;
}

.footer {
    text-align: center;
    color: #00d4ff;
    font-size: 1em;
    margin-top: 2rem;
    padding: 1rem;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.api-key-input {
    background: linear-gradient(135deg, #ff6f61 0%, #ff8a65 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(255, 111, 97, 0.4);
}
"""

with gr.Blocks(theme=gr.themes.Default(primary_hue="teal", secondary_hue="blue"), css=custom_css) as microphone:
    with gr.Column(elem_classes=["main-container"]):
        # Header section
        with gr.Row(elem_classes=["header-section"]):
            gr.Markdown("# 🎙️ LINGUASENSE", elem_classes=["header"])
            gr.Markdown("### **MULTILINGUAL SPEECH RECOGNITION**", elem_classes=["subheader"])
        
demo = microphone
app = FastAPI()

app.mount("/gradio", demo.app)

app.mount("/", StaticFiles(directory="app-project/client/build", html=True), name="static")

# To run this, you would typically use uvicorn:
# uvicorn app:app --reload --port 7860
# For this task, I will run it directly using the venv python.
# The Gradio interface will be available at /gradio
# The React frontend will be available at /

@app.websocket("/")
async def websocket_proxy(websocket: WebSocket):
    await websocket.accept()
    # The Gradio client expects a specific path for its WebSocket connection.
    # When Gradio is mounted at "/gradio", its WebSocket endpoint is typically "/gradio/queue/join"
    # The port should be the same as the FastAPI app.
    gradio_ws_url = f"ws://127.0.0.1:7860/gradio/queue/join" 

    try:
        async with websockets.connect(gradio_ws_url) as gradio_websocket:
            # Forward messages from frontend to Gradio backend
            async def forward_to_gradio():
                try:
                    while True:
                        message = await websocket.receive_text()
                        await gradio_websocket.send(message)
                except WebSocketDisconnect:
                    pass
                except Exception as e:
                    print(f"Error forwarding to Gradio: {e}")

            # Forward messages from Gradio backend to frontend
            async def forward_to_frontend():
                try:
                    while True:
                        message = await gradio_websocket.recv()
                        await websocket.send_text(message)
                except websockets.exceptions.ConnectionClosedOK:
                    pass
                except Exception as e:
                    print(f"Error forwarding to frontend: {e}")

            # Run both forwarding tasks concurrently
            await asyncio.gather(forward_to_gradio(), forward_to_frontend())

    except websockets.exceptions.ConnectionRefusedError:
        print(f"Gradio WebSocket connection refused at {gradio_ws_url}")
        await websocket.close(code=1011) # Internal Error
    except Exception as e:
        print(f"WebSocket proxy error: {e}")
        await websocket.close(code=1011) # Internal Error
