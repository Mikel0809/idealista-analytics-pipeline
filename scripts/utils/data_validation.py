"""
Data validation utilities for the idealista-analytics-pipeline.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from pydantic import ValidationError

from scripts.api_client.models import PropertyListing, SearchResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_property_data(properties: List[PropertyListing]) -> Tuple[List[PropertyListing], List[Dict]]:
    """
    Validate a list of property listings and separate valid from invalid entries.
    
    Args:
        properties: List of PropertyListing objects to validate
        
    Returns:
        Tuple containing (valid_properties, invalid_properties)
    """
    valid_properties = []
    invalid_properties = []
    
    for prop in properties:
        # Basic validation checks
        if not prop.id or not prop.location or not prop.price:
            invalid_properties.append({
                "data": prop.dict(),
                "error": "Missing required fields (id, location, or price)"
            })
            continue
            
        # Price validation
        if prop.price.price <= 0 or prop.price.price_per_sqm <= 0:
            invalid_properties.append({
                "data": prop.dict(),
                "error": "Invalid price values"
            })
            continue
            
        # Size validation
        if prop.features.size <= 0:
            invalid_properties.append({
                "data": prop.dict(),
                "error": "Invalid size value"
            })
            continue
            
        # Location validation (basic check for Spain)
        if not prop.location.country.lower() in ["españa", "spain", "espana"]:
            invalid_properties.append({
                "data": prop.dict(),
                "error": "Property not in Spain"
            })
            continue
            
        # Date validation
        try:
            if isinstance(prop.published_date, str):
                datetime.fromisoformat(prop.published_date.replace('Z', '+00:00'))
            if isinstance(prop.updated_date, str):
                datetime.fromisoformat(prop.updated_date.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            invalid_properties.append({
                "data": prop.dict(),
                "error": "Invalid date format"
            })
            continue
            
        # If all checks pass, add to valid properties
        valid_properties.append(prop)
    
    logger.info(f"Validated {len(properties)} properties: {len(valid_properties)} valid, {len(invalid_properties)} invalid")
    return valid_properties, invalid_properties


def detect_outliers(df: pd.DataFrame, column: str, method: str = "iqr", threshold: float = 1.5) -> pd.DataFrame:
    """
    Detect outliers in a DataFrame column.
    
    Args:
        df: Pandas DataFrame
        column: Column name to check for outliers
        method: Method to use for outlier detection ('iqr' or 'zscore')
        threshold: Threshold for outlier detection
        
    Returns:
        DataFrame with outliers flagged in a new column 'is_outlier_{column}'
    """
    result_df = df.copy()
    outlier_col = f"is_outlier_{column}"
    
    if method == "iqr":
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        result_df[outlier_col] = ((df[column] < lower_bound) | (df[column] > upper_bound))
        
    elif method == "zscore":
        from scipy import stats
        z_scores = stats.zscore(df[column])
        result_df[outlier_col] = abs(z_scores) > threshold
        
    else:
        raise ValueError(f"Unknown outlier detection method: {method}")
    
    logger.info(f"Detected {result_df[outlier_col].sum()} outliers in column {column} using {method} method")
    return result_df


def validate_dataset_completeness(df: pd.DataFrame, required_columns: List[str], 
                                 min_non_null_percentage: float = 0.9) -> Dict[str, Dict[str, Union[bool, float]]]:
    """
    Validate the completeness of a dataset.
    
    Args:
        df: Pandas DataFrame to validate
        required_columns: List of columns that must be present
        min_non_null_percentage: Minimum percentage of non-null values required
        
    Returns:
        Dictionary with validation results
    """
    results = {
        "missing_columns": [],
        "incomplete_columns": {},
        "overall_valid": True
    }
    
    # Check for missing columns
    for col in required_columns:
        if col not in df.columns:
            results["missing_columns"].append(col)
            results["overall_valid"] = False
    
    # Check for null values in each column
    for col in df.columns:
        non_null_percentage = df[col].notnull().mean()
        if non_null_percentage < min_non_null_percentage:
            results["incomplete_columns"][col] = non_null_percentage
            results["overall_valid"] = False
    
    # Log results
    if not results["overall_valid"]:
        if results["missing_columns"]:
            logger.warning(f"Missing required columns: {results['missing_columns']}")
        if results["incomplete_columns"]:
            logger.warning(f"Columns with too many null values: {results['incomplete_columns']}")
    else:
        logger.info("Dataset completeness validation passed")
    
    return results


def convert_properties_to_dataframe(properties: List[PropertyListing]) -> pd.DataFrame:
    """
    Convert a list of PropertyListing objects to a pandas DataFrame.
    
    Args:
        properties: List of PropertyListing objects
        
    Returns:
        Pandas DataFrame with flattened property data
    """
    # Convert each property to a dictionary and flatten nested structures
    flattened_data = []
    
    for prop in properties:
        prop_dict = prop.dict()
        flat_dict = {}
        
        # Flatten location data
        for key, value in prop_dict["location"].items():
            flat_dict[f"location_{key}"] = value
            
        # Flatten features data
        for key, value in prop_dict["features"].items():
            flat_dict[f"features_{key}"] = value
            
        # Flatten price data
        for key, value in prop_dict["price"].items():
            flat_dict[f"price_{key}"] = value
            
        # Add all other top-level fields
        for key, value in prop_dict.items():
            if key not in ["location", "features", "price"]:
                flat_dict[key] = value
                
        flattened_data.append(flat_dict)
    
    # Create DataFrame
    df = pd.DataFrame(flattened_data)
    
    logger.info(f"Converted {len(properties)} properties to DataFrame with {len(df.columns)} columns")
    return df
