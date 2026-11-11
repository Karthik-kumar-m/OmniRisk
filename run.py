"""OmniRisk Application Launcher.

Starts the FastAPI server and serves both the REST API and the Frontend UI.
Usage: python run.py
"""

import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print("  OMNIRISK: Automated Risk Profile Summarizer")
    print("  TCS Technology Day Challenge - Underwriting AI Assistant")
    print("=" * 65)
    print("  Web Cockpit UI:  http://127.0.0.1:8000")
    print("  API Docs (Docs): http://127.0.0.1:8000/docs")
    print("  Health Endpoint: http://127.0.0.1:8000/api/health")
    print("=" * 65)
    print("Starting server on http://127.0.0.1:8000 ... Press Ctrl+C to stop.\n")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
