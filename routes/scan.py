# from fastapi import APIRouter
# from drone_db import SessionLocal
# from model import Violation
# from fetcher import fetch_drones
# from main import report_violation

# # Create a new router that can be included in main.py
# router = APIRouter()

# # Function to check if a drone is in the no-fly zone
# def is_in_no_fly_zone(x: float, y: float) -> bool:
#     return x ** 2 + y ** 2 <= 1000 ** 2

# # Define an endpoint for GET /scan
# @router.get("/scan")
# async def scan_drones():
#     print(">>> /scan endpoint called")

#     # Fetch drone data from the external API (async HTTP request)
#     data = await fetch_drones()
#     print(">>> drones fetched:", data)

#     # Create a database session
#     db = SessionLocal()

#     # Iterate over the list of drones (adjust this if API structure differs)
#     for drone in data:
#         try:
#             x = drone["x"]
#             y = drone["y"]
#             z = drone.get("z", 0)
#             owner_id = drone.get("owner_id")

#             if owner_id is None:
#                 print(f"Skipping drone due to missing owner_id: {drone}")
#                 continue

#             # Check if the drone is in the no-fly zone
#             if is_in_no_fly_zone(x, y):
#                 print(f"Drone in restricted zone: x={x}, y={y}, z={z}, owner_id={owner_id}")

#                 # Create a violation record with the drone's data
#                 violation = Violation(
#                     x=x,
#                     y=y,
#                     z=z,
#                     owner_id=owner_id
#                 )
#                 # report_violation(violation, db)
#                 # db.add(violation)
#         except KeyError as e:
#             print(f"Malformed drone entry skipped: missing {e} in {drone}")

#     # Save all pending inserts to the database
#     db.commit()

#     # Close the database session
#     db.close()

#     # Return a success message
#     return {"message": "Scan complete"}
