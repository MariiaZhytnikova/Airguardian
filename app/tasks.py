# from celery import shared_task
# from app.celery_app import app as celery_app
# import httpx
# from datetime import datetime
# from sqlalchemy.orm import Session

# from app.drone_db import SessionLocal
# from app.model import Violation, Owner
# from app.schemas import OwnerOut
# from app.utils import is_in_no_fly_zone, report_violation
# from app.config import settings


from datetime import datetime
import httpx
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.drone_db import SessionLocal, Base, engine
from app.model import Violation, Owner
from app.schemas import OwnerOut
from app.utils import is_in_no_fly_zone, report_violation
from app.config import settings


# Use settings instead of os.getenv
DRONES_LIST_API = settings.DRONES_LIST_API


@celery_app.task(name='scan_for_violations')
def scan_for_violations():
    db: Session = SessionLocal()
    try:
        response = httpx.get(DRONES_LIST_API, timeout=5)
        response.raise_for_status()
        data = response.json()

        for drone in data:
            try:
                x = drone["x"]
                y = drone["y"]
                z = drone.get("z", 0)
                drone_id = drone.get("id")
                owner_id = drone.get("owner_id")

                # skip missing owner_id
                if owner_id is None:
                    print(f"Skipping drone due to missing owner_id: {drone}")
                    continue

                owner_id = str(owner_id)

                if is_in_no_fly_zone(x, y):
                    print(
                        f"Drone in restricted zone: x={x}, y={y}, z={z}, "
                        f"drone_id={drone_id}, owner_id={owner_id}"
                    )

                    violation = Violation(
                        drone_id=drone_id,
                        owner_id=owner_id,
                        x=x,
                        y=y,
                        z=z,
                        timestamp=datetime.utcnow()
                    )

                    report_violation(violation, db)

            except KeyError as e:
                print(f"Malformed drone entry skipped: missing {e} in {drone}")
            except Exception as e:
                print(f"Error processing drone: {e}")

    except httpx.HTTPError as e:
        print(f"Drone fetch failed: {e}")
    finally:
        db.close()
