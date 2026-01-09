"""
Test suite for Aptoide Scraper API

Run tests with: pytest test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_endpoint_returns_200(self):
        """Test that health endpoint returns status 200"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_endpoint_json_structure(self):
        """Test that health endpoint returns correct JSON structure"""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "message" in data
        assert "version" in data
        assert data["status"] == "ok"


class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root_returns_200(self):
        """Test that root endpoint returns status 200"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_returns_html(self):
        """Test that root endpoint returns HTML content"""
        response = client.get("/")
        assert response.headers["content-type"].startswith("text/html")
        assert b"Aptoide App Search" in response.content


class TestAptoideEndpoint:
    """Tests for main /aptoide endpoint"""
    
    def test_valid_package_returns_200_or_404(self):
        """Test that valid package format returns 200 (if found) or 404 (if not found)"""
        response = client.get("/aptoide?package_name=com.facebook.katana")
        assert response.status_code in [200, 404]
    
    def test_valid_package_json_structure(self):
        """Test that valid package returns correct JSON structure if found"""
        response = client.get("/aptoide?package_name=com.facebook.katana")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check all required fields exist
            required_fields = [
                "name", "size", "downloads", "version", "release_date",
                "min_screen", "supported_cpu", "package_id", "sha1_signature",
                "developer_cn", "organization", "local", "country", "state_city"
            ]
            
            for field in required_fields:
                assert field in data, f"Missing field: {field}"
            
            # Verify package_id matches request
            assert data["package_id"] == "com.facebook.katana"
    
    def test_invalid_package_format_returns_400(self):
        """Test that invalid package format returns 400"""
        invalid_packages = [
            "invalid",           # No dots
            "test",              # Single word
            "com.",              # Ends with dot
            ".com.test",         # Starts with dot
            "com..test",         # Double dots
        ]
        
        for package in invalid_packages:
            response = client.get(f"/aptoide?package_name={package}")
            assert response.status_code == 400, f"Failed for package: {package}"
    
    def test_missing_package_name_returns_422(self):
        """Test that missing package_name parameter returns 422 (validation error)"""
        response = client.get("/aptoide")
        assert response.status_code == 422
    
    def test_empty_package_name_returns_422(self):
        """Test that empty package_name returns 422 (validation error)"""
        response = client.get("/aptoide?package_name=")
        assert response.status_code == 422
    
    def test_nonexistent_package_returns_404(self):
        """Test that non-existent package returns 404"""
        response = client.get("/aptoide?package_name=com.nonexistent.fake.app.xyz123")
        assert response.status_code == 404
    
    def test_valid_two_segment_package(self):
        """Test that two-segment package names are accepted"""
        response = client.get("/aptoide?package_name=com.whatsapp")
        assert response.status_code in [200, 404]  # Should not return 400


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_404_error_contains_detail(self):
        """Test that 404 errors contain helpful detail message"""
        response = client.get("/aptoide?package_name=com.fake.nonexistent.app")
        if response.status_code == 404:
            data = response.json()
            assert "detail" in data
            assert "not found" in data["detail"].lower()
    
    def test_400_error_contains_detail(self):
        """Test that 400 errors contain helpful detail message"""
        response = client.get("/aptoide?package_name=invalid")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "format" in data["detail"].lower()


class TestAPIDocumentation:
    """Tests for API documentation endpoints"""
    
    def test_docs_endpoint_accessible(self):
        """Test that /docs endpoint is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_endpoint_accessible(self):
        """Test that /redoc endpoint is accessible"""
        response = client.get("/redoc")
        assert response.status_code == 200


class TestResponseHeaders:
    """Tests for response headers"""
    
    def test_json_content_type(self):
        """Test that JSON endpoints return correct content type"""
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]
    
    def test_aptoide_response_is_json(self):
        """Test that /aptoide endpoint returns JSON content type"""
        response = client.get("/aptoide?package_name=com.facebook.katana")
        if response.status_code == 200:
            assert "application/json" in response.headers["content-type"]


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
