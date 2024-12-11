import httpx

from .location_api import Location, LocationAPI

BASE_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "TieTimeBot/1.0"


def build_headers() -> dict:
    return {"User-Agent": USER_AGENT}


class NominatimAPI(LocationAPI):
    # https://nominatim.org/release-docs/latest/

    async def search(self, search_term: str) -> Location:
        params = {"q": search_term, "format": "json", "limit": 1}

        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL, params=params, headers=build_headers())

        if response.status_code != 200:
            return None

        data = response.json()

        if len(data) == 0:
            return None

        location = data[0]
        return {
            "lat": location["lat"],
            "lon": location["lon"],
        }

    async def get_place_name(self, location: Location) -> str:
        params = {
            "q": f"{location['lat']},{location['lon']}",
            "format": "json",
            "limit": 1,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL, params=params, headers=build_headers())

        if response.status_code != 200:
            return None

        data = response.json()

        if len(data) == 0:
            return None

        place = data[0]
        return place["display_name"]
