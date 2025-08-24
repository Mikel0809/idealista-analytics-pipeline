"""
Data models for the Idealista API responses.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PropertyLocation(BaseModel):
    """Location data for a property."""
    latitude: float
    longitude: float
    address: str
    district: str
    neighborhood: str
    city: str
    province: str
    country: str = "España"
    postal_code: Optional[str] = None


class PropertyFeatures(BaseModel):
    """Physical features of a property."""
    size: float = Field(..., description="Size in square meters")
    rooms: int = Field(..., description="Number of rooms")
    bathrooms: int = Field(..., description="Number of bathrooms")
    has_elevator: Optional[bool] = None
    has_parking: Optional[bool] = None
    has_terrace: Optional[bool] = None
    has_garden: Optional[bool] = None
    has_pool: Optional[bool] = None
    floor: Optional[int] = None
    is_exterior: Optional[bool] = None
    energy_certificate: Optional[str] = None
    condition: Optional[str] = None
    construction_year: Optional[int] = None


class PropertyPrice(BaseModel):
    """Price information for a property."""
    price: float = Field(..., description="Price in euros")
    price_per_sqm: float = Field(..., description="Price per square meter")
    currency: str = "EUR"
    original_price: Optional[float] = None
    price_change_date: Optional[datetime] = None
    price_change_percentage: Optional[float] = None


class PropertyListing(BaseModel):
    """Main model for property listings from Idealista."""
    id: str = Field(..., description="Unique identifier for the property")
    reference: Optional[str] = None
    type: str = Field(..., description="Type of property (apartment, house, etc.)")
    operation: str = Field(..., description="Type of operation (sale, rent)")
    status: str = Field(..., description="Status of the listing (active, sold, etc.)")
    url: str
    title: str
    description: Optional[str] = None
    location: PropertyLocation
    features: PropertyFeatures
    price: PropertyPrice
    images: List[str] = []
    published_date: datetime
    updated_date: datetime
    contact_phone: Optional[str] = None
    contact_name: Optional[str] = None
    agency_id: Optional[str] = None
    agency_name: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SearchResponse(BaseModel):
    """Response model for search API."""
    total_results: int
    page: int
    total_pages: int
    items_per_page: int
    results: List[PropertyListing]
    search_date: datetime = Field(default_factory=datetime.now)
