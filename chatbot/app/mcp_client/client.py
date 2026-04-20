"""Async MCP Server HTTP client with automatic JWT token refresh."""
import httpx

from app.config import get_settings

settings = get_settings()

_token: str | None = None


def _ssl_verify():
    """Return the SSL verification setting for httpx.
    Accepts a CA bundle path, 'true' (default verify), or 'false' (disable — dev only)."""
    v = settings.mcp_ssl_verify.lower()
    if v == "false":
        return False
    if v == "true":
        return True
    return v  # treat as a path to a CA bundle


async def _get_token() -> str:
    global _token
    if _token:
        return _token
    async with httpx.AsyncClient(verify=_ssl_verify()) as client:
        resp = await client.post(
            f"{settings.mcp_base_url}/api/v1/auth/token",
            data={"username": settings.mcp_username, "password": settings.mcp_password},
        )
        resp.raise_for_status()
        _token = resp.json()["access_token"]
    return _token


async def _request(method: str, path: str, **kwargs):
    global _token
    token = await _get_token()
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient(verify=_ssl_verify()) as client:
        resp = await client.request(
            method,
            f"{settings.mcp_base_url}{path}",
            headers=headers,
            **kwargs,
        )
        if resp.status_code == 401:
            # Token expired — reset and retry once
            _token = None
            token = await _get_token()
            headers["Authorization"] = f"Bearer {token}"
            resp = await client.request(
                method,
                f"{settings.mcp_base_url}{path}",
                headers=headers,
                **kwargs,
            )
        resp.raise_for_status()
        return resp.json()


async def get_ingredients(skip: int = 0, limit: int = 20) -> list[dict]:
    return await _request("GET", "/api/v1/ingredients/", params={"skip": skip, "limit": limit})


async def get_ingredient(ingredient_id: str) -> dict:
    return await _request("GET", f"/api/v1/ingredients/{ingredient_id}")


async def pairing_score(ingredient_a: str, ingredient_b: str) -> dict:
    return await _request(
        "GET",
        "/api/v1/pairings/score",
        params={"ingredient_a": ingredient_a, "ingredient_b": ingredient_b},
    )


async def genetic_filter(ingredient: str) -> dict:
    return await _request(
        "GET",
        "/api/v1/pairings/genetic-filter",
        params={"ingredient": ingredient},
    )


async def get_molecules(skip: int = 0, limit: int = 20) -> list[dict]:
    return await _request("GET", "/api/v1/molecules/", params={"skip": skip, "limit": limit})
