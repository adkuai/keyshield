📑 KeyShield — Enterprise API Gateway & Micro-SaaS Management Console
KeyShield is a production-grade, full-stack API Gateway and Credential Management Platform. It serves as a centralized developer control hub where software platforms can securely provision, rotate, and audit access tokens (API keys) while defending target infrastructure through sliding-window rate limiters and scope security firewalls.
Inspired by enterprise developer architectures like Stripe, Twilio, and Kong Gateway, KeyShield is engineered using an asynchronous Python backend, a relational database layer, and a highly responsive single-page frontend console.
🎛️ Architecture & Feature Ecosystem
• OAuth2 User Session Space (Days 1–5): Secure developer registration with cryptographic password hashing (pwdlib[bcrypt]) and stateful session tracking through signed JWT access tokens.
• Multi-Project Hierarchical Isolation (Days 6–8): Complete workspace logical isolation. A single user account can provision independent projects (e.g., Staging Pipeline vs. Mobile Production App), each bound to specific database rules.
• Dynamic Key Registry & Verification (Days 9–10): Cryptographic security mapping. Frontend views filter and expose only active, friendly Key Prefixes to minimize token leakage. The gateway verifies active tokens instantly via the backend engine.
• Fine-Grained Scope Enforcement (Days 11–13): Access tokens enforce granular endpoint privileges: READ, WRITE, and DELETE. Unauthorized method targets are terminated instantly using a 403 Forbidden firewall gate.
• Async Performance Metrics Auditing (Days 14–16): Request logging offloaded natively to FastAPI BackgroundTasks threads. Captures route paths, response codes, and microsecond latencies directly to PostgreSQL without slowing connections.
• Sliding-Window Rate Limiter (Days 17–19): Configurable RPM (Requests Per Minute) guards saved to the schema layer. If an external client floods your routes, the backend counts recent database records and applies an explicit 429 Too Many Requests block.
• Interactive Simulation Playground (Days 20–22): An embedded live playground console (mini-Postman) that connects inputs right to secure endpoint proxies, refreshing the analytics cards instantly on success.
📂 Repository File Directory Map
text
keyshield/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Manual empty module marker
│   │   ├── main.py              # Entrypoint, CORS configurations, Profiler middleware
│   │   ├── database.py          # SQLAlchemy Asyncio engine and pool context
│   │   ├── models.py            # PostgreSQL database relational table schemas
│   │   ├── schemas.py           # Pydantic data validation and serialization models
│   │   ├── dependencies.py      # Token auth, smart prefix matching, rate-limit check
│   │   └── routers/
│   │       ├── auth.py          # User registration and JWT credential engine
│   │       ├── projects.py      # Project tier provisioning and metrics aggregation
│   │       ├── keys.py          # API key minting, list loops, rotation handlers
│   │       └── gateway.py       # Protected sandbox routes & background tasks loggers
│   ├── tests/
│   │   ├── conftest.py          # Pytest isolated database test session setup
│   │   └── test_integration.py  # End-to-end endpoint verification scripts
│   ├── .env                     # Local environment file parameters
│   └── requirements.txt         # Core Python framework dependency lists
└── frontend/
    ├── src/
    │   ├── services/
    │   │   └── api.js           # Dynamic central API request abstraction client
    │   ├── App.jsx              # Main Single Page App UI view router console
    │   ├── index.css            # Tailwind directive loading imports
    │   └── main.jsx             # React Virtual DOM engine rendering root
    ├── index.html               # Frontend HTML shell template
    └── vite.config.js           # Vite development server configuration rules
Use code with caution.
🚀 Local Deployment & Running Guide
Follow these exact steps to clone, configure, and boot the entire platform on your local machine:
1. Setup Your Local PostgreSQL Databases
Open your terminal or pgAdmin, connect to your database engine, and run these two commands to create the target schemas:
sql
CREATE DATABASE keyshield_db;
CREATE DATABASE keyshield_test_db;
Use code with caution.
2. Configure and Run the Backend API Engine
Open a terminal tab, step cleanly inside your backend directory, initialize your Python environment, and start the application server:
bash
# Move to backend folder
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # On Mac/Linux use: source venv/bin/activate

# Install operational dependencies
pip install -r requirements.txt
Use code with caution.
Create a file named .env directly inside the backend/ directory and add your database configuration parameters:
text
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD_HERE@127.0.0.1:5432/keyshield_db
Use code with caution.
(Replace YOUR_PASSWORD_HERE with your actual local PostgreSQL superuser password).
Now, start your FastAPI hot-reloading development server:
bash
fastapi dev app/main.py
Use code with caution.
The API is now running natively on http://127.0.0.1:8000.
3. Run the Automated Tests (Optional Validation Check)
Open a separate terminal window, activate the virtual environment, and execute your test suite:
bash
cd backend
.\venv\Scripts\Activate.ps1
pytest -v
Use code with caution.
4. Configure and Run the React Frontend Console
Open a new, separate terminal window tab, navigate to your frontend directory, install your node modules, and launch the Vite compiler:
bash
# Move to frontend folder
cd frontend

# Install package dependencies
npm install

# Start the Vite local compiler engine
npm run dev
Use code with caution.
Open http://localhost:5173/ in your web browser.
🧪 Complete Platform Verification Protocol
1. Sign Up & In: Open the interface, register a clean email account profile, and log in to clear out any old local state cache lines.
2. Provision Tiers: Create a new tracking project (e.g., Core Engine Gateway) and set its rate limiting threshold to 60.
3. Mint Your Prefix Key: Type a reference name (e.g., Local Script Core), check READ and WRITE, and click Mint Key. Your active key prefix will populate inside your list table grid immediately.
4. Trigger the Playground Proxy: Copy your prefix key string directly from the registry grid loop. Scroll down to the simulator box, select POST, target path /products, paste your key into the header field slot, and click Send Request.
5. Observe Real-time Metrics: The panel will render a clean success code 201. Scroll back up to the top metrics strip panel—the graphs will automatically tick up from zero instantly, reflecting your live transaction calculations!

