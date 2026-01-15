# Gunicorn configuration file
# This ensures the background worker runs in the WORKER process (not master)
# so it shares memory with the web request handlers.

import os

# Bind to PORT env var (Render sets this)
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Use only 1 worker - CRITICAL for shared state
workers = 1

# Use threads for handling multiple requests
threads = 2

# Don't preload - we want to start background worker AFTER fork
preload_app = False

# Timeout for requests (increase if OCI API is slow)
timeout = 120

# Access log format
accesslog = "-"
errorlog = "-"
loglevel = "info"


def post_fork(server, worker):
    """
    Called after a worker has been forked.
    Start the background worker here so it runs in the same process as web requests.
    """
    from web_app import start_background_worker
    print(f"[gunicorn] Worker {worker.pid} starting background worker...", flush=True)
    start_background_worker()
