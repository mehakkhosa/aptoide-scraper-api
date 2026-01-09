from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import json

from .schemas import AppDetails, ErrorResponse
from .scraper import scraper, AptoideScraperException

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_search_page() -> str:
    """Generate HTML search page"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aptoide App Search</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }
        
        #packageName {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        #packageName:focus {
            outline: none;
            border-color: #667eea;
        }
        
        #packageName::placeholder {
            color: #999;
        }
        
        button {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loading {
            text-align: center;
            color: #667eea;
            margin: 20px 0;
            display: none;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            display: inline-block;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #fee;
            border: 1px solid #fcc;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            display: none;
        }
        
        .error.active {
            display: block;
        }
        
        .app-details {
            background: #f9f9f9;
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            display: none;
        }
        
        .app-details.active {
            display: block;
        }
        
        .app-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }
        
        .app-title {
            flex: 1;
        }
        
        .app-name {
            font-size: 24px;
            font-weight: 700;
            color: #333;
            margin-bottom: 5px;
        }
        
        .app-package {
            font-size: 12px;
            color: #999;
            font-family: monospace;
        }
        
        .app-rating {
            font-size: 32px;
            color: #ffc107;
            text-align: right;
        }
        
        .app-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .info-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #eee;
        }
        
        .info-label {
            font-size: 12px;
            color: #999;
            text-transform: uppercase;
            margin-bottom: 5px;
            font-weight: 600;
        }
        
        .info-value {
            font-size: 16px;
            color: #333;
            font-weight: 500;
        }
        
        .certificate-info {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin-top: 15px;
        }
        
        .certificate-info h3 {
            font-size: 14px;
            color: #333;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .cert-field {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
            font-size: 13px;
        }
        
        .cert-field:last-child {
            border-bottom: none;
        }
        
        .cert-label {
            color: #666;
            font-weight: 500;
        }
        
        .cert-value {
            color: #333;
            font-family: monospace;
            text-align: right;
            word-break: break-word;
        }
        
        .no-results {
            text-align: center;
            color: #666;
            padding: 20px;
            display: none;
        }
        
        .no-results.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Aptoide App Search</h1>
        <p class="subtitle">Search for any app available on Aptoide</p>
        
        <div class="search-box">
            <input 
                type="text" 
                id="packageName" 
                placeholder="com.facebook.katana"
                autocomplete="off"
                title="Enter package name only (e.g., com.facebook.katana)"
            >
            <button onclick="searchApp()">Search</button>
        </div>
        
        <p style="color: #999; font-size: 12px; text-align: center; margin-bottom: 20px;">
            💡 Tip: Enter only the package name (e.g., <code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px;">com.facebook.katana</code>)
        </p>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Searching for app...</p>
        </div>
        
        <div class="error" id="error"></div>
        <div class="no-results" id="noResults">No app found with that package name</div>
        
        <div class="app-details" id="appDetails"></div>
    </div>

    <script>
        // Allow Enter key to search
        document.getElementById('packageName').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') searchApp();
        });
        
        function searchApp() {
            const packageName = document.getElementById('packageName').value.trim();
            
            if (!packageName) {
                showError('Please enter a package name');
                return;
            }
            
            // Show loading, hide others
            document.getElementById('loading').classList.add('active');
            document.getElementById('error').classList.remove('active');
            document.getElementById('appDetails').classList.remove('active');
            document.getElementById('noResults').classList.remove('active');
            
            // Make API request
            fetch(`/aptoide?package_name=${encodeURIComponent(packageName)}`)
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw new Error(data.detail || 'App not found');
                        });
                    }
                    return response.json();
                })
                .then(data => displayApp(data))
                .catch(error => {
                    document.getElementById('loading').classList.remove('active');
                    showError(error.message);
                });
        }
        
        function displayApp(data) {
            document.getElementById('loading').classList.remove('active');
            
            let html = `
                <div class="app-header">
                    <div class="app-title">
                        <div class="app-name">${escapeHtml(data.name)}</div>
                        <div class="app-package">${escapeHtml(data.package_id)}</div>
                    </div>
                </div>
                
                <div class="app-grid">
                    <div class="info-card">
                        <div class="info-label">Size</div>
                        <div class="info-value">${escapeHtml(data.size)}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Downloads</div>
                        <div class="info-value">${escapeHtml(data.downloads)}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Version</div>
                        <div class="info-value">${escapeHtml(data.version)}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Released</div>
                        <div class="info-value">${escapeHtml(data.release_date)}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Min Screen</div>
                        <div class="info-value">${escapeHtml(data.min_screen)}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">CPU Support</div>
                        <div class="info-value">${escapeHtml(data.supported_cpu)}</div>
                    </div>
                </div>
            `;
            
            // Add certificate info if available
            if (data.developer_cn) {
                html += `
                    <div class="certificate-info">
                        <h3>Developer Information</h3>
                        ${data.developer_cn ? `<div class="cert-field"><span class="cert-label">Common Name</span><span class="cert-value">${escapeHtml(data.developer_cn)}</span></div>` : ''}
                        ${data.organization ? `<div class="cert-field"><span class="cert-label">Organization</span><span class="cert-value">${escapeHtml(data.organization)}</span></div>` : ''}
                        ${data.local ? `<div class="cert-field"><span class="cert-label">Locality</span><span class="cert-value">${escapeHtml(data.local)}</span></div>` : ''}
                        ${data.country ? `<div class="cert-field"><span class="cert-label">Country</span><span class="cert-value">${escapeHtml(data.country)}</span></div>` : ''}
                        ${data.state_city ? `<div class="cert-field"><span class="cert-label">State/City</span><span class="cert-value">${escapeHtml(data.state_city)}</span></div>` : ''}
                        ${data.sha1_signature ? `<div class="cert-field"><span class="cert-label">SHA1</span><span class="cert-value">${escapeHtml(data.sha1_signature)}</span></div>` : ''}
                    </div>
                `;
            }
            
            document.getElementById('appDetails').innerHTML = html;
            document.getElementById('appDetails').classList.add('active');
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = '❌ ' + message;
            errorDiv.classList.add('active');
        }
        
        function escapeHtml(text) {
            if (!text) return '';
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }
        
        // Focus on input when page loads
        window.addEventListener('load', function() {
            document.getElementById('packageName').focus();
        });
    </script>
</body>
</html>
    """

