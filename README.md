# Airguardian
A secure and ef- ficient system will ensure real-time detection of unauthorized drones, helping protect restricted airspace.


pip install fastapi uvicorn requests pydantic psycopg2-binary celery python-dotenv
pip3 install uvicorn


▶️ Run the server

In terminal, run:

python3 -m uvicorn main:app --reload

🔹 Here’s what it means:
Part	Meaning
uvicorn	Runs your FastAPI app (it's the web server)
main:app	main is the file name (main.py), app is the FastAPI instance inside it
--reload	Auto-reloads the server if you change the code (useful during development)

✅ STEP-BY-STEP ROADMAP FOR BEGINNERS
📍 Phase 0: Basic Setup

You’ll need to install the necessary tools first.
1. Create a project folder

mkdir drone-nfz-backend
cd drone-nfz-backend

2. Create a virtual environment

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

3. Install required libraries

pip install fastapi uvicorn requests pydantic psycopg2-binary celery python-dotenv

📦 STEP 1: FastAPI Basics

Create a file called main.py:

from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"success": "ok"}

Run the API:

uvicorn main:app --reload

Visit: http://localhost:8000/health
🧠 STEP 2: Understand the Requirements

Here’s what you’ll build:
Feature	Tools you'll use
API backend	FastAPI
Data models & validation	Pydantic
Periodic data fetching	Celery + requests
Background processing	Celery + Redis
Database	PostgreSQL
Logging + error handling	Python logging, FastAPI features
Protected endpoint	FastAPI + headers + .env
🗃️ STEP 3: Setup Database (PostgreSQL)

    Install PostgreSQL or use Docker.

    Create a database named e.g. drone_db.

    Install SQLAlchemy to connect FastAPI to Postgres:

pip install sqlalchemy

    Create database.py:

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/drone_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

📌 STEP 4: Drone Model & Violation Logic

You’ll define a Violation table and write a function that:

    Fetches drones from https://drones-api.hive.fi/drones/

    Checks if drone is in the no-fly zone (x² + y² <= 1000²)

    If yes → get owner data and save in database.

🔁 STEP 5: Background Task with Celery

    Install Redis and run it (you can use Docker).

    Setup Celery to run a job every 10 seconds.

    Celery task will fetch drone data, detect violations, and store them.

🌐 STEP 6: More API Endpoints

    /drones → Fetches and returns live drone data.

    /nfz → Returns violations in the past 24h. Requires secret in header.

🔒 STEP 7: .env File for Secret & DB URL

Create a .env file:

X_SECRET=supersecret123
DATABASE_URL=postgresql://user:password@localhost/drone_db

🔧 STEP 8: Error Handling & Logging

Use Python’s logging module and FastAPI’s RequestValidationError handlers.
🔚 Final Result

You’ll have a working backend that:

✅ Fetches drone data
✅ Detects violations
✅ Stores to database
✅ Offers 3 API endpoints
✅ Is secured with a header
✅ Uses background tasks
✅ Handles errors and logs events
👉 Want a working file/folder template to begin with?

I can generate a ready-to-go skeleton (with main.py, models.py, database.py, etc.) for you. Just say “yes”, and I’ll build it for you.







✅ 1. API Backend

Tool: FastAPI

FastAPI helps you:

    Define routes like /health, /drones, /nfz

    Return structured JSON data

    Handle input and output easily

🧠 FastAPI = the skeleton of your web app.
✅ 2. Data Models & Validation

Tool: Pydantic (used by FastAPI)

Pydantic helps you:

    Define models for data, like:

    class Drone(BaseModel):
        x: float
        y: float
        z: float
        owner_id: str

    Validate incoming data is correct (types, required fields)

    Structure response data (for consistency)

🧠 Think of Pydantic as data security and cleanliness.
✅ 3. Periodic Data Fetching

Tool: Celery + requests

You need to:

    Fetch live drone data every 10 seconds

    Do this in the background

Celery = background task runner
requests = makes HTTP requests to external APIs

🧠 Celery helps automate and repeat this fetch process, even if the server is busy.
✅ 4. Background Processing

Tool: Celery + Redis

Celery needs a message broker to run properly — usually Redis.

    Redis is a lightweight in-memory server that queues tasks

    Celery connects to Redis and runs your function (like: "check drones for NFZ violation")

🧠 Redis = "task queue brain", Celery = "worker doing the tasks"
✅ 5. Database

Tool: PostgreSQL (with SQLAlchemy)

You’ll:

    Save drone violations into a table

    Each record will contain:

        Position

        Time

        Owner info

Use:

    psycopg2 to connect

    SQLAlchemy to define models/tables

🧠 PostgreSQL stores your data. Without it, you’d lose violations every time the app restarts.
✅ 6. Logging & Error Handling

Tool: Python logging, FastAPI exception tools

You’ll handle things like:

    What if the drone API is down?

    What if owner data is missing?

    What if the request is bad?

Use logs to debug or monitor:

import logging
logging.info("Drone checked")

🧠 Logs = app diary. Errors = clean feedback to users.
✅ 7. Protected Endpoint

Tool: FastAPI + .env + Header checking

You don’t want /nfz (with private owner data) to be public.

Solution:

    Store a secret in .env

    Require a custom header X-Secret in the request

    Block if missing or incorrect

🧠 Like a password for access.
🧠 TL;DR — WHO DOES WHAT?
Feature	Purpose	Tool(s)
API routing	Endpoints like /drones, /nfz	FastAPI
Data validation	Ensure clean inputs/outputs	Pydantic
Periodic fetching	Get drone positions every 10s	Celery + requests
Background tasking	Run tasks outside main server	Celery + Redis
Database storage	Save violations permanently	PostgreSQL + SQLAlchemy
Logging & errors	Handle problems and debugging	logging + FastAPI
Secured access	Block unauthorized data views	Header + .env
