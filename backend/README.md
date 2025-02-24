# Backend
The backend for the project. Runs a Flask server which calls functions from `core/`.

# Setup
1. Install the required packages using `pip install -r requirements.txt`.
   - **It is reccomended to use a virtual environment (`venv`) for this.**
2. Run `python3 server.py` to start the server. By default this runs on **port 5000**.

You will then need to enable the frontend locally, which is configured to communicate with this backend on port 5000. Please refer to the frontend README for more information on how to do this.