# Make hook for a runnable dashboard or small application.
# It runs scripts/dashboard/serve.py, which uses only the Python standard library
# and listens only on this computer. Change `dashboard` to the name of the application.

.PHONY: dashboard  ## Start the dashboard at http://127.0.0.1:8000 (PORT=9000 changes the port)
dashboard:
	python3 scripts/dashboard/serve.py
