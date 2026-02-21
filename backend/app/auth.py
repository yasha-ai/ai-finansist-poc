"""Telegram Mini App initData verification."""
import hashlib
import hmac
import json
from urllib.parse import unquote, parse_qs

from fastapi import HTTPException, Header

from app.config import settings


def verify_init_data(init_data: str) -> dict:
    """Verify Telegram Mini App initData and return parsed user data."""
    if settings.DEBUG and init_data == "debug":
        return {
            "id": 123456789,
            "username": "debug_user",
            "first_name": "Debug",
            "last_name": "User",
        }

    try:
        parsed = parse_qs(unquote(init_data))
        
        # Extract hash
        received_hash = parsed.get("hash", [None])[0]
        if not received_hash:
            raise ValueError("No hash in initData")

        # Build data-check-string
        data_pairs = []
        for key, values in sorted(parsed.items()):
            if key != "hash":
                data_pairs.append(f"{key}={values[0]}")
        data_check_string = "\n".join(data_pairs)

        # Compute HMAC
        secret_key = hmac.new(
            b"WebAppData",
            settings.BOT_TOKEN.encode(),
            hashlib.sha256,
        ).digest()
        
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        if computed_hash != received_hash:
            raise ValueError("Invalid hash")

        # Parse user
        user_data = json.loads(parsed.get("user", ['{}'])[0])
        return user_data

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid initData: {str(e)}")


async def get_current_user(x_init_data: str = Header(alias="X-Init-Data", default="")):
    """FastAPI dependency for auth via Telegram initData."""
    if not x_init_data:
        raise HTTPException(status_code=401, detail="X-Init-Data header required")
    return verify_init_data(x_init_data)
