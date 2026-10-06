KeyShield — Developer Setup & Run Guide 🚀
A streamlined deployment blueprint to clone, configure, and boot the KeyShield API Gateway Console on your local system using automated hot-reloading compilers and an isolated database layer.

🚀 Step-by-Step Running Instructions
# 1. Database Provisioning Layer
Open pgAdmin, connect to your local PostgreSQL server database node, and initialize the system storage instances:

sql

CREATE DATABASE keyshield_db;

CREATE DATABASE keyshield_test_db;

Use code with caution.

# 2. Configure & Boot the FastAPI Backend Engine

Open a new system terminal panel instance, step inside the backend workspace directory, activate a fresh virtual environment container, and install the required modules:

bash
# Navigate to the backend directory context

cd backend

# Create and isolate the virtual environment

python -m venv venv

.\venv\Scripts\Activate.ps1   # On macOS/Linux platforms execution syntax: source venv/bin/activate

# Install the Python framework dependencies list

pip install -r requirements.txt

Use code with caution.

Create a text configuration file named .env directly within the root of your backend/ folder and add your local PostgreSQL password parameter string:

text

DATABASE_URL=postgresql+asyncpg://postgres:YOUR_DB_PASSWORD@127.0.0.1:5432/keyshield_db

Use code with caution.

(Make sure to change YOUR_DB_PASSWORD to your actual local administrative database password).

Now, launch your asynchronous hot-reloading development server application:

bash

fastapi dev app/main.py

Use code with caution.

The core backend API engine is now listening for real-time traffic requests on http://127.0.0.1:8000.

# 3. Configure & Run the React UI Console

Open a second, completely separate terminal window panel (do not close your active backend server console), navigate to your frontend asset layout path, download your packages, and start the local compiler:

bash

# Navigate to the frontend directory context

cd frontend

# Download the node client package modules

npm install

# Activate the local Vite development server compiler engine

npm run dev

Use code with caution.

Open your web browser window to http://localhost:5173/ to interact with the full-stack developer cockpit app interface canvas!
