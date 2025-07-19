from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

app.conf.beat_schedule = {
	'scan-every-10-seconds': {
		'task': 'scan_for_violations',  # ✅ matches the @app.task(name=...)
		'schedule': 10.0,
	},
}

app.conf.timezone = 'UTC'

import task
