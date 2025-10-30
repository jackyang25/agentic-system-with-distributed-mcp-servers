import os
import httpx
from typing import Any
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

server: FastMCP = FastMCP(name="Location")


def _get_zip_coordinates(zip_code: str) -> tuple[float, float]:
    """Convert ZIP code to lat/lon coordinates"""
    try:
        url = f"https://api.zippopotam.us/us/{zip_code}"

        with httpx.Client() as client:
            response: httpx.Response = client.get(url=url, timeout=10.0)
            response.raise_for_status()
            data: Any = response.json()

        if data and "places" in data and len(data["places"]) > 0:
            place: Any = data["places"][0]
            lat = float(place["latitude"])
            lon = float(place["longitude"])
            return (lat, lon)
        else:
            raise ValueError(f"ZIP code {zip_code} not found")

    except Exception:
        return (40.7505, -73.9934)


@server.tool()
def get_transit_score(zip_code: str) -> dict[str, Any]:
    """
    Get transit score and summary for a specific ZIP code

    Args:
        zip_code: ZIP code for the location

    Returns:
        dictionary containing transit score, description, and route summary
    """
    try:
        lat, lon = _get_zip_coordinates(zip_code=zip_code)

        api_key = os.getenv("WALKSCORE_API_KEY")
        if not api_key:
            return {
                "error": "Walk Score API key not configured",
                "status": "error",
                "zip_code": zip_code,
            }

        params: dict[str, Any] = {"lat": lat, "lon": lon, "wsapikey": api_key}

        with httpx.Client() as client:
            response: httpx.Response = client.get(
                url="https://transit.walkscore.com/transit/score/",
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            data: Any = response.json()

        if data and "transit_score" in data:
            return {
                "transit_score": data.get("transit_score"),
                "description": data.get("description"),
                "summary": data.get("summary"),
                "zip_code": zip_code,
                "lat": lat,
                "lon": lon,
                "status": "success",
            }
        else:
            return {
                "error": "No transit score found for this location",
                "status": "error",
                "zip_code": zip_code,
            }

    except httpx.RequestError as e:
        return {
            "error": f"Transit API request failed: {str(e)}",
            "status": "error",
            "zip_code": zip_code,
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "status": "error",
            "zip_code": zip_code,
        }


if __name__ == "__main__":
    server.run(transport="stdio")
