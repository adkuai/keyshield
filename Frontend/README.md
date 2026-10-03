# KeyShield — Enterprise API Gateway & Management Console
KeyShield is a production-grade, full-stack API Gateway and Credential Management Platform designed to handle authentication, usage tracking, fine-grained access control, and rate-limiting. Inspired by modern developer platforms like Stripe, Twilio, and Kong Gateway, KeyShield provides developers with a dynamic single-page dashboard to securely provision, rotate, and audit API keys while actively protecting target server resources through an asynchronous Python backend and a relational PostgreSQL datastore.

🚀 Local Deployment Guide
Follow this systematic setup sequence to configure and run the entire KeyShield application environment on your local machine:

# 1. Database Infrastructure Provisioning
Open your PostgreSQL terminal workspace or pgAdmin interface, connect to your active local engine instance, and execute the following commands to initialize the required development and testing schemas:

sql

CREATE DATABASE keyshield_db;

CREATE DATABASE keyshield_test_db;

# 2. Backend Environment Configuration & Server Boot

Navigate into the backend project workspace directory from your system terminal, initialize an isolated virtual python node environment, and install the underlying production dependencies:

bash

Move inside the backend directory context

cd backend

Initialize and activate the isolated virtual environment

python -m venv venv

.\venv\Scripts\Activate.ps1   # On macOS/Linux platforms execution syntax: source venv/bin/activate

Install structural framework packages

pip install -r requirements.txt

Create a file named .env directly within the root of the backend/ directory and populate it with your local system database parameters:

DATABASE_URL=postgresql+asyncpg://postgres:YOUR_DB_PASSWORD@127.0.0.1:5432/keyshield_db

Launch the asynchronous Uvicorn hot-reloading development server:

bash

fastapi dev app/main.py

# 3. Automated Testing Execution (Optional Verification)

To validate the structural data persistence integrity, authentication endpoints, and gateway checks automatically, open a parallel terminal shell and run the test suite:

bash

cd backend

.\venv\Scripts\Activate.ps1

pytest -v

# 4. React UI Dashboard Compilation & Boot

Open a final, independent terminal window session, navigate straight into your frontend client folder path, pull down the Node package modules, and start the local compiler engine:

bash

Step cleanly inside the frontend workspace

cd frontend

Install client-side module packages

npm install

Activate the local Vite development compiler engine

npm run dev
