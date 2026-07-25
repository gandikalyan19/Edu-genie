"""Root entrypoint so the app can run with `uvicorn main:app --reload`."""

from backend.app.main import app

__all__ = ["app"]
