import multiprocessing
import os

bind = "0.0.0.0:" + os.getenv("PORT", "8000")
workers = int(os.getenv("GUNICORN_WORKERS", str(max(2, multiprocessing.cpu_count() // 2))))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
accesslog = "-"
errorlog = "-"
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gthread")
