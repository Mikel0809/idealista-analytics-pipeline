"""
API client for Idealista data extraction.
"""
import base64
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Union

import requests
from dotenv import load_dotenv
from pydantic import ValidationError

from scripts.api_client.models import PropertyListing, SearchResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class IdealistaAPIClient:
    """Client for interacting with the Idealista API."""

    BASE_URL = "https://api.idealista.com/3.5"
    TOKEN_URL = "https://api.idealista.com/oauth/token"
    
    def __init__(self, api_key: Optional[str] = None, secret: Optional[str] = None):
        """
        Initialize the Idealista API client.
        
        Args:
            api_key: Idealista API key (defaults to IDEALISTA_API_KEY env var)
            secret: Idealista secret (defaults to IDEALISTA_SECRET env var)
        """
        self.api_key = api_key or os.getenv("IDEALISTA_API_KEY")
        self.secret = secret or os.getenv("IDEALISTA_SECRET")
        
        if not self.api_key or not self.secret:
            raise ValueError("API key and secret must be provided or set as environment variables")
        
        self.access_token = None
        self.token_expiry = None
        
    def _get_auth_header(self) -> Dict[str, str]:
        """
        Get the authentication header for API requests.
        
        Returns:
            Dict containing the Authorization header
        """
        # Check if token is expired or not set
        if not self.access_token or (self.token_expiry and datetime.now() >= self.token_expiry):
            self._refresh_token()
            
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def _refresh_token(self) -> None:
        """
        Refresh the OAuth access token.
        """
        auth_string = f"{self.api_key}:{self.secret}"
        auth_bytes = auth_string.encode("ascii")
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode("ascii")
        
        headers = {
            "Authorization": f"Basic {base64_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"grant_type": "client_credentials", "scope": "read"}
        
        try:
            response = requests.post(self.TOKEN_URL, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            # Set expiry to slightly before actual expiry to avoid edge cases
            expires_in = token_data["expires_in"] - 60  # Subtract 60 seconds as buffer
            self.token_expiry = datetime.now().timestamp() + expires_in
            
            logger.info("Successfully refreshed access token")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error refreshing token: {e}")
            raise
    
    def search_properties(
        self,
        operation: str,
        property_type: str,
        location: str,
        max_items: int = 50,
        max_pages: Optional[int] = None,
        **kwargs
    ) -> List[PropertyListing]:
        """
        Search for properties with the given criteria.
        
        Args:
            operation: Type of operation (sale, rent)
            property_type: Type of property (homes, offices, etc.)
            location: Location to search in (city, district, etc.)
            max_items: Maximum number of items per page
            max_pages: Maximum number of pages to retrieve (None for all)
            **kwargs: Additional search parameters
            
        Returns:
            List of PropertyListing objects
        """
        endpoint = f"{self.BASE_URL}/es/search"
        
        params = {
            "operation": operation,
            "propertyType": property_type,
            "location": location,
            "maxItems": max_items,
            "numPage": 1,
            **kwargs
        }
        
        all_results = []
        current_page = 1
        total_pages = 1  # Will be updated after first request
        
        while current_page <= total_pages and (max_pages is None or current_page <= max_pages):
            params["numPage"] = current_page
            
            try:
                headers = self._get_auth_header()
                response = requests.post(endpoint, headers=headers, json=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse response
                search_response = SearchResponse(
                    total_results=data.get("totalResults", 0),
                    page=current_page,
                    total_pages=data.get("totalPages", 1),
                    items_per_page=data.get("itemsPerPage", 0),
                    results=[self._parse_property(item) for item in data.get("elementList", [])],
                    search_date=datetime.now()
                )
                
                all_results.extend(search_response.results)
                total_pages = search_response.total_pages
                
                logger.info(f"Retrieved page {current_page}/{total_pages} with {len(search_response.results)} results")
                
                # Respect API rate limits
                if current_page < total_pages:
                    time.sleep(1)  # Sleep for 1 second between requests
                
                current_page += 1
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error searching properties: {e}")
                if hasattr(e.response, 'text'):
                    logger.error(f"Response: {e.response.text}")
                raise
            except ValidationError as e:
                logger.error(f"Error parsing response: {e}")
                raise
        
        return all_results
    
    def get_property_detail(self, property_id: str) -> PropertyListing:
        """
        Get detailed information for a specific property.
        
        Args:
            property_id: The ID of the property
            
        Returns:
            PropertyListing object with detailed information
        """
        endpoint = f"{self.BASE_URL}/es/detail"
        
        params = {
            "propertyId": property_id
        }
        
        try:
            headers = self._get_auth_header()
            response = requests.post(endpoint, headers=headers, json=params)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_property(data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting property detail: {e}")
            raise
        except ValidationError as e:
            logger.error(f"Error parsing property detail: {e}")
            raise
    
    def _parse_property(self, data: Dict) -> PropertyListing:
        """
        Parse property data from API response into a PropertyListing object.
        
        Args:
            data: Raw property data from API
            
        Returns:
            PropertyListing object
        """
        # This is a simplified implementation - in a real scenario,
        # you would need to map the actual API response fields to your model
        try:
            # Transform API response to match our model structure
            transformed_data = {
                "id": data.get("propertyCode", ""),
                "reference": data.get("reference", ""),
                "type": data.get("propertyType", ""),
                "operation": data.get("operation", ""),
                "status": data.get("status", "active"),
                "url": data.get("url", ""),
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "location": {
                    "latitude": data.get("latitude", 0.0),
                    "longitude": data.get("longitude", 0.0),
                    "address": data.get("address", ""),
                    "district": data.get("district", ""),
                    "neighborhood": data.get("neighborhood", ""),
                    "city": data.get("city", ""),
                    "province": data.get("province", ""),
                    "postal_code": data.get("postalCode", "")
                },
                "features": {
                    "size": data.get("size", 0.0),
                    "rooms": data.get("rooms", 0),
                    "bathrooms": data.get("bathrooms", 0),
                    "has_elevator": data.get("hasElevator", None),
                    "has_parking": data.get("hasParking", None),
                    "has_terrace": data.get("hasTerrace", None),
                    "has_garden": data.get("hasGarden", None),
                    "has_pool": data.get("hasPool", None),
                    "floor": data.get("floor", None),
                    "is_exterior": data.get("isExterior", None),
                    "energy_certificate": data.get("energyCertificate", None),
                    "condition": data.get("condition", None),
                    "construction_year": data.get("constructionYear", None)
                },
                "price": {
                    "price": data.get("price", 0.0),
                    "price_per_sqm": data.get("pricePerSquareMeter", 0.0),
                    "currency": data.get("currency", "EUR"),
                    "original_price": data.get("originalPrice", None),
                    "price_change_date": data.get("priceChangeDate", None),
                    "price_change_percentage": data.get("priceChangePercentage", None)
                },
                "images": data.get("images", []),
                "published_date": data.get("publishedDate", datetime.now().isoformat()),
                "updated_date": data.get("updatedDate", datetime.now().isoformat()),
                "contact_phone": data.get("contactPhone", None),
                "contact_name": data.get("contactName", None),
                "agency_id": data.get("agencyId", None),
                "agency_name": data.get("agencyName", None)
            }
            
            return PropertyListing(**transformed_data)
            
        except Exception as e:
            logger.error(f"Error parsing property data: {e}")
            logger.error(f"Raw data: {json.dumps(data, indent=2)}")
            raise
