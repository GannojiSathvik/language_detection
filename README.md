# Language Detection Project

This project is a full-stack application designed for language detection. It features a Python-based backend for processing language detection requests and a React-based frontend for user interaction.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Language Detection API**: A robust backend API capable of identifying the language of input text.
- **User-Friendly Interface**: A modern web interface built with React for submitting text and viewing detection results.
- **Scalable Architecture**: Separated frontend and backend components for easier development and deployment.

## Technologies Used
### Backend
- Python
- Flask (or similar web framework, inferred from `app.py`)

### Frontend
- React
- JavaScript/TypeScript
- npm/Yarn

## Setup Instructions

Follow these steps to get the project up and running on your local machine.

### Backend Setup

1.  **Navigate to the project root**:
    ```bash
    cd /Users/gannojisathvik/Documents/adp
    ```
2.  **Install Python dependencies**:
    It is recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt # Assuming a requirements.txt exists or will be created
    ```
    *(If `requirements.txt` does not exist, you may need to install Flask and any other dependencies manually, e.g., `pip install Flask`)*
3.  **Run the backend server**:
    ```bash
    python app.py
    ```
    The backend server should now be running, typically on `http://127.0.0.1:5000`.

### Frontend Setup

1.  **Navigate to the frontend directory**:
    ```bash
    cd app-project/client/linguasense-dark
    ```
2.  **Install Node.js dependencies**:
    ```bash
    npm install
    ```
3.  **Start the frontend development server**:
    ```bash
    npm start
    ```
    The frontend application should open in your browser, typically on `http://localhost:3000`.

## Usage

1.  Ensure both the backend and frontend servers are running as per the setup instructions.
2.  Open your web browser and navigate to the frontend URL (e.g., `http://localhost:3000`).
3.  Enter the text you wish to analyze into the provided input field.
4.  Submit the text to see the detected language.

## Contributing

Contributions are welcome! Please follow these steps:
1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -am 'Add new feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Create a new Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. *(Assuming an MIT license, create a LICENSE file if one does not exist)*
