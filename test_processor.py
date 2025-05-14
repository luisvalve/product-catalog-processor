"""
Basic tests for the Product Processor
"""
import unittest
import pandas as pd
from main import ProductProcessor
import os
from pathlib import Path

class TestProductProcessor(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.processor = ProductProcessor()
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
    def tearDown(self):
        """Clean up test files"""
        test_input = self.data_dir / "input.csv"
        test_output = self.data_dir / "output.csv"
        if test_input.exists():
            test_input.unlink()
        if test_output.exists():
            test_output.unlink()
    
    def test_process_bullets(self):
        """Test bullet point processing"""
        # Test normal case
        bullets = "First Point | Second Point | Third Point"
        result = self.processor.process_bullets(bullets)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "First Point")
        
        # Test empty string
        self.assertEqual(len(self.processor.process_bullets("")), 0)
        
        # Test None value
        self.assertEqual(len(self.processor.process_bullets(None)), 0)
        
        # Test whitespace string
        self.assertEqual(len(self.processor.process_bullets("   ")), 0)

    def test_clean_alphanumeric_codes(self):
        """Test cleaning of alphanumeric codes in parentheses"""
        # Test basic case
        self.assertEqual(
            self.processor.clean_alphanumeric_codes("Engine Part (VQ35DE) Premium"),
            "Engine Part Premium"
        )
        
        # Test multiple codes
        self.assertEqual(
            self.processor.clean_alphanumeric_codes("Part (ABC123) Type (XY999) Quality"),
            "Part Type Quality"
        )
        
        # Test with no codes
        self.assertEqual(
            self.processor.clean_alphanumeric_codes("Normal Text"),
            "Normal Text"
        )
        
        # Test with empty parentheses
        self.assertEqual(
            self.processor.clean_alphanumeric_codes("Text () Here"),
            "Text () Here"
        )
        
        # Test with non-alphanumeric in parentheses
        self.assertEqual(
            self.processor.clean_alphanumeric_codes("Text (!) Here"),
            "Text (!) Here"
        )
    
    def test_process_data(self):
        """Test data processing with a small sample"""
        # Create test data
        test_data = {
            'PartNumber': ['TEST123'],
            'Title': [' Test Product (ABC123) '],  # Extra spaces and code to test cleaning
            'Bullets': ['Point 1 (XY789) | Point 2 | Point 3']
        }
        
        # Create temporary test file
        df = pd.DataFrame(test_data)
        df.to_csv(self.data_dir / "input.csv", index=False)
        
        # Process the data
        result = self.processor.process_data()
        
        # Verify results
        self.assertEqual(len(result), 1)
        self.assertEqual(result['Title'].iloc[0], 'Test Product')  # Should be cleaned
        self.assertEqual(result['bullet01'].iloc[0], 'Point 1')  # Code should be removed
        self.assertEqual(result['bullet02'].iloc[0], 'Point 2')
        self.assertEqual(result['bullet03'].iloc[0], 'Point 3')
        self.assertEqual(result['bullet04'].iloc[0], '')  # Empty for missing bullets
        self.assertEqual(result['bullet05'].iloc[0], '')

if __name__ == '__main__':
    unittest.main() 