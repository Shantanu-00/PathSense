from typing import List, Tuple, Optional
from app.schemas.places import Place
import requests
from app.config.logging import logger

class OSMClient:
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
    NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"

    amenity_map = {
        # Healthcare
        "hospital": ["hospital"],
        "clinic": ["clinic", "doctors"],
        "pharmacy": ["pharmacy"],
        "medical": ["pharmacy", "clinic", "doctors", "hospital"],

        # Food & Drinks
        "restaurant": ["restaurant"],
        "cafe": ["cafe"],
        "fast_food": ["fast_food"],
        "bar": ["bar"],
        "pub": ["pub"],
        "bakery": ["bakery"],
        "supermarket": ["supermarket"],

        # Finance
        "atm": ["atm"],
        "bank": ["bank"],

        # Shopping
        "shop": ["shop"],
        "mall": ["mall"],
        "hardware": ["hardware"],
        "grocery": ["supermarket", "convenience"],
        "market": ["marketplace"],

        # Transport
        "bus_stop": ["bus_station", "bus_stop"],
        "train": ["train_station", "subway_station"],
        "airport": ["aerodrome"],

        # Education
        "school": ["school"],
        "college": ["college"],
        "university": ["university"],
        "library": ["library"],

        # Leisure
        "park": ["park"],
        "gym": ["gym", "fitness_centre"],
        "cinema": ["cinema"],
        "theatre": ["theatre"],
        "stadium": ["stadium"],

        # Emergency / Govt
        "police": ["police"],
        "fire_station": ["fire_station"],
        "post_office": ["post_office"],

        # Hotels & Stay
        "hotel": ["hotel"],
        "hostel": ["hostel"],
        "motel": ["motel"],
        "guesthouse": ["guest_house"],
    }

    @staticmethod
    async def search_places(business_type: str, location: str, limit: int = 5) -> List[Place]:
        # Normalize business types
        types = [t.strip() for t in business_type.lower().split(",")]
        amenities = []
        for t in types:
            amenities.extend(OSMClient.amenity_map.get(t, [t]))
        amenity_str = "|".join(amenities)

        # Get lat/lon of location
        coords = OSMClient.geocode(location)
        if not coords:
            logger.warning(f"Geocoding failed for location: {location}")
            return []
        lat, lon = coords

        # Bounding box (~5km radius)
        delta = 0.05
        bbox = (lat - delta, lon - delta, lat + delta, lon + delta)

        query = f"""
        [out:json];
        (
          node["amenity"~"{amenity_str}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          way["amenity"~"{amenity_str}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          node["shop"~"{amenity_str}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          way["shop"~"{amenity_str}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        );
        out center {limit};
        """

        logger.info(f"Searching OSM for '{business_type}' in '{location}' with limit {limit}. Amenity filter: {amenity_str}")
        logger.debug(f"Raw Overpass query:\n{query}")

        try:
            response = requests.post(OSMClient.OVERPASS_URL, data={"data": query}, timeout=15)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Raw OSM response: {data}")
            return OSMClient._parse_osm_response(data, business_type)
        except Exception as e:
            logger.error(f"OSM API error: {str(e)}")
            return []

    @staticmethod
    def _parse_osm_response(data: dict, business_type: str) -> List[Place]:
        places = []

        for element in data.get("elements", []):
            if "tags" not in element:
                continue

            tags = element["tags"]
            name = tags.get("name", "Unknown")

            if "lat" in element and "lon" in element:
                lat, lon = element["lat"], element["lon"]
            elif "center" in element:
                lat, lon = element["center"]["lat"], element["center"]["lon"]
            else:
                continue

            address = (
                tags.get("addr:full")
                or tags.get("addr:street")
                or tags.get("addr:housenumber")
                or None
            )

            if not address:
                address = OSMClient._reverse_geocode(lat, lon)

            places.append(
                Place(
                    name=name,
                    latitude=lat,
                    longitude=lon,
                    address=address,
                    type=business_type,
                )
            )

        logger.info(f"Total parsed places for {business_type}: {len(places)}")
        return places

    @staticmethod
    def _reverse_geocode(lat: float, lon: float) -> str:
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "format": "json",
                "addressdetails": 1,
            }
            headers = {"User-Agent": "RouteGenie/1.0"}
            response = requests.get(OSMClient.NOMINATIM_URL, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("display_name", None)
        except Exception as e:
            logger.warning(f"Reverse geocode failed: {str(e)}")
            return None

    @staticmethod
    def geocode(address: str) -> Optional[Tuple[float, float]]:
        try:
            params = {
                "q": address,
                "format": "json",
                "limit": 1
            }
            headers = {"User-Agent": "RouteGenie/1.0"}
            response = requests.get(OSMClient.NOMINATIM_SEARCH_URL, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
            return None
        except Exception as e:
            logger.error(f"Geocode failed: {str(e)}")
            return None
