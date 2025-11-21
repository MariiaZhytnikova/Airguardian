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

### 🔐 Environment Variables

`.env` file used to securely store all necessary values.

   - external API URLs
   - required headers (e.g. API secrets) must match the values stored in your `.env` file. 

See `.env.example` for a reference and descriptions of each variable.

## 🚀 Run Instructions

### 🐳 1. Run the Entire App with Docker (recommended)

Make sure your .env file is configured (see .env.example).

Then start everything:

		make up

or

		docker compose up --build

Stop all services:

		make down

Check running containers:

		docker ps

### 2. API Endpoints
Once the app is running, you can access the following endpoints:

Swagger/OpenAPI Docs: 

	http://localhost:8000/docs

Health Check: 
	
 	http://localhost:8000/health

Drones API: 
	
 	http://localhost:8000/drones

No-Fly Zones API (This API requires a secret header for authorization, Make sure to set the `X-SECRET-KEY` in your `.env` file for successful requests): 

	http://localhost:8000/nfz

Real-time map: 

	http://localhost:8080/map-data

### 4. Run the Frontend (Static)
You can serve a static frontend using Python's built-in HTTP server:

```bash
cd static
python3 -m http.server 8080
```
Then open your browser to:
	
	http://localhost:8080/

