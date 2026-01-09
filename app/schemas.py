from pydantic import BaseModel, Field
from typing import Optional


class AppDetails(BaseModel):
    """Schema for Aptoide app details response"""
    name: str = Field(..., description="App name")
    size: Optional[str] = Field(None, description="App size")
    downloads: Optional[str] = Field(None, description="Number of downloads")
    version: Optional[str] = Field(None, description="App version")
    release_date: Optional[str] = Field(None, description="Release date")
    min_screen: Optional[str] = Field(None, description="Minimum screen size")
    supported_cpu: Optional[str] = Field(None, description="Supported CPU architecture")
    package_id: str = Field(..., description="Package identifier")
    sha1_signature: Optional[str] = Field(None, description="SHA1 signature")
    developer_cn: Optional[str] = Field(None, description="Developer common name")
    organization: Optional[str] = Field(None, description="Organization name")
    local: Optional[str] = Field(None, description="Location/city")
    country: Optional[str] = Field(None, description="Country code")
    state_city: Optional[str] = Field(None, description="State/Province")

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