# Initialize FastAPI app
app = FastAPI(
    title="Aptoide Scraper API",
    description="API for scraping package data from Aptoide app store",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    """Root endpoint - Returns HTML search interface"""
    return HTMLResponse(content=get_search_page())


@app.get("/health", tags=["Health"])
def health():
    """JSON health check endpoint"""
    return {
        "status": "ok",
        "message": "Aptoide Scraper API is running",
        "version": "1.0.0"
    }


@app.get(
    "/aptoide",
    response_model=AppDetails,
    responses={
        200: {
            "description": "Successfully retrieved app details",
            "model": AppDetails
        },
        400: {
            "description": "Bad request - invalid or missing package_name",
            "model": ErrorResponse
        },
        404: {
            "description": "App not found",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    },
    tags=["Aptoide"]
)
async def get_aptoide_package(
    package_name: str = Query(
        ...,
        description="Package identifier (e.g., com.facebook.katana)",
        examples=["com.facebook.katana"],
        min_length=1
    )
):
    """
    Scrape and return app details from Aptoide app store
    
    This endpoint fetches detailed information about an Android application
    from the Aptoide app store, including metadata like version, size,
    downloads, and developer information.
    
    **Example Request:**
    ```
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
    """
    try:
        # Validate package_name format
        if not package_name or not package_name.strip():
            raise HTTPException(
                status_code=400,
                detail="Package name cannot be empty"
            )
        
        # Basic validation for package name format
        if not _is_valid_package_name(package_name):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid package name format: '{package_name}'. Expected format: com.example.app"
            )
        
        logger.info(f"Received request for package: {package_name}")
        
        # Fetch app details
        app_data = scraper.get_app_details(package_name)
        
        logger.info(f"Successfully retrieved data for: {package_name}")
        
        # Return compact JSON - let browser's Pretty-print button format it
        return app_data
        
    except AptoideScraperException as e:
        logger.error(f"Scraper error for {package_name}: {str(e)}")
        # Check if it's a not found error
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=404,
                detail=f"App with package name '{package_name}' not found on Aptoide"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to scrape app data: {str(e)}"
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error for {package_name}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


def _is_valid_package_name(package_name: str) -> bool:
    """
    Validate Android package name format
    
    Basic validation - package names typically follow format: com.company.app
    """
    import re
    # Require at least two segments (e.g., com.whatsapp or com.example.app)
    # Pattern: labels start with a letter, then letters/digits/underscores; segments separated by dots
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*){1,}$'
    return bool(re.match(pattern, package_name))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred"
        }
    )
