"""Very simple API-key protection for the endpoints that CHANGE data.

If the API_KEY environment variable is empty (local development), everything is open.
If it is set (cloud deployment), POST /parking/entry and /parking/exit need the header
    X-API-Key: <the key>
Reading data (GET) stays open. This is basic protection for a demo, not full authentication."""
import hmac

from fastapi import Header, HTTPException

from backend import config


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = config.API_KEY  # read at call time so tests can change it
    if not expected:
        return
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key (send header X-API-Key)")
