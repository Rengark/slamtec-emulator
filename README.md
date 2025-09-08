# Slamtec Robot API Emulator

This project is a Python-based emulator for the Slamtec Robot RESTful API, built using the Flask web framework. It simulates the robot's behavior based on the provided OpenAPI (Swagger) configuration file.

## Setup

1.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Emulator

1.  **Start the Flask server:**
    ```bash
    python app.py
    ```

2.  The server will start, typically on `http://127.0.0.1:1448`. You will see output in the console indicating that the server is running and which endpoints are available.

## How It Works

-   `app.py`: This is the main Flask application. It reads the API specification and creates a web endpoint for each defined path and method.
-   `mock_data.py`: This file simulates the robot's internal state. API calls will read from or write to the data structures in this file. You can modify the initial values here to test different scenarios.

You can now send HTTP requests to the running server (e.g., using `curl`, Postman, or another Python script) to interact with the emulated robot.
