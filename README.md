# Aptoide Scraper API

A Python-based REST API that fetches package data from the Aptoide app store and exposes it through a clean, documented endpoint.

## Features

- **FastAPI Framework**: Modern, fast, and with automatic API documentation
- **Direct Aptoide API Fetch**: Uses Aptoide's public API to reliably retrieve app metadata
- **Comprehensive Error Handling**: Graceful handling of missing apps, network errors, and invalid inputs
- **Input Validation**: Package name format validation
- **Structured Response**: Well-defined JSON schema with all app metadata
- **API Documentation**: Auto-generated Swagger UI and ReDoc documentation
- **Logging**: Request and error logging for debugging
- **Simple Web UI**: Root (`/`) serves a minimal search page to try the endpoint

> **Note**: Although not required by the challenge, a minimal web interface was added purely as a convenience layer to demonstrate how the API can be consumed by a client. The core functionality is entirely API-based.

## API Endpoint

### GET `/aptoide`

Fetch detailed information about an Android app from Aptoide.

**Query Parameters:**
- `package_name` (required): Android package identifier (e.g., `com.facebook.katana`)

**Example Request:**
```bash
GET /aptoide?package_name=com.facebook.katana
```

**Example Response:**
```json
{
  "name": "Facebook",
  "size": "152.5 MB",
  "downloads": "2B",
  "version": "532.0.0.55.71",
  "release_date": "2025-09-30 17:06:59",
  "min_screen": "SMALL",
  "supported_cpu": "arm64-v8a",
  "package_id": "com.facebook.katana",
  "sha1_signature": "8A:3C:4B:26:2D:72:1A:CD:49:A4:BF:97:D5:21:31:99:C8:6F:A2:B9",
  "developer_cn": "Facebook Corporation",
  "organization": "Facebook Mobile",
  "local": "Palo Alto",
  "country": "US",
  "state_city": "CA"
}
```

**Status Codes:**
- `200 OK`: Successfully retrieved app details
- `400 Bad Request`: Invalid or missing package_name
- `404 Not Found`: App not found on Aptoide
- `500 Internal Server Error`: Server error while fetching data

Note: The `size` field reflects the APK download size reported by Aptoide, which may differ from installed size.

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd aptoide-scraper-api
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the API

Start the server with:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API Base URL**: `http://localhost:8000`
- **Interactive Docs (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative Docs (ReDoc)**: `http://localhost:8000/redoc`
- **Web UI (Search Page)**: `http://localhost:8000/` - A simple interface to test the API in your browser
- **Health Check**: `http://localhost:8000/health`

### Running on a Different Port

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## Usage Examples

### Using curl

```bash
# Basic request
curl "http://localhost:8000/aptoide?package_name=com.facebook.katana"

# With pretty printing (using jq)
curl "http://localhost:8000/aptoide?package_name=com.facebook.katana" | jq
```

### Using Python requests

```python
import requests

response = requests.get(
    "http://localhost:8000/aptoide",
    params={"package_name": "com.facebook.katana"}
)

if response.status_code == 200:
    app_data = response.json()
    print(f"App Name: {app_data['name']}")
    print(f"Version: {app_data['version']}")
else:
    print(f"Error: {response.json()}")
```

### Using JavaScript/Fetch

```javascript
fetch('http://localhost:8000/aptoide?package_name=com.facebook.katana')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

## Project Structure

```
aptoide-scraper-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application, endpoints, and web UI
│   ├── schemas.py       # Pydantic models for response
│   └── scraper.py       # Aptoide API fetch + formatting
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Design Decisions & Assumptions

### Architecture

1. **FastAPI Choice**: Selected for its modern async capabilities, automatic OpenAPI documentation, and excellent performance
2. **Modular Structure**: Separated concerns into:
   - `main.py`: API routes and request handling
   - `schemas.py`: Data models and validation
   - `scraper.py`: Web scraping logic

### Data Fetch Strategy

1. **Aptoide Public API**: Queries the Aptoide API (e.g., `https://ws75.aptoide.com/api/7/apps/search`) to retrieve app metadata
2. **Graceful Degradation**: Returns `null` for fields that aren't available rather than failing entirely
3. **User-Agent Header**: Set when needed to avoid blocking by upstream services

### Error Handling

1. **Custom Exception**: `AptoideScraperException` for scraping-specific errors
2. **HTTP Status Codes**: Proper status codes for different error scenarios
3. **Detailed Logging**: Comprehensive logging for debugging and monitoring
4. **Validation**: Package name format validation to catch obvious errors early

### Scalability Considerations

1. **Session Reuse**: Maintains a session for connection pooling
2. **Timeout**: 10-second timeout on requests to prevent hanging
3. **Stateless Design**: Each request is independent, allowing horizontal scaling
4. **CORS Enabled**: Ready for frontend integration

### Assumptions

1. **Aptoide Structure**: Assumes Aptoide's HTML structure remains relatively stable
   - If structure changes, extraction patterns may need updates
2. **Rate Limiting**: No rate limiting implemented (should be added for production)
3. **Caching**: No caching layer (could improve performance for repeated queries)
4. **Data Availability**: Not all fields may be available for every app
   - Returns `null` for unavailable fields rather than error

## Testing

### Manual Testing

1. Visit `http://localhost:8000/` and use the search bar to query by package name (e.g., `com.facebook.katana`)
2. Call the endpoint directly:
   - `http://localhost:8000/aptoide?package_name=com.facebook.katana`
3. Try different package names:
   - Valid: `com.facebook.katana`, `com.whatsapp`, `com.instagram.android`
   - Invalid format: `invalid`, `test`
   - Non-existent: `com.nonexistent.app123456`

## Known Limitations

1. **Scraping Fragility**: Web scraping is inherently fragile and may break if Aptoide changes their HTML structure
2. **No Rate Limiting**: Production use should implement rate limiting
3. **No Caching**: Repeated requests fetch fresh data every time
4. **Limited Data Validation**: Some fields may be incomplete or unavailable depending on Aptoide's data
5. **Single Source**: Only scrapes from Aptoide, not other app stores

## Future Improvements

- [ ] Add Redis caching for repeated queries
- [ ] Implement rate limiting with slowapi
- [ ] Add comprehensive test suite
- [ ] Support for batch queries (multiple packages)
- [ ] Async scraping for better performance
- [ ] Database storage for historical data
- [ ] API authentication for production
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Monitoring and metrics (Prometheus/Grafana)

## Requirements

- Python 3.9+
- FastAPI
- Uvicorn
- Requests
- Pydantic

See `requirements.txt` for the full dependency list.

## License

This project is for educational and evaluation purposes.

## Author

Created as part of the Aptoide Python Developer Challenge.

## Contributing

This is a challenge submission, but feedback and suggestions are welcome!

---

**Note**: This is a web scraping tool. Be respectful of Aptoide's terms of service and implement appropriate rate limiting for production use.
