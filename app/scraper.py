import requests
import json
from typing import Optional


BASE_URL = "https://en.aptoide.com/"

# Map full state names to abbreviations
STATE_TO_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"
}

def resolve_app_url(package_name: str) -> dict:
    """Resolve and return exact app data by package name.

    Uses Aptoide search API but enforces an exact match on the
    `package` field. This prevents partial inputs like `com.what`
    from returning unrelated apps.
    """

    api_url = (
        "https://ws75.aptoide.com/api/7/apps/search?"
        f"query={package_name}&limit=50"
    )

    r = requests.get(api_url, timeout=10)
    r.raise_for_status()
    data = r.json()

    try:
        apps = data.get("datalist", {}).get("list", [])
        # Find exact package match
        for app in apps:
            if app.get("package") == package_name:
                return app
        # No exact match found
        raise ValueError("App not found on Aptoide")
    except (KeyError, TypeError):
        raise ValueError("App not found on Aptoide")


def format_downloads(downloads: int) -> str:
    """Convert download count to readable format (e.g., 2B, 1.5M)"""
    if downloads >= 1_000_000_000:
        return f"{downloads / 1_000_000_000:.0f}B"
    elif downloads >= 1_000_000:
        return f"{downloads / 1_000_000:.1f}M"
    elif downloads >= 1_000:
        return f"{downloads / 1_000:.1f}K"
    return str(downloads)


def format_size(size_bytes: int) -> str:
    """Convert bytes to MB"""
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def parse_certificate_info(cert_owner: str) -> dict:
    """Parse certificate owner string to extract organization, location, country, etc."""
    result = {
        "developer_cn": "",
        "organization": "",
        "local": "",
        "country": "",
        "state_city": ""
    }
    
    # Parse certificate string like: "CN=Brian Acton, OU=Engineering, O=WhatsApp Inc., L=Santa Clara, ST=California, C=US"
    parts = [p.strip() for p in cert_owner.split(",")]
    
    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip()
            
            if key == "CN":
                result["developer_cn"] = value
            elif key == "O":
                result["organization"] = value
            elif key == "L":
                result["local"] = value
            elif key == "C":
                result["country"] = value
            elif key == "ST":
                # Convert full state name to abbreviation if available
                if value in STATE_TO_ABBR:
                    result["state_city"] = STATE_TO_ABBR[value]
                else:
                    # Keep as-is if already abbreviated or not in mapping
                    result["state_city"] = value
    
    return result


def format_app_data(app_info: dict) -> dict:
    """Format raw app data into the desired JSON response format"""
    file_info = app_info.get("file", {})
    signature_info = file_info.get("signature", {})
    cert_parts = parse_certificate_info(signature_info.get("owner", ""))
    
    downloads = app_info.get("stats", {}).get("downloads", 0)
    
    return {
        "name": app_info.get("name"),
        "size": format_size(app_info.get("size", 0)),
        "downloads": format_downloads(downloads),
        "version": file_info.get("vername"),
        "release_date": app_info.get("updated"),
        "min_screen": "SMALL",  # Default value, not available in API
        "supported_cpu": "arm64-v8a",  # Default value, not available in API
        "package_id": app_info.get("package"),
        "sha1_signature": signature_info.get("sha1"),
        "developer_cn": cert_parts["developer_cn"],
        "organization": cert_parts["organization"],
        "local": cert_parts["local"],
        "country": cert_parts["country"],
        "state_city": cert_parts["state_city"]
    }


def fetch_app_data(package_name: str) -> dict:
    """Fetch app data directly from the API and format it"""
    app_info = resolve_app_url(package_name)
    return format_app_data(app_info)


# Exception for scraper errors
class AptoideScraperException(Exception):
    """Custom exception for Aptoide scraper errors"""
    pass


# Scraper class for FastAPI integration
class AptoideScraper:
    """Scraper class to fetch app details from Aptoide"""
    
    def get_app_details(self, package_name: str) -> dict:
        """
        Fetch app details for a given package name
        
        Args:
            package_name: Android package identifier (e.g., com.facebook.katana)
            
        Returns:
            dict: Formatted app details
            
        Raises:
            AptoideScraperException: If app not found or scraping fails
        """
        try:
            return fetch_app_data(package_name)
        except ValueError as e:
            raise AptoideScraperException(str(e))
        except Exception as e:
            raise AptoideScraperException(f"Failed to fetch app data: {str(e)}")


# Create a singleton instance
scraper = AptoideScraper()



