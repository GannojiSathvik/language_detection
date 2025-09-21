document.addEventListener('DOMContentLoaded', () => {
    // --- Element Selection ---
    const apiKeyInput = document.getElementById('api-key');
    const languageCodeSelect = document.getElementById('language-code');
    const startRecordingButton = document.getElementById('start-recording');
    const stopRecordingButton = document.getElementById('stop-recording');
    const audioFileInput = document.getElementById('audio-file-input');
    const transcriptionOutput = document.getElementById('transcription-output');
    const clearTranscriptionButton = document.getElementById('clear-transcription');
    const clearApiKeyButton = document.getElementById('clear-api-key');
    const mainContainer = document.querySelector('.main-container');
    const aboutSection = document.getElementById('about');
    const navLinks = document.querySelectorAll('.nav-link');
    const audioWave = document.getElementById('audio-wave');
    const fileNameDisplay = document.getElementById('file-name');

    let mediaRecorder;
    let audioChunks = [];
    let audioStream;

    // --- Dynamic UI Creation ---
    // Create audio wave bars dynamically
    for (let i = 0; i < 10; i++) {
        const bar = document.createElement('div');
        bar.classList.add('wave-bar');
        audioWave.appendChild(bar);
    }

    // --- API Key Management ---
    const saveApiKey = (key) => localStorage.setItem('sarvam_api_key', key);
    const loadApiKey = () => localStorage.getItem('sarvam_api_key');

    const savedApiKey = loadApiKey();
    if (savedApiKey) {
        apiKeyInput.value = savedApiKey;
    }

    // --- Event Listeners ---
    startRecordingButton.addEventListener('click', startRecording);
    stopRecordingButton.addEventListener('click', stopRecording);
    audioFileInput.addEventListener('change', handleFileUpload);
    clearTranscriptionButton.addEventListener('click', clearTranscription);
    clearApiKeyButton.addEventListener('click', clearApiKey);
    
    // --- Functions ---
    async function startRecording() {
        if (!apiKeyInput.value) {
            alert('Please enter your Sarvam AI Key first.');
            return;
        }
        try {
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(audioStream);
            audioChunks = [];

            mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                sendAudioToBackend(audioBlob, 'recording.wav');
            };

            mediaRecorder.start();
            updateUIForRecording(true);
            transcriptionOutput.value = '';
            transcriptionOutput.placeholder = 'Recording... Speak now.';
        } catch (error) {
            console.error('Error accessing microphone:', error);
            transcriptionOutput.placeholder = 'Error: Could not access microphone. Please grant permission.';
        }
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            audioStream.getTracks().forEach(track => track.stop());
            updateUIForRecording(false);
            transcriptionOutput.placeholder = 'Processing transcript...';
        }
    }

    function handleFileUpload(event) {
        const file = event.target.files[0];
        if (file) {
            fileNameDisplay.textContent = file.name; // Update displayed file name
            transcriptionOutput.value = '';
            transcriptionOutput.placeholder = `Uploading and transcribing ${file.name}...`;
            sendAudioToBackend(file, file.name);
        }
    }

    function clearTranscription() {
        transcriptionOutput.value = '';
        transcriptionOutput.placeholder = 'Awaiting audio...';
        audioFileInput.value = ''; // Reset file input
        fileNameDisplay.textContent = 'no file selected';
    }

    function clearApiKey() {
        apiKeyInput.value = '';
        localStorage.removeItem('sarvam_api_key');
    }

    function updateUIForRecording(isRecording) {
        startRecordingButton.style.display = isRecording ? 'none' : 'block';
        stopRecordingButton.style.display = isRecording ? 'block' : 'none';
        audioWave.style.display = isRecording ? 'flex' : 'none';
    }

    async function sendAudioToBackend(audioBlob, fileName) {
        const apiKey = apiKeyInput.value.trim();
        if (!apiKey) {
            transcriptionOutput.value = 'Error: Please enter your Sarvam AI Key.';
            transcriptionOutput.placeholder = 'Awaiting audio...';
            return;
        }
        saveApiKey(apiKey);

        const formData = new FormData();
        formData.append('file', audioBlob, fileName);
        formData.append('language_code', languageCodeSelect.value);
        
        try {
            const response = await fetch('/transcribe', {
                method: 'POST',
                headers: {
                    'X-API-Key': apiKey // Sending API key in headers is more secure
                },
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! Status: ${response.status}`);
            }
            
            const languageLabel = data.detected_language || 'Detected';
            transcriptionOutput.value = `(${languageLabel}) → ${data.transcript}`;
        } catch (error) {
            console.error('Error sending audio to backend:', error);
            transcriptionOutput.value = `Error: ${error.message}`;
        } finally {
            transcriptionOutput.placeholder = 'Awaiting audio...';
        }
    }

    // --- Navigation ---
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');

            if (targetId === '#about') {
                mainContainer.style.display = 'none';
                aboutSection.style.display = 'block';
            } else if (targetId === '#home') {
                mainContainer.style.display = 'block';
                aboutSection.style.display = 'none';
            }
        });
    });

    // --- Human UI: Light-beam effect on mouse movement ---
    const lightBeam = document.querySelector('.light-beam');
    if (lightBeam) {
        document.body.addEventListener('mousemove', (e) => {
            lightBeam.style.setProperty('--mouse-x', `${e.clientX}px`);
            lightBeam.style.setProperty('--mouse-y', `${e.clientY}px`);
        });
    }
});
