# Airguardian
A secure and efficient system will ensure real-time detection of unauthorized drones, helping protect restricted airspace.

### 🛰️ Project Overview

This project is a FastAPI-based backend system that performs the following tasks:

- 📡 **Collects drone position data** (`x`, `y`, `z`) from an external API at scheduled intervals.
- 🚫 **Detects violations** when a drone enters a **1,000-unit No-Fly Zone (NFZ)** radius centered at `(0, 0)`.
- 👤 **Fetches owner information** from a separate API, but **only for drones that violated the NFZ**.
- 🐘 **Stores violations** in a PostgreSQL database under a table named `violations`.
- 🌐 **Exposes API endpoints** to:
  - Retrieve real-time drone data.
  - Retrieve violations detected within the **last 24 hours**.
  - Draws a real-time map of drone positions, including NFZ boundaries and detected violations.

## 🛠️ Requirements

### 🧩 Dependencies

Make sure you have the following packages installed (e.g. via `poetry` or `pip`):

	- fastapi (>=0.110.0,<0.111.0)
	- uvicorn (>=0.29.0,<0.30.0)
	- httpx (>=0.27.0,<0.28.0)
	- sqlalchemy (>=2.0,<3.0)
	- asyncpg (>=0.29.0,<0.30.0)
	- python-dotenv (>=1.0.1,<2.0.0)
	- requests (>=2.32.4,<3.0.0)
	- psycopg2-binary (>=2.9.10,<3.0.0)
	- celery (>=5.5.3,<6.0.0)
	- redis (>=6.2.0,<7.0.0)

## 📥 Installation of Dependencies

### 🛠️ Installing with Poetry

Poetry is used for dependency management and packaging.

📌 Poetry installation:

	curl -sSL https://install.python-poetry.org | python3 -

After installation, restart your terminal or run:

	export PATH="$HOME/.local/bin:$PATH"

Verify the installation:

	poetry --version
 
💡 Install dependencies with pyproject.toml

	poetry install

 ### 🔧 Install dependencies manually with pip

	pip install \
	  fastapi>=0.110.0,<0.111.0 \
	  uvicorn>=0.29.0,<0.30.0 \
	  httpx>=0.27.0,<0.28.0 \
	  sqlalchemy>=2.0,<3.0 \
	  asyncpg>=0.29.0,<0.30.0 \
	  python-dotenv>=1.0.1,<2.0.0 \
	  requests>=2.32.4,<3.0.0 \
	  psycopg2-binary>=2.9.10,<3.0.0 \
	  celery>=5.5.3,<6.0.0 \
	  redis>=6.2.0,<7.0.0

### 🔐 Environment Variables

`.env` file used to securely store all necessary values.

   - external API URLs
   - required headers (e.g. API secrets) must match the values stored in your `.env` file. 

See `.env.example` for a reference and descriptions of each variable.

## 🚀 Run Instructions

### 🐘 1. Start PostgreSQL with Docker

If PostgreSQL database not yet created:

	docker run --name database_name \
	  -e POSTGRES_USER=user_name \
	  -e POSTGRES_PASSWORD=user_password \
	  -e POSTGRES_DB=database_name \
	  -p 5432:5432 \
	  -d postgres

Where user_name, user_password, database_name should correspond data from .env (see .env.example for reference)

	DATABASE_URL=postgresql://user_name:user_password@localhost:5432/database_name

Start the existing PostgreSQL container (e.g., database_name):

```bash
	docker start database_name
```

Verify that it's running:
```bash
	docker ps
```

To stop PostgreSQL running in Docker, use command:
```bash
	docker stop database_name
```

To stop delete PostgreSQL database:
```bash
	docker rm database_name
```

### 2. Run the Backend App
Using uvicorn directly:
```bash
	uvicorn app.main:app --reload
```

If you're using Poetry:
```bash
	poetry run uvicorn app.main:app --reload
```
🔄 The --reload flag enables automatic code reload on changes (useful in development).
Show the Process Using Port 8000 (in case you need to kill them)
```bash
	lsof -i :8000
```

### ⚙️ 2. Start Celery service for 

Celery is used to run background tasks, such as periodically checking for drone violations and saving them to the database.

Using Celery directly:
```bash
	celery -A celery_app worker --beat --loglevel=info
```

If you're using Poetry:
```bash
	poetry run celery -A app.celery_app worker --beat --loglevel=info
```
This command starts both the worker and the beat scheduler. The worker processes tasks, and beat periodically triggers scheduled jobs (like fetching drone data).

### 3. API Endpoints
Once the app is running, you can access the following endpoints:

Swagger/OpenAPI Docs: 

	http://localhost:8000/docs

Health Check: 
	
 	http://localhost:8000/health

Drones API: 
	
 	http://localhost:8000/drones

No-Fly Zones API (This API requires a secret header for authorization, Make sure to set the `X-SECRET-KEY` in your `.env` file for successful requests.): 

	http://localhost:8000/nfz

Real-time map: 

	http://localhost:8080/map-data

### 4. Run the Frontend (Static)
You can serve a static frontend using Python's built-in HTTP server:

```bash
cd static
python3 -m http.server 8080
```
Then open your browser to: http://localhost:8080/

