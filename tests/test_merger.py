"""
Unit tests for the Product Merger.

Tests the core functionality of merging and enriching automotive product data:
- Loading and validating product catalog (product_catalog.csv)
- Loading vehicle fitments (vehicle_fitments.xlsx)
- Processing brand mappings (brand_mappings.csv)
- Generating enriched catalog (enriched_catalog.csv)
"""
import unittest
import pandas as pd
import os
from product_merger.merger import ProductMerger

class TestProductMerger(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.merger = ProductMerger()
        
        # Create test data directory if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")
            
    def test_normalize_merge_keys(self):
        """Test key normalization."""
        df1 = pd.DataFrame({"PartNumber": ["ABC123 ", " def456"]})
        df2 = pd.DataFrame({0: [" ABC123", "DEF456 "]})
        
        df1_norm, df2_norm = self.merger.normalize_merge_keys(df1, df2)
        
        self.assertEqual(df1_norm["PartNumber"].tolist(), ["ABC123", "DEF456"])
        self.assertEqual(df2_norm[0].tolist(), ["ABC123", "DEF456"])
        
    def test_process_titles(self):
        """Test title processing."""
        df = pd.DataFrame({
            "Title": [
                'Test Product"',
                'Another Product For',
                'Third Product'
            ]
        })
        
        processed = self.merger.process_titles(df)
        
        self.assertEqual(processed["Title"].tolist(), [
            'Test Product For',
            'Another Product For',
            'Third Product For'
        ])
        
    def test_process_descriptions(self):
        """Test description processing."""
        df = pd.DataFrame({
            "Merged Description": [
                "Some vehicle info",
                "VEHICLE FIT: existing info",
                None
            ]
        })
        
        processed = self.merger.process_descriptions(df)
        
        self.assertEqual(processed["Merged Description"].tolist(), [
            "VEHICLE FIT: Some vehicle info",
            "VEHICLE FIT: existing info",
            None
        ])
        
    def test_normalize_model_year_blocks(self):
        """Test year block normalization with valid and invalid years."""
        df = pd.DataFrame({
            "Merged Description": [
                # Valid year ranges and single years
                "VEHICLE FIT: Model A (95-00) Basic, Model B (05-10) Premium",
                "VEHICLE FIT: Model C (2015-2020) Standard",
                "(13) SUB XV Crosstrek, (95-00) Legacy",
                
                # Invalid years (outside 1955-2025)
                "(1900) Invalid Year Model",
                "(2030) Future Model",
                "(1950-1960) Partial Valid Range",
                "(45) Old Model",  # Would convert to 2045, invalid
                
                # Mix of valid and invalid
                "(2020) Valid Model, (2030) Invalid Model",
                "(13) Valid Crosstrek, (45) Invalid Model"
            ]
        })
        
        processed = self.merger.normalize_model_year_blocks(df)
        
        # Test valid year ranges
        self.assertTrue("1995-2000" in processed["Merged Description"].iloc[0])
        self.assertTrue("2005-2010" in processed["Merged Description"].iloc[0])
        self.assertTrue("2015-2020" in processed["Merged Description"].iloc[1])
        
        # Test valid single years
        single_year_result = processed["Merged Description"].iloc[2]
        self.assertTrue("SUB XV Crosstrek (2013)" in single_year_result)
        self.assertTrue("Legacy (1995-2000)" in single_year_result)
        
        # Test invalid years are removed
        self.assertEqual(processed["Merged Description"].iloc[3], "VEHICLE FIT: No valid year range")
        self.assertEqual(processed["Merged Description"].iloc[4], "VEHICLE FIT: No valid year range")
        
        # Test partial valid ranges are removed
        self.assertEqual(processed["Merged Description"].iloc[5], "VEHICLE FIT: No valid year range")
        self.assertEqual(processed["Merged Description"].iloc[6], "VEHICLE FIT: No valid year range")
        
        # Test mixed valid/invalid
        self.assertTrue("Valid Model (2020)" in processed["Merged Description"].iloc[7])
        self.assertFalse("2030" in processed["Merged Description"].iloc[7])
        
        self.assertTrue("Crosstrek (2013)" in processed["Merged Description"].iloc[8])
        self.assertFalse("45" in processed["Merged Description"].iloc[8])

if __name__ == '__main__':
    unittest.main() 