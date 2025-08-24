"""
Custom Airflow operator for Idealista API interactions.
"""
import json
import os
from typing import Dict, List, Optional

import pandas as pd
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

from scripts.api_client.api import IdealistaAPIClient
from scripts.utils.data_validation import (convert_properties_to_dataframe,
                                          validate_property_data)


class IdealistaAPIOperator(BaseOperator):
    """
    Airflow operator for extracting data from Idealista API.
    
    This operator handles authentication, data extraction, validation,
    and saving the results to a specified location.
    """
    
    @apply_defaults
    def __init__(
        self,
        operation: str,
        property_type: str,
        location: str,
        output_path: str,
        max_pages: Optional[int] = 10,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        validate_data: bool = True,
        *args, **kwargs
    ):
        """
        Initialize the IdealistaAPIOperator.
        
        Args:
            operation: Type of operation (sale, rent)
            property_type: Type of property (homes, offices, etc.)
            location: Location to search in (city, district, etc.)
            output_path: Path to save the extracted data
            max_pages: Maximum number of pages to retrieve
            api_key: Idealista API key (defaults to env var)
            api_secret: Idealista secret (defaults to env var)
            validate_data: Whether to validate the extracted data
            *args, **kwargs: Additional arguments for BaseOperator
        """
        super().__init__(*args, **kwargs)
        self.operation = operation
        self.property_type = property_type
        self.location = location
        self.output_path = output_path
        self.max_pages = max_pages
        self.api_key = api_key
        self.api_secret = api_secret
        self.validate_data = validate_data
        
    def execute(self, context):
        """
        Execute the operator.
        
        Args:
            context: Airflow context
            
        Returns:
            Path to the saved data file
        """
        self.log.info(f"Extracting {self.property_type} properties for {self.operation} in {self.location}")
        
        # Initialize API client
        client = IdealistaAPIClient(api_key=self.api_key, secret=self.api_secret)
        
        # Extract data
        properties = client.search_properties(
            operation=self.operation,
            property_type=self.property_type,
            location=self.location,
            max_pages=self.max_pages
        )
        
        self.log.info(f"Extracted {len(properties)} properties")
        
        # Validate data if requested
        if self.validate_data:
            valid_properties, invalid_properties = validate_property_data(properties)
            self.log.info(f"Validation results: {len(valid_properties)} valid, {len(invalid_properties)} invalid")
            
            # Save invalid data for analysis
            if invalid_properties:
                invalid_file = f"{os.path.splitext(self.output_path)[0]}_invalid.json"
                with open(invalid_file, 'w') as f:
                    json.dump(invalid_properties, f, indent=2, default=str)
                self.log.info(f"Saved invalid data to {invalid_file}")
        else:
            valid_properties = properties
        
        # Convert to DataFrame
        df = convert_properties_to_dataframe(valid_properties)
        
        # Add metadata columns
        execution_date = context['execution_date']
        df['extraction_date'] = execution_date.isoformat()
        df['city'] = self.location
        df['property_type'] = self.property_type
        df['operation'] = self.operation
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # Save to CSV
        df.to_csv(self.output_path, index=False)
        self.log.info(f"Saved {len(df)} properties to {self.output_path}")
        
        return self.output_path
